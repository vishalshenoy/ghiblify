from typing import Any
import base64
from io import BytesIO
from typing import Dict
import torch
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline
from dataclasses import asdict


BASE64_PREAMBLE = "data:image/png;base64,"


def pil_to_b64(pil_img):
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return BASE64_PREAMBLE + str(img_str)[2:-1]


def b64_to_pil(b64_str):
    return Image.open(BytesIO(base64.b64decode(b64_str.replace(BASE64_PREAMBLE, ""))))


STABLE_DIFFUSION_MODEL_ID = "nitrosocke/Ghibli-Diffusion"


class Model:
    def __init__(self, **kwargs) -> None:
        self._model = None

    def load(self):
        print("startup")
        self._model = StableDiffusionImg2ImgPipeline.from_pretrained(
            STABLE_DIFFUSION_MODEL_ID,
            torch_dtype=torch.float16,
        )
        self._model = self._model.to("cuda")

    def preprocess(self, request: Dict) -> Dict:
        # Convert from base64
        print("to base64 before")
        if "image" in request:
            request["image"] = b64_to_pil(request["image"]).convert("RGB")
        return request

    def postprocess(self, request: Dict) -> Dict:
        # Convert to base64
        print("done!")
        request.images = [pil_to_b64(img) for img in request.images]
        return asdict(request)

    def predict(self, request: Dict):
        print("predicting!")
        generator = torch.Generator(device="cuda").manual_seed(512)
        response = self._model(**request, strength=0.8,
                               guidance_scale=12, generator=generator)
        return response
