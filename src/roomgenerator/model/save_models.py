import torch
from transformers import DPTImageProcessor, DPTForDepthEstimation
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, AutoencoderKL

# Download and save the models
depth_estimator = DPTForDepthEstimation.from_pretrained("Intel/dpt-hybrid-midas")
depth_estimator.save_pretrained("dpt-hybrid-midas/")

image_processor = DPTImageProcessor.from_pretrained("Intel/dpt-hybrid-midas")
image_processor.save_pretrained("dpt-hybrid-midas/")

controlnet = ControlNetModel.from_pretrained("diffusers/controlnet-depth-sdxl-1.0")
controlnet.save_pretrained(
    "controlnet-depth-sdxl-1.0/",
    variant="fp16",
    use_safetensors=True,
    torch_dtype=torch.float16
)

vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
vae.save_pretrained("sdxl-vae-fp16-fix/")

sdxl = StableDiffusionXLControlNetPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        controlnet=controlnet,
        vae=vae,
        variant="fp16",
        use_safetensors=True,
        torch_dtype=torch.float16,
)
sdxl.save_pretrained("stable-diffusion-xl-base-1.0")