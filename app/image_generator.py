import requests
import os
import time
from PIL import Image
import io
import logging

def generate_image(prompt: str, scholarship_id: int) -> str:
    """Generate image and return the URL path"""
    # Create images directory if it doesn't exist
    images_dir = "static/images"
    os.makedirs(images_dir, exist_ok=True)
    
    # Define the image path and URL
    filename = f"scholarship_{scholarship_id}.png"
    output_path = os.path.join(images_dir, filename)
    url_path = f"/static/images/{filename}"
    
    api_token = os.getenv("HF_API_TOKEN")
    if not api_token:
        raise Exception("HF_API_TOKEN environment variable is not set")
    
    API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=30
        )
        
        logging.info(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            image.save(output_path)
            return url_path
        elif response.status_code == 429:
            raise Exception("Max requests total reached")
        else:
            logging.error(f"API Error Response: {response.text}")
            raise Exception(f"Error generating image: {response.text}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        raise Exception(f"Request failed: {str(e)}") 