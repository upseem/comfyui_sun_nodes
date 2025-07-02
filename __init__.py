import os
import importlib

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

nodes_path = os.path.join(os.path.dirname(__file__), "nodes")

for filename in os.listdir(nodes_path):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"{__name__}.nodes.{filename[:-3]}"
        module = importlib.import_module(module_name)

        for attr in dir(module):
            if attr.endswith("_CLASS_MAPPINGS"):
                NODE_CLASS_MAPPINGS.update(getattr(module, attr))
            elif attr.endswith("_DISPLAY_NAME_MAPPINGS"):
                NODE_DISPLAY_NAME_MAPPINGS.update(getattr(module, attr))

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
