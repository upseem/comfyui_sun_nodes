好的！以下是一个规范清晰的 `README.md` 使用指南文档，帮助你快速创建自定义 ComfyUI 节点文件，并使用 `_CLASS_MAPPINGS` 和 `_DISPLAY_NAME_MAPPINGS` 结构统一自动注册：

---

# ☀️ 如何创建自定义 ComfyUI 节点模块 (`nodes/`)

## 🧩 文件结构约定

每一个节点模块放在 `custom_nodes/comfyui_sun_nodes/nodes/` 目录下，每个 `.py` 文件建议只放一组相关节点。

## 📄 新建节点文件

例如，你想写一个名为 `mynode_node.py` 的节点：

```bash
touch custom_nodes/comfyui_sun_nodes/nodes/mynode_node.py
```

## ✨ 在 `mynode_node.py` 中写入如下格式：

```python
class MyNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "Hello"})
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "SunX🌞"

    def run(self, text):
        return (f"你输入的是: {text}",)

# 固定后缀写法（前缀随意）
mynode_CLASS_MAPPINGS = {
    "MyNode": MyNode,
}

mynode_DISPLAY_NAME_MAPPINGS = {
    "MyNode": "🌞 My Custom Node",
}
```

## 🧠 命名规范建议

| 内容           | 建议写法                                                         |
| ------------ | ------------------------------------------------------------ |
| 类名           | 使用大驼峰，例如 `MyNode`                                            |
| 内部节点名        | 不含空格、驼峰或下划线                                                  |
| 显示节点名        | 可加 Emoji，中文描述更友好                                             |
| MAPPINGS 变量名 | `xxx_CLASS_MAPPINGS` 和 `xxx_DISPLAY_NAME_MAPPINGS`，前缀随意，后缀固定 |

---

## 🧩 在 `__init__.py` 中自动导入所有节点

路径：`custom_nodes/comfyui_sun_nodes/__init__.py`

```python
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
```

---

## 🧪 示例效果

你创建的节点文件如下：

```bash
custom_nodes/
└── comfyui_sun_nodes/
    ├── __init__.py
    └── nodes/
        ├── mynode_node.py      ✅
        └── another_node.py     ✅
```

ComfyUI 启动后会自动加载并注册这些节点，不需手动添加字典。

---

## ✅ 最佳实践建议

* 一个文件写一组节点，便于维护
* 使用固定后缀 `_CLASS_MAPPINGS` 和 `_DISPLAY_NAME_MAPPINGS`，自动加载更稳
* 所有功能类建议加注释，便于他人理解和合作开发

---

如需我提供一个脚本自动生成这种节点模板（例如 `create_node.py mynode`），也可以帮你完成。
