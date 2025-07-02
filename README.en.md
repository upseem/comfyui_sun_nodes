🌐 [English](./README.en.md) | [中文说明](./README.md)
# ☀️ comfyui_sun_nodes

A custom node plugin for [ComfyUI](https://github.com/comfyanonymous/ComfyUI), developed by [**SunX AI**](https://github.com/upseem).

Currently supported: **Batch Image Looping**

---

## 🧠 Features

### ✅ Batch Image Loop: `Batch Image Loop Open SunxAI` & `Close`

This node pair is designed to **process a batch of images one by one**, passing them into the ComfyUI graph sequentially, ensuring full processing of each image before the next iteration.

**Included nodes:**

- `Batch Image Loop Open SunxAI`: Feeds each image from the batch into the workflow
- `Batch Image Loop Close SunxAI`: Collects and assembles processed images

📌 **Highlights:**

- 🖼 **One at a time**: Each image is fully processed before the next one is started
- 🧵 **Synchronous execution**: Prevents overlapping or early execution; suitable for accurate frame-by-frame tasks

Use cases:
- Video frame-by-frame processing
- Sequential style transfer
- Animation workflows, etc.

---

## 📦 Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/upseem/comfyui_sun_nodes.git
