from .nodes.loop_images import BatchImageLoopOpenSun, BatchImageLoopCloseSun

NODE_CLASS_MAPPINGS = {
    "SunxAI_BatchImageLoopOpenChen": BatchImageLoopOpenSun,
    "SunxAI_BatchImageLoopCloseChen": BatchImageLoopCloseSun,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SunxAI_BatchImageLoopOpenChen": "Batch Image Loop Open SunxAI",
    "SunxAI_BatchImageLoopCloseChen": "Batch Image Loop Close SunxAI",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
