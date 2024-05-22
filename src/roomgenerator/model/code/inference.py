from io import BytesIO
import json
import base64
import torch
import numpy as np
from PIL import Image
from transformers import DPTImageProcessor, DPTForDepthEstimation
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, HeunDiscreteScheduler, AutoencoderKL
from compel import Compel, ReturnedEmbeddingsType
import boto3

s3_client = boto3.client('s3')

# Model initialization
def model_fn(model_dir):
    depth_estimator = DPTForDepthEstimation.from_pretrained(model_dir + "/dpt-hybrid-midas").to("cuda")
    feature_extractor = DPTImageProcessor.from_pretrained(model_dir + "/dpt-hybrid-midas")
    
    controlnet = ControlNetModel.from_pretrained(
        model_dir + "/controlnet-depth-sdxl-1.0",
        variant="fp16",
        use_safetensors=True,
        torch_dtype=torch.float16,
    ).to("cuda")
    
    vae = AutoencoderKL.from_pretrained(
        model_dir + "/sdxl-vae-fp16-fix", 
        torch_dtype=torch.float16
    ).to("cuda")
    
    pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
        model_dir + "/stable-diffusion-xl-base-1.0",
        controlnet=controlnet,
        vae=vae,
        variant="fp16",
        use_safetensors=True,
        torch_dtype=torch.float16,
    ).to("cuda")
    # print(pipe.scheduler.compatibles)
    pipe.scheduler = HeunDiscreteScheduler.from_config(pipe.scheduler.config)
    
    compel = Compel(
      tokenizer=[pipe.tokenizer, pipe.tokenizer_2] ,
      text_encoder=[pipe.text_encoder, pipe.text_encoder_2],
      returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,
      requires_pooled=[False, True]
    )

    return depth_estimator, feature_extractor, controlnet, vae, pipe, compel

def input_fn(request_body, request_content_type):    
    if request_content_type == 'application/json':
        # Parse the JSON input
        input_data = json.loads(request_body)        
        image = fetch_image(input_data)
        
        return image, input_data
        
    raise ValueError("Unsupported content type: {}".format(request_content_type))

# Predict the result using the model
def predict_fn(input_data, model):
    image, data = input_data
    depth_estimator, feature_extractor, controlnet, vae, pipe, compel = model
    prompt = data['prompt']
    conditioning, pooled = compel(prompt)
    depth_image = get_depth_map(image, feature_extractor, depth_estimator)
    generator = torch.manual_seed(33)
    
    # https://huggingface.co/docs/diffusers/en/api/pipelines/controlnet#diffusers.StableDiffusionControlNetImg2ImgPipeline.__call__
    generated_images = pipe(
        prompt_embeds=conditioning,
        pooled_prompt_embeds=pooled,
        negative_prompt=data['negative_prompt'],
        image=depth_image,
        num_inference_steps=data['steps'],
        strength=data['strength'],
        controlnet_conditioning_scale=data['controlnet_conditioning_scale'],
        generator=generator,
    ).images
    
    # create response 
    encoded_images=[]
    for image in generated_images:
      buffered = BytesIO()
      image.save(buffered, format="JPEG")
      encoded_images.append(base64.b64encode(buffered.getvalue()).decode())
    encoded_images.append(depth_image)

    # create response
    return {"generated_images": encoded_images}

def get_depth_map(image, feature_extractor, depth_estimator):
    rgb_image = image.convert("RGB")
    image = feature_extractor(images=rgb_image, return_tensors="pt").pixel_values.to("cuda")
    with torch.no_grad(), torch.autocast("cuda"):
        depth_map = depth_estimator(image).predicted_depth

    depth_map = torch.nn.functional.interpolate(
        depth_map.unsqueeze(1),
        size=(1024, 1024),
        mode="bicubic",
        align_corners=False,
    )
    depth_min = torch.amin(depth_map, dim=[1, 2, 3], keepdim=True)
    depth_max = torch.amax(depth_map, dim=[1, 2, 3], keepdim=True)
    depth_map = (depth_map - depth_min) / (depth_max - depth_min)
    image = torch.cat([depth_map] * 3, dim=1)

    image = image.permute(0, 2, 3, 1).cpu().numpy()[0]
    image = Image.fromarray((image * 255.0).clip(0, 255).astype(np.uint8))
    return image

def fetch_image(input_data: dict) -> Image:
    image_bytes = fetch_image_s3(input_data['init_image_s3']) if input_data.get('init_image_s3') else base64.b64decode(input_data['init_image'])
    image_stream = BytesIO(image_bytes)
    return Image.open(image_stream)

def fetch_image_s3(s3_object: dict) -> bytes:
    response = s3_client.get_object(Bucket=s3_object['Bucket'], Key=s3_object['Key'])
    return response["Body"].read()
    