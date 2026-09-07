import os
import json
import numpy as np
import torch
import folder_paths
import comfy.model_management as mm
from qwen_asr import Qwen3ForcedAligner
from .utils import load_audio_input, ALIGNER_SUPPORTED_LANGUAGES, aligner_to_sentence, aligner_to_srt, aligner_to_lrc


class PLQwen3ForcedAlignerLoader:
    """加载 Qwen3-ForcedAligner 模型"""
    
    MODELS = {
        "Qwen3-ForcedAligner-0.6B": "Qwen/Qwen3-ForcedAligner-0.6B",
    }
    PRECISIONS = ["bf16", "fp16", "fp32"]
    ATTENTIONS = ["auto", "flash_attention_2", "sdpa", "eager"]
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_name": (list(cls.MODELS.keys()), {"default": "Qwen3-ForcedAligner-0.6B"}),
                "precision": (cls.PRECISIONS, {"default": "bf16"}),
                "attention": (cls.ATTENTIONS, {"default": "auto"}),
            },
        }
    
    RETURN_TYPES = ("QWEN3_ALIGNER",)
    RETURN_NAMES = ("aligner",)
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
        )
        if attention != "auto":
            model_load_args["attn_implementation"] = attention

        aligner = Qwen3ForcedAligner.from_pretrained(local_model_path, **model_load_args)
        
        print(f"[Qwen3-ASR] ForcedAligner loaded: {model_name}")
        return (aligner,)


class PLQwen3ForcedAlign:
    """使用 Qwen3-ForcedAligner 进行文本-语音对齐，返回时间戳"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "aligner": ("QWEN3_ALIGNER",),
                "audio": ("AUDIO",),
                "text": ("STRING", {"multiline": True}),
                "language_text": ("STRING", {"multiline": False}),
                "language": (ALIGNER_SUPPORTED_LANGUAGES, {"default": "Chinese"}),
                "srt_begin_idx": ("INT", {"default": 1, "min": 1, "max": 2**31 - 1, "tooltip": "When it is greater than 1, an index can be left for SRT output to facilitate filling in other information."}),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING","STRING", "STRING",)
    RETURN_NAMES = ("json", "sentence", "srt", "lrc",)
    FUNCTION = "align"
    CATEGORY = "Qwen3-ASR"

    def align(self, aligner, audio, text, language_text, language, srt_begin_idx):        
        audio_data = load_audio_input(audio)
        if audio_data is None:
            return ("", "", "", "")
        
        ctx = text if text.strip() else ""
        ctx = ctx if ctx else None
        if ctx is None:
            return ("", "", "", "")
        
        lang = language_text if language_text.strip() else ""
        lang = lang if lang else None
        if lang is None:
            lang = language
        
        results = aligner.align(
            audio=audio_data,
            text=ctx,
            language=lang,
        )
        
        items = results[0]
        json_items = []
        for item in items:
            json_items.append({'start': item.start_time, 'end': item.end_time, 'text': item.text})
        json_str = json.dumps(json_items, ensure_ascii=False, indent=4)
        sentence_str = aligner_to_sentence(ctx, items)
        srt_str = aligner_to_srt(ctx, items, srt_begin_idx)
        lrc_str = aligner_to_lrc(ctx, items)
        
        print(f"[Qwen3-ASR] Alignment completed")
        
        return (json_str, sentence_str, srt_str, lrc_str,)


NODE_CLASS_MAPPINGS = {
    "PLQwen3ForcedAlignerLoader": PLQwen3ForcedAlignerLoader,
    "PLQwen3ForcedAlign": PLQwen3ForcedAlign,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PLQwen3ForcedAlignerLoader": "PL Qwen3 ForcedAligner Loader",
    "PLQwen3ForcedAlign": "PL Qwen3 Forced Align",
}
