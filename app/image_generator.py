from diffusers import StableDiffusionPipeline
import torch

def generate_image(prompt: str, output_path: str):
    # Load the Stable Diffusion model
    model_id = "CompVis/stable-diffusion-v1-4"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")

    # Generate an image
    image = pipe(prompt).images[0]

    # Save the image
    image.save(output_path) 