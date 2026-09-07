import string
import re
import numpy as np
import torch

TRANSCRIBE_SUPPORTED_LANGUAGES = [
    "Auto",
    "Chinese",
    "English",
    "Cantonese",
    "Arabic",
    "German",
    "French",
    "Spanish",
    "Portuguese",
    "Indonesian",
    "Italian",
    "Korean",
    "Russian",
    "Thai",
    "Vietnamese",
    "Japanese",
    "Turkish",
    "Hindi",
    "Malay",
    "Dutch",
    "Swedish",
    "Danish",
    "Finnish",
    "Polish",
    "Czech",
    "Filipino",
    "Persian",
    "Greek",
    "Romanian",
    "Hungarian",
    "Macedonian",
]

ALIGNER_SUPPORTED_LANGUAGES = [
    "Chinese",
    "English",
    "Cantonese",
    "French",
    "German",
    "Italian",
    "Japanese",
    "Korean",
    "Portuguese",
    "Russian",
    "Spanish",
]

def load_audio_input(audio_input):
    if audio_input is None:
        return None
        
    waveform = audio_input["waveform"]
    sr = audio_input["sample_rate"]
    
    wav = waveform[0]
    
    if wav.shape[0] > 1:
        wav = torch.mean(wav, dim=0)
    else:
        wav = wav.squeeze(0)
        
    return (wav.numpy().astype(np.float32), sr)

def load_audio_input2(audio_input):
    if audio_input is None:
        return None
    
    # 处理 ComfyUI AUDIO 格式: {"waveform": tensor, "sample_rate": int}
    waveform = audio_input["waveform"]  # shape: (batch, channels, samples)
    sample_rate = audio_input["sample_rate"]
    
    # 转换为 numpy，取第一个 batch，转为单声道
    if isinstance(waveform, torch.Tensor):
        waveform = waveform.cpu().numpy()
    
    # 处理维度: (batch, channels, samples) -> (samples,)
    if waveform.ndim == 3:
        waveform = waveform[0]  # 取第一个 batch
    if waveform.ndim == 2:
        waveform = np.mean(waveform, axis=0)  # 多声道转单声道
    
    waveform = waveform.astype(np.float32)        
    return (waveform.numpy().astype(np.float32), sample_rate)

def seconds_to_srt_time(seconds):
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def seconds_to_lrc_time(seconds):
    """Convert seconds to LRC time format (MM:SS,mmm)"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{minutes:02d}:{secs:02d},{milliseconds:03d}"

def aligner_to_sentence(text, items):
    if text is None:
        return None
    if items is None:
        return None
    
    texts, starts, ends = [], [], []    
    segments = [s for s in re.split(r'[。？！，、；.?!,;：:\s]+', text) if s]
    item_idx = 0
    for seg in segments:
        seg_start = None
        seg_end = None
        matched = ""
        while item_idx < len(items) and len(matched) < len(seg):
            if seg_start is None:
                seg_start = items[item_idx].start_time
            seg_end = items[item_idx].end_time
            matched += items[item_idx].text
            item_idx += 1
        if seg_start is not None:
            texts.append(seg)
            starts.append(f"{seg_start:.3f}")
            ends.append(f"{seg_end:.3f}")
    
    sentence_str = "\n".join(f"{t}\t{s}\t{e}" for t, s, e in zip(texts, starts, ends))
    return sentence_str

def aligner_to_srt(text, items, srt_begin_idx = 1):
    if text is None:
        return None
    if items is None:
        return None

    item_idx = 0
    srt_begin_idx = 1 if srt_begin_idx < 2 else srt_begin_idx
    line_idx = srt_begin_idx - 1
    texts = []
    lines = str.splitlines(text)
    for line in lines:
        cl = re.sub(r'[^\w\s]', ' ', line, flags=re.UNICODE)
        sl = re.sub(r'\s+', ' ', cl).strip()
        tl = sl if sl.strip() else ""
        if tl == "":
            continue 

        line_idx += 1
        seg_start = None
        seg_end = None

        segments = [s for s in re.split(r'[\s]+', tl) if s]
        for seg in segments:
            matched = ""
            while item_idx < len(items) and len(matched) < len(seg):
                if seg_start is None:
                    seg_start = items[item_idx].start_time
                seg_end = items[item_idx].end_time
                matched += items[item_idx].text
                item_idx += 1
        
        if seg_start is not None:
            start_time = seconds_to_srt_time(seg_start)
            end_time = seconds_to_srt_time(seg_end)
            texts.append(f"{line_idx}")
            texts.append(f"{start_time} --> {end_time}")
            texts.append(line)
            texts.append("")
    
    srt_str = "\n".join(texts)
    return srt_str

def aligner_to_lrc(text, items):
    if text is None:
        return None
    if items is None:
        return None

    item_idx = 0
    line_idx = 0
    texts = []
    lines = str.splitlines(text)
    for line in lines:
        cl = re.sub(r'[^\w\s]', ' ', line, flags=re.UNICODE)
        sl = re.sub(r'\s+', ' ', cl).strip()
        tl = sl if sl.strip() else ""
        if tl == "":
            continue 

        line_idx += 1
        seg_start = None
        seg_end = None

        segments = [s for s in re.split(r'[\s]+', tl) if s]
        for seg in segments:
            matched = ""
            while item_idx < len(items) and len(matched) < len(seg):
                if seg_start is None:
                    seg_start = items[item_idx].start_time
                seg_end = items[item_idx].end_time
                matched += items[item_idx].text
                item_idx += 1
        
        if seg_start is not None:
            start_time = seconds_to_lrc_time(seg_start)
            texts.append(f"[{start_time}] {line}")
            texts.append("")
    
    lrc_str = "\n".join(texts)
    return lrc_str
