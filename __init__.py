import os
import importlib.util

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

nodes_dir = os.path.join(os.path.dirname(__file__), "nodes")

for filename in os.listdir(nodes_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        filepath = os.path.join(nodes_dir, filename)
        module_name = filename[:-3]  # 不要带你的包名

        # 动态加载模块（防止污染 __name__）
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 查找 *_CLASS_MAPPINGS
        for attr in dir(module):
            if attr.endswith("_CLASS_MAPPINGS"):
                NODE_CLASS_MAPPINGS.update(getattr(module, attr))
            elif attr.endswith("_DISPLAY_NAME_MAPPINGS"):
                NODE_DISPLAY_NAME_MAPPINGS.update(getattr(module, attr))

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
