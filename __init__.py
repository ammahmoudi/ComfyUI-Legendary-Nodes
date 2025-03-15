
import os

from .nodes.image_url_loader.image_url_loader import ImageUrlLoader



from .nodes.dataset_loader.dataset_loader import CustomNodeSaveImagesWithPrompts

from .nodes.lora_url_loader.lora_url_loader import LoRADownloader



# Node mappings
NODE_CLASS_MAPPINGS = { 
    "Legendary Lora URL Loader": LoRADownloader,
    "Legendary Dataset Saver": CustomNodeSaveImagesWithPrompts,
    "Legendary Image URL Loader": ImageUrlLoader

}

# Display names
NODE_DISPLAY_NAME_MAPPINGS = { 
    "Legendary Lora URL Loader": "Legendary Lora URL Loader",
    "Legendary Dataset Saver":"Legendary Dataset Saver",
    "Legendary Image URL Loader": "Legendary Image URL Loader"

}

# Web directory for JavaScript files
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY"
]