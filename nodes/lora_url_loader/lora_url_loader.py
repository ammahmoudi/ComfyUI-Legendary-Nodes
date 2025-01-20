import os
from urllib.parse import urlparse, unquote
import comfy.sd
import comfy.utils
from ..base_downloader import BaseModelDownloader
from ..download_utils import DownloadManager
import folder_paths


class LoRADownloader(BaseModelDownloader):
    FUNCTION = "load_lora"
    RETURN_TYPES = ("MODEL", "CLIP")
    CATEGORY = "loaders"

    def __init__(self):
        # Base directory for LoRA files
        self.output_dir = os.path.join(folder_paths.models_dir, "loras", "api_loras")
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def INPUT_TYPES():
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "lora_link": ("STRING", {}),
                "strength_model": (
                    "FLOAT",
                    {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01},
                ),
                "strength_clip": (
                    "FLOAT",
                    {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01},
                ),
                "output": ("STRING", {}),
            }
        }

    def resolve_path(self, path: str) -> str:
        """Resolve relative paths to the ComfyUI models/loras/api_loras directory."""
        if not os.path.isabs(path):
            path = os.path.join(self.output_dir, path)
        return os.path.abspath(path)

    def load_lora(self, model, clip, lora_link, strength_model, strength_clip, output):
        if strength_model == 0 and strength_clip == 0:
            return (model, clip)

        # Resolve the output path relative to the base directory
        output = self.resolve_path(output)

        # Download the LoRA file
        downloaded_lora_path = self.download_lora(lora_link, output)
        if not downloaded_lora_path:
            raise RuntimeError("Error downloading LoRA file. Workflow halted.")

        try:
            # Load the LoRA content
            lora_content = comfy.utils.load_torch_file(
                downloaded_lora_path, safe_load=True
            )
            model_lora, clip_lora = comfy.sd.load_lora_for_models(
                model, clip, lora_content, strength_model, strength_clip
            )
            return (model_lora, clip_lora)
        except Exception as e:
            raise RuntimeError(f"Error loading LoRA: {e}")

    def download_lora(self, link, output):
        try:
            # Parse the URL and sanitize the filename
            parsed_url = urlparse(link)
            filename = os.path.basename(parsed_url.path)
            filename = unquote(filename)

            # Strip any query parameters from the filename
            if '?' in filename:
                filename = filename.split('?')[0]

            # Prepare the output directory and file path
            save_path = self.prepare_download_path(output, "")
            full_path = os.path.join(save_path, filename)

            # Check if the file already exists
            if os.path.exists(full_path):
                print(f"File already exists: {full_path}. Using the existing file.")
                return full_path

            # Start downloading using DownloadManager
            print(f"Downloading file to: {full_path}")
            downloaded_file = DownloadManager.download_with_progress(
                url=link,
                save_path=save_path,
                progress_callback=self,
                params=None,
                chunk_size=1024 * 1024
            )

            # Verify the downloaded file is not empty
            if downloaded_file and os.path.getsize(downloaded_file) == 0:
                print("Downloaded file is empty. Deleting...")
                os.remove(downloaded_file)
                return None

            return downloaded_file
        except Exception as e:
            print(f"Error downloading LoRA file: {e}")
            return None
