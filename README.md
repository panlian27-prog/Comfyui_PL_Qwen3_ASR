English | [简体中文](README_cn.md)

# ComfyUI_PL_Qwen3_ASR

A ComfyUI speech recognition plugin based on [Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR).

## Original Project

[https://github.com/QwenLM/Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR)

## Features

- 🎤 **Speech-to-Text**: High-accuracy speech recognition
- 🌍 **Multilingual Support**: Supports 52 languages/dialects with automatic language detection
- ⏱️ **Forced Alignment**: Generates character/word/line-level timestamps
- 🤖 **Multiple Output Formats**: Supports json, srt, and lrc formats
- 📊 **Long Audio Support**: Supports long audio (extra-long audio is automatically split into segments)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install qwen-asr torchaudio
```

### 2. Model Download

You need to manually download the models to the following directory:

```
ComfyUI/models/Qwen3-ASR/
├── Qwen3-ASR-1.7B/           # ASR model (1.7B, default)
├── Qwen3-ASR-0.6B/           # ASR model (0.6B, lighter)
└── Qwen3-ForcedAligner-0.6B/ # Forced alignment model
```

## Node Documentation

### 1. PL Qwen3 ASR Loader

Loads the Qwen3-ASR speech recognition model.

**Inputs:**
- `model_name`: Select the model version
  - `Qwen3-ASR-1.7B` (default) - Higher accuracy
  - `Qwen3-ASR-0.6B` - Faster, lower VRAM usage
- `precision`: Default `bf16`
- `attention`: Default `auto`

**Outputs:**
- `model`: The ASR model, used by the transcribe node

### 2. PL Qwen3 ASR Transcribe

Speech-to-text.

**Inputs:**
- `model`: The model from the Loader node
- `audio`: Audio input (ComfyUI AUDIO type)
- `language`: Language selection (default: Auto, automatic detection)

**Outputs:**
- `text`: The recognized text
- `language_text`: The detected language

### 3. PL Qwen3 ForcedAligner Loader

Loads the forced alignment model, used to generate timestamps.

**Inputs:**
- `model_name`: Select the model version
  - `Qwen3-ForcedAligner-0.6B` (default)
- `precision`: Default `bf16`
- `attention`: Default `auto`

**Outputs:**
- `aligner`: The aligner model, used by the align node

### 4. PL Qwen3 Forced Align

Generates character/word/line-level timestamps.

**Inputs:**
- `aligner`: The aligner from the Loader node
- `audio`: Audio input (ComfyUI AUDIO type)
- `text`: The text to align
- `language_text`: Language (for easy chaining with the `PL Qwen3 ASR Transcribe` node; takes priority over the `language` parameter. The `language` parameter only takes effect when this parameter is empty)
- `language`: Language selection
- `srt_begin_idx`: The starting index value of the srt output (default: 1; when greater than 1, it reserves index numbers in the srt output to make room for other information).

**Outputs:**
- `json`: Character/word-level timestamps in json format
- `sentence`: Character/word-level timestamps
- `srt`: Line-level timestamps, commonly used for generating subtitle text. The text to be aligned generally needs to be provided in advance, arranged line by line
- `lrc`: Line-level timestamps, commonly used for generating subtitle text. The text to be aligned generally needs to be provided in advance, arranged line by line

## Supported Languages

**ASR (52 languages):** Chinese, English, Cantonese, Arabic, German, French, Spanish, Portuguese, Indonesian, Italian, Korean, Russian, Thai, Vietnamese, Japanese, Turkish, Hindi, Malay, Dutch, Swedish, Danish, Finnish, Polish, Czech, Filipino, Persian, Greek, Romanian, Hungarian, Macedonian, and more.

**Forced Alignment (11 languages):** Chinese, English, Cantonese, French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish

## License

This project follows the license of the original Qwen3-ASR project.

## Related Links

- [Qwen3-ASR Original Project](https://github.com/QwenLM/Qwen3-ASR)
- [Qwen3-ASR HuggingFace Models](https://huggingface.co/Qwen)