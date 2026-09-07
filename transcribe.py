import os
import numpy as np
import torch
import folder_paths
import comfy.model_management as mm
from qwen_asr import Qwen3ASRModel
from .utils import load_audio_input, TRANSCRIBE_SUPPORTED_LANGUAGES


class PLQwen3ASRLoader:
    """加载 Qwen3-ASR 模型"""
    MODELS = {
        "Qwen3-ASR-1.7B": "Qwen/Qwen3-ASR-1.7B",
        "Qwen3-ASR-0.6B": "Qwen/Qwen3-ASR-0.6B",
    }
    PRECISIONS = ["bf16", "fp16", "fp32"]
    ATTENTIONS = ["auto", "flash_attention_2", "sdpa", "eager"]
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_name": (list(cls.MODELS.keys()), {"default": "Qwen3-ASR-1.7B"}),
                "precision": (cls.PRECISIONS, {"default": "bf16"}),
                "attention": (cls.ATTENTIONS, {"default": "auto"}),
            },
        }

    RETURN_TYPES = ("QWEN3_ASR_MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_model"
    CATEGORY = "Qwen3-ASR"

    def load_model(self, model_name, precision, attention):
        models_dir = folder_paths.models_dir
        local_model_path = os.path.join(models_dir, "Qwen3-ASR", model_name)
        print(f"[Qwen3-ASR] Using local model: {local_model_path}")

        device = mm.get_torch_device()
        
        dtype = torch.float32
        if precision == "bf16":
            if device.type == "mps":
                dtype = torch.float16
                print("Note: Using fp16 on MPS (bf16 has limited support)")
            else:
                dtype = torch.bfloat16
        elif precision == "fp16":
            dtype = torch.float16

        model_load_args = dict(
            dtype=dtype,
            device_map=str(device),
            max_inference_batch_size=32,
            max_new_tokens=512,
        )
        if attention != "auto":
            model_load_args["attn_implementation"] = attention

        model = Qwen3ASRModel.from_pretrained(local_model_path, **model_load_args)

        print(f"[Qwen3-ASR] Model loaded: {model_name}")
        return (model,)



class PLQwen3ASRTranscribe:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("QWEN3_ASR_MODEL",),
                "audio": ("AUDIO",),
            },
            "optional": {
                "language": (TRANSCRIBE_SUPPORTED_LANGUAGES, {"default": "auto"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "language_text")
    FUNCTION = "transcribe"
    CATEGORY = "Qwen3-ASR"

    def transcribe(self, model, audio, language="auto"):
        audio_data = load_audio_input(audio)
        if audio_data is None:
            return ("", "", "")
        
        lang = None if language == "Auto" else language
        
        results = model.transcribe(
            audio=audio_data,
            language=lang,
            return_time_stamps=False,
        )
        
        result = results[0]
        text = result.text
        language_text = result.language or ""        
        
        return (text, language_text)

NODE_CLASS_MAPPINGS = {
    "PLQwen3ASRLoader": PLQwen3ASRLoader,
    "PLQwen3ASRTranscribe": PLQwen3ASRTranscribe,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PLQwen3ASRLoader": "PL Qwen3 ASR Loader",
    "PLQwen3ASRTranscribe": "PL Qwen3 ASR Transcribe",
}
