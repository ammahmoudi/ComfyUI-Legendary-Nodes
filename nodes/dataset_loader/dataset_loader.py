import os
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import json
import folder_paths

class CustomNodeSaveImagesWithPrompts:
    def __init__(self) -> None:
        self.output_dir = os.path.join(folder_paths.models_dir, "loras", "api_loras")
        os.makedirs(self.output_dir, exist_ok=True)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_data": ("STRING", {"default": "", "multiline": True}),
                "folder_name": ("STRING", {"default": "output_folder", "multiline": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "process_json"
    OUTPUT_NODE = True

    CATEGORY = "Custom Nodes"

    def process_json(self, json_data: str, folder_name: str):
        try:
            # Parse the input JSON string
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return ("Error: Invalid JSON data",)

        base_folder = os.path.join(self.output_dir, folder_name)
        os.makedirs(base_folder, exist_ok=True)

        for idx, content in data.items():
            image_url = content.get("image_url")
            prompt = content.get("prompt")

            # Validate required fields
            if not image_url or not prompt:
                print(f"Skipping entry {idx}: Missing 'image_url' or 'prompt'")
                continue

            try:
                # Download the image
                response = requests.get(image_url, stream=True)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))

                # Determine the file format from the image (e.g., JPEG, PNG)
                image_format = image.format if image.format else "JPEG"
                filename = f"{idx}"
                image_path = os.path.join(base_folder, f"{filename}.{image_format.lower()}")
                prompt_path = os.path.join(base_folder, f"{filename}.txt")

                # Save the image
                image.save(image_path, format=image_format)

                # Save the prompt to a text file
                with open(prompt_path, "w") as f:
                    f.write(prompt)

                print(f"Saved: {image_path} and {prompt_path}")

            except requests.exceptions.RequestException as e:
                print(f"Error downloading image for entry {idx}: {e}")
            except UnidentifiedImageError as e:
                print(f"Error identifying image for entry {idx}: {e}")
            except Exception as e:
                print(f"Unexpected error for entry {idx}: {e}")

        # Return the folder path as a single string in a tuple
        return (base_folder,)

