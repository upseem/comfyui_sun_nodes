import os
import uuid
from PIL import Image
import numpy as np

from comfy_execution.graph_utils import GraphBuilder, is_link
import folder_paths

from ..tools.tools import VariantSupport
import torch.nn.functional as F
import torch
from nodes import NODE_CLASS_MAPPINGS as ALL_NODE_CLASS_MAPPINGS


@VariantSupport()
class BatchImageLoopOpenSun:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "segmented_images": ("IMAGE", {"forceInput": True}),
                "output_dir": ("STRING", {"default": ""}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "iteration_count": ("INT", {"default": 0}),
                "previous_image": ("IMAGE",),
                "batch_id": ("STRING",),
            }
        }
        return inputs

    RETURN_TYPES = ("FLOW_CONTROL", "IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("FLOW_CONTROL", "current_image", "max_iterations", "iteration_count", "batch_path")
    FUNCTION = "while_loop_open"
    CATEGORY = "CyberEveLoop🐰·Chen定制"

    def standardize_images(self, images):
        if isinstance(images, list):
            images = torch.cat(images, dim=0)
        if len(images.shape) == 3:
            images = images.unsqueeze(0)
        assert len(images.shape) == 4, f"Images must be 4D [B,H,W,C], got {images.shape}"
        return images

    def resize_to_match(self, image, target_shape):
        if image.shape[1:3] != target_shape[1:3]:
            if len(image.shape) == 3:
                image = image.unsqueeze(0)
            image = image.permute(0, 3, 1, 2)
            image = F.interpolate(image, size=(target_shape[1], target_shape[2]), mode='bilinear', align_corners=False)
            image = image.permute(0, 2, 3, 1)
        return image

    def while_loop_open(self, segmented_images, output_dir="", unique_id=None, iteration_count=0, previous_image=None, batch_id=None):
        print(f"[chen] Loop iteration: {iteration_count}")

        images = self.standardize_images(segmented_images)
        max_iterations = images.shape[0]

        if batch_id is None:
            batch_id = uuid.uuid4().hex[:8]

        base_output = folder_paths.get_output_directory()
        if output_dir:
            batch_path = os.path.join(base_output, output_dir, batch_id)
        else:
            batch_path = os.path.join(base_output, "loop_batch", batch_id)

        if iteration_count == 0:
            os.makedirs(batch_path, exist_ok=True)
            print(f"[chen] Created batch directory: {batch_path}")

        if iteration_count >= max_iterations:
            raise ValueError(f"[chen] Iteration {iteration_count} exceeds max {max_iterations}")

        if previous_image is not None and iteration_count > 0:
            previous_image = self.resize_to_match(previous_image, images.shape)
            idx = min(iteration_count, max_iterations - 1)
            images[idx:idx+1] = previous_image

        current_image = images[iteration_count:iteration_count+1]
        return ("stub", current_image, max_iterations, iteration_count, batch_path)


@VariantSupport()
class BatchImageLoopCloseSun:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "flow_control": ("FLOW_CONTROL", {"rawLink": True}),
                "current_image": ("IMAGE",),
                "max_iterations": ("INT", {"forceInput": True}),
                "iteration_count": ("INT", {"forceInput": True}),
                "batch_path": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "pass_back": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "dynprompt": "DYNPROMPT",
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("result_images", "output_path")
    FUNCTION = "while_loop_close"
    CATEGORY = "CyberEveLoop🐰·Chen定制"

    def standardize_image(self, image):
        if len(image.shape) == 3:
            image = image.unsqueeze(0)
        assert len(image.shape) == 4, f"Image must be 4D [B,H,W,C], got {image.shape}"
        return image

    def save_image(self, image, batch_path, index):
        filepath = os.path.join(batch_path, f"{index:05d}.png")
        if os.path.exists(filepath):
            print(f"[chen] Skip (exists): {filepath}")
            return
        img_np = (image.squeeze(0).cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        img_pil = Image.fromarray(img_np)
        img_pil.save(filepath)
        print(f"[chen] Saved: {filepath}")

    def load_all_images(self, batch_path, max_iterations, device):
        results = []
        for i in range(max_iterations):
            filepath = os.path.join(batch_path, f"{i:05d}.png")
            img_pil = Image.open(filepath).convert("RGB")
            img_np = np.array(img_pil).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_np).unsqueeze(0)
            results.append(img_tensor)
        return torch.cat(results, dim=0).to(device)

    def while_loop_close(self, flow_control, current_image, max_iterations, batch_path,
                         iteration_count, pass_back=False,
                         dynprompt=None, unique_id=None):
        print(f"[chen] Iteration {iteration_count} / {max_iterations}")

        current_image = self.standardize_image(current_image)
        device = current_image.device

        if iteration_count >= max_iterations:
            raise ValueError(f"[chen] Iteration {iteration_count} exceeds max {max_iterations}")

        self.save_image(current_image, batch_path, iteration_count)

        if iteration_count == max_iterations - 1:
            print(f"[chen] Loop finished, loading results from {batch_path}")
            result_images = self.load_all_images(batch_path, max_iterations, device)
            return (result_images, batch_path)

        open_node = flow_control[0]

        upstream = {}
        parent_ids = []
        self.explore_dependencies(unique_id, dynprompt, upstream, parent_ids)

        prompts = dynprompt.get_original_prompt()
        output_nodes = {}
        for id, node in prompts.items():
            if "inputs" not in node:
                continue
            class_type = node.get("class_type")
            if class_type in ALL_NODE_CLASS_MAPPINGS:
                class_def = ALL_NODE_CLASS_MAPPINGS[class_type]
                if getattr(class_def, 'OUTPUT_NODE', False):
                    for k, v in node['inputs'].items():
                        if is_link(v):
                            output_nodes[id] = v

        graph = GraphBuilder()
        self.explore_output_nodes(dynprompt, upstream, output_nodes, parent_ids)

        contained = {}
        self.collect_contained(open_node, upstream, contained)
        contained[unique_id] = True
        contained[open_node] = True

        for node_id in contained:
            node_info = dynprompt.get_node(node_id)
            node = graph.node(node_info["class_type"], "Recurse" if node_id == unique_id else node_id)
            node.set_override_display_id(node_id)

        for node_id in contained:
            node_info = dynprompt.get_node(node_id)
            node = graph.lookup_node("Recurse" if node_id == unique_id else node_id)
            for k, v in node_info["inputs"].items():
                if is_link(v) and v[0] in contained:
                    parent = graph.lookup_node(v[0])
                    node.set_input(k, parent.out(v[1]))
                else:
                    node.set_input(k, v)

        my_clone = graph.lookup_node("Recurse")
        my_clone.set_input("iteration_count", iteration_count + 1)

        new_open = graph.lookup_node(open_node)
        new_open.set_input("iteration_count", iteration_count + 1)
        new_open.set_input("batch_id", os.path.basename(batch_path))
        if pass_back:
            new_open.set_input("previous_image", current_image)

        return {
            "result": (my_clone.out(0), my_clone.out(1)),
            "expand": graph.finalize()
        }

    def explore_dependencies(self, node_id, dynprompt, upstream, parent_ids):
        node_info = dynprompt.get_node(node_id)
        if "inputs" not in node_info:
            return
        for _, v in node_info["inputs"].items():
            if is_link(v):
                parent_id = v[0]
                display_id = dynprompt.get_display_node_id(parent_id)
                if display_id != node_id:
                    parent_ids.append(display_id)
                if parent_id not in upstream:
                    upstream[parent_id] = []
                    self.explore_dependencies(parent_id, dynprompt, upstream, parent_ids)
                upstream[parent_id].append(node_id)

    def explore_output_nodes(self, dynprompt, upstream, output_nodes, parent_ids):
        for parent_id in upstream:
            display_id = dynprompt.get_display_node_id(parent_id)
            for output_id in output_nodes:
                id = output_nodes[output_id][0]
                if id in parent_ids and display_id == id and output_id not in upstream[parent_id]:
                    if '.' in parent_id:
                        arr = parent_id.split('.')
                        arr[-1] = output_id
                        upstream[parent_id].append('.'.join(arr))
                    else:
                        upstream[parent_id].append(output_id)

    def collect_contained(self, node_id, upstream, contained):
        if node_id not in upstream:
            return
        for child_id in upstream[node_id]:
            if child_id not in contained:
                contained[child_id] = True
                self.collect_contained(child_id, upstream, contained)
