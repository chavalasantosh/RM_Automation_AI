import torch
from diffusers import DiffusionPipeline, UniPCMultistepScheduler

# Model ID and generation parameters
model_id = "black-forest-labs/FLUX.1-schnell"
prompt = "A cat holding a sign that says hello world"
image_width = 768
image_height = 1360
inference_steps = 4

# Hardware configuration
device = "cpu"
torch_dtype = torch.float32  # Recommended dtype for CPU only

print(f"Loading model '{model_id}' to {device} with {torch_dtype} precision...")

# Load the diffusion pipeline with CPU-optimized settings
pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch_dtype)
pipe = pipe.to(device)

# --- Apply CPU-specific and model-specific optimizations ---

# Optimize scheduler for faster inference
# UniPCMultistepScheduler is one of the fastest schedulers and suitable for CPU
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
print("Enabled UniPCMultistepScheduler for faster inference.")

# Enable attention slicing for memory optimization on CPU, especially for larger images
# This reduces memory footprint by processing attention computations in slices
pipe.enable_attention_slicing()
print("Enabled attention slicing for CPU memory optimization.")

# Compile the UNet model for potential performance improvements with PyTorch 2.0+
# This can provide 5-50% speedup by optimizing graph execution
pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
print("Compiled UNet with torch.compile for performance.")

# --- Generate image ---
print("Generating image...")
# For FLUX models, guidance_scale parameter is not needed and should be omitted.
image = pipe(
    prompt=prompt,
    width=image_width,
    height=image_height,
    num_inference_steps=inference_steps,
).images[0]

print("Image generation complete.")
image.save("optimized_flux_cpu_image.png")
print("Image saved as 'optimized_flux_cpu_image.png'")