import os
import subprocess
import requests
import json
from PIL import Image
import io
import torch
import numpy as np

class BookCoverFinder:
    CATEGORY = "books"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "query": ("STRING",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    def execute(self, query):

        search_url = f"https://openlibrary.org/search.json?q={query}"
        headers = {}

        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        size="M"
        if data and data['docs']:
            first_book = data['docs'][0]  # Get the first book from the results
            cover_id = None
            if 'cover_edition_key' in first_book:
                cover_id = first_book['cover_edition_key']  # Use cover_edition_key if available
                key_type = "olid"  # Key type for OLID
            elif 'cover_i' in first_book:
                cover_id = first_book['cover_i']  # Use cover_i if cover_edition_key is missing
                key_type = "id"  # Key type for cover ID
            if cover_id:
                cover_url = f"https://covers.openlibrary.org/b/{key_type}/{cover_id}-{size}.jpg" # Construct the cover URL
                print(f"Attempting to download cover from: {cover_url}")
                cover_response = requests.get(cover_url, stream=True, headers=headers) # Make the GET request, stream=True for large files
                cover_response.raise_for_status()
                image_bytes = io.BytesIO(cover_response.content)
                pil_image = Image.open(image_bytes).convert("RGB") # Convert to RGB if not already
                img_array = np.array(pil_image).astype(np.float32)
                img_array = img_array / 255.0
                image_tensor = torch.from_numpy(img_array)[None, ] # [1, H, W, C] format
                return (image_tensor,) # Return the tensor as a tuple
            else:
                print("No cover identifier found for the first book in the search results.")
        else:
            print("No books found for your query.")
        return (torch.zeros(2,2, 100, 100, 3))

