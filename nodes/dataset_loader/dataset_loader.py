import os
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import json
import folder_paths


class CustomNodeSaveImagesWithPrompts:
    def __init__(self) -> None:
        self.models_dir = folder_paths.get_directory_by_type("models") or folder_paths.models_dir
        self.input_dir = folder_paths.get_directory_by_type("input") or folder_paths.input_directory
        self.temp_dir = folder_paths.get_directory_by_type("temp") or folder_paths.temp_directory
        self.output_dir = folder_paths.get_directory_by_type("output") or folder_paths.output_directory

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_data": ("STRING", {"default": "", "multiline": True}),
                "folder_name": ("STRING", {"default": "output_folder", "multiline": False}),
                "base_dir": ("STRING", {
                    "default": "output",  # Default to "output" directory
                    "choices": ["models", "input", "temp", "output"]
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "process_json"
    OUTPUT_NODE = True

    CATEGORY = "Custom Nodes"

    def process_json(self, json_data: str, folder_name: str, base_dir: str):
        try:
            # Parse the input JSON string
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return ("Error: Invalid JSON data",)

        # Determine the base directory
        base_directory_map = {
            "models": self.models_dir,
            "input": self.input_dir,
            "temp": self.temp_dir,
            "output": self.output_dir,
        }
        selected_base_dir = base_directory_map.get(base_dir, self.output_dir)

        # Append folder_name to the base directory
        base_folder = os.path.join(selected_base_dir, folder_name)
        os.makedirs(base_folder, exist_ok=True)

        for idx, content in data.items():
            image_url = content.get("image_url")
            prompt = content.get("prompt", "")

            # Validate required fields
            if not image_url:
                print(f"Skipping entry {idx}: Missing 'image_url'")
                continue

            try:
                # Download the image
                response = requests.get(image_url, stream=True)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))

                # Determine the file format from the image
                image_format = image.format if image.format else "JPEG"
                filename = f"{idx}"
                extension = image_format.lower()  # Ensure lowercase extensions
                if not extension.startswith("."):
                    extension = f".{extension}"
                image_path = os.path.join(base_folder, f"{filename}{extension}")
                prompt_path = os.path.join(base_folder, f"{filename}.txt")

                # Save the image
                image.save(image_path, format=image_format)

                # Save the prompt to a text file if not empty
                if prompt.strip():
                    with open(prompt_path, "w") as f:
                        f.write(prompt)

                print(f"Saved: {image_path} and {prompt_path if prompt.strip() else '(no prompt)'}")

            except requests.exceptions.RequestException as e:
                print(f"Error downloading image for entry {idx}: {e}")
            except UnidentifiedImageError as e:
                print(f"Error identifying image for entry {idx}: {e}")
            except Exception as e:
                print(f"Unexpected error for entry {idx}: {e}")

        # Return the folder path as a single string in a tuple
        return (base_folder,)
