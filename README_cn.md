简体中文 | [English](README.md)

# ComfyUI_PL_Qwen3_ASR

基于 [Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR) 的 ComfyUI 语音识别插件。

## 原项目

[https://github.com/QwenLM/Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR)

## 功能特性

- 🎤 **语音转文字**：高精度语音识别
- 🌍 **多语言支持**：支持52种语言/方言，自动语言检测
- ⏱️ **强制对齐**：生成 字/词/行 级别的时间戳
- 🤖 **多种输出格式**：支持 json、srt、lrc 格式
- 📊 **长音频支持**：支持长音频（超长音频自动分段处理）

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install qwen-asr torchaudio
```

### 2. 模型下载

需要手动将模型下载到以下目录：

```
ComfyUI/models/Qwen3-ASR/
├── Qwen3-ASR-1.7B/           # ASR 模型 (1.7B, 默认)
├── Qwen3-ASR-0.6B/           # ASR 模型 (0.6B, 更轻量)
└── Qwen3-ForcedAligner-0.6B/ # 强制对齐模型
```

## 节点说明

### 1. PL Qwen3 ASR Loader

加载 Qwen3-ASR 语音识别模型。

**输入参数：**
- `model_name`：选择模型版本
  - `Qwen3-ASR-1.7B`（默认）- 精度更高
  - `Qwen3-ASR-0.6B` - 速度更快，显存占用更低
- `precision`：默认 `bf16`
- `attention`：默认 `auto`

**输出：**
- `model`：ASR 模型，用于转录节点

### 2. PL Qwen3 ASR Transcribe

语音转文字。

**输入参数：**
- `model`：来自 Loader 节点的模型
- `audio`：音频输入（ComfyUI AUDIO 类型）
- `language`：语言选择（默认：Auto 自动检测）

**输出：**
- `text`：识别的文本
- `language_text`：检测到的语言

### 3. PL Qwen3 ForcedAligner Loader

加载强制对齐模型，用于生成时间戳。

**输入参数：**
- `model_name`：选择模型版本
  - `Qwen3-ForcedAligner-0.6B`（默认）
- `precision`：默认 `bf16`
- `attention`：默认 `auto`

**输出：**
- `aligner`：对齐器模型，用于对齐节点

### 4. PL Qwen3 Forced Align

生成 字/词/行 级别的时间戳。

**输入参数：**
- `aligner`：来自 Loader 节点的对齐器
- `audio`：音频输入（ComfyUI AUDIO 类型）
- `text`：要对齐的文本
- `language_text`：语言（方便与`PL Qwen3 ASR Transcribe`节点串联，优先级高于参数`language`，只有此参数为空时，参数`language`才生效）
- `language`：语言选择
- `srt_begin_idx`：srt输出的开始索引值（默认：1，大于1时，可以为srt输出留出索引，方便填充其他信息）。

**输出：**
- `json`：字/词 级别的时间戳，json格式
- `sentence`：字/词 级别的时间戳
- `srt`：行 级别的时间戳，常用于字幕文本的生成，一般需要预先提供用于对齐的文本，并按行排列
- `lrc`：行 级别的时间戳，常用于歌词文本的生成，一般需要预先提供用于对齐的文本，并按行排列

## 支持的语言

**ASR（52种语言）：** 中文、英语、粤语、阿拉伯语、德语、法语、西班牙语、葡萄牙语、印尼语、意大利语、韩语、俄语、泰语、越南语、日语、土耳其语、印地语、马来语、荷兰语、瑞典语、丹麦语、芬兰语、波兰语、捷克语、菲律宾语、波斯语、希腊语、罗马尼亚语、匈牙利语、马其顿语等。

**强制对齐（11种语言）：** 中文、英语、粤语、法语、德语、意大利语、日语、韩语、葡萄牙语、俄语、西班牙语

## 许可证

本项目遵循原 Qwen3-ASR 项目的许可证。

## 相关链接

- [Qwen3-ASR 原项目](https://github.com/QwenLM/Qwen3-ASR)
- [Qwen3-ASR HuggingFace 模型](https://huggingface.co/Qwen)
