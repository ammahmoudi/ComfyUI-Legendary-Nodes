import os
import torch
import numpy as np
from PIL import Image
from urllib.parse import urlparse, unquote
from ..download_utils import DownloadManager
from ..base_downloader import BaseModelDownloader
import folder_paths

class ImageUrlLoader(BaseModelDownloader):
    FUNCTION = "load_image"
    RETURN_TYPES = ("IMAGE", "MASK", "BOOLEAN")
    RETURN_NAMES = ("image", "mask", "has_image")
    CATEGORY = "loaders"

    def __init__(self):
        super().__init__()
        self.output_dir = folder_paths.get_temp_directory()

    @staticmethod
    def INPUT_TYPES():
        return {
            "required": {},
            "optional": {
                "url": ("STRING", {"default": "", "multiline": True}),
                "keep_alpha_channel": (
                    "BOOLEAN", {"default": False, "label_on": "enabled", "label_off": "disabled"}
                ),
            }
        }

    def load_image(self, url="", keep_alpha_channel=False):
        url = url.strip()
        if not url:
            return None, None, False

        try:
            downloaded_file_path = DownloadManager.download_with_progress(
                url=url,
                save_path=self.output_dir,
                progress_callback=self,
                params=None,
                chunk_size=1024 * 1024,
            )

            if not downloaded_file_path:
                return None, None, False

            image = Image.open(downloaded_file_path).convert("RGBA" if keep_alpha_channel else "RGB")
            mask = image.getchannel("A") if keep_alpha_channel else None

            image_tensor = torch.tensor(np.array(image) / 255.0, dtype=torch.float32).unsqueeze(0)

            if mask:
                mask_tensor = torch.tensor(np.array(mask) / 255.0, dtype=torch.float32).unsqueeze(0)
            else:
                mask_tensor = torch.zeros((1, image.height, image.width), dtype=torch.float32)

            return image_tensor, mask_tensor if mask else mask, True

        except Exception as e:
            print(f"Error downloading or processing image from {url}: {e}")
            return None, None, False
