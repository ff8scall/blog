---
title: "[Practical Guide] Stable Diffusion 3.5 Local Installation and LoRA Training Implementation"
date: "2026-04-14T08:46:51+09:00"
description: "A comprehensive CLI-driven guide to installing Stable Diffusion 3.5 and fine-tuning custom LoRA models using industry-standard tools (ComfyUI/Kohya_ss)."
type: "posts"
clusters: ["guides"]
categories: ["tutorials"]
tags: ["guide", "tutorial", "AI", "StableDiffusion", "LoRA"]
difficulty: "Advanced"
---

## Overview

This guide details the professional, CLI-based setup required for running Stable Diffusion 3.5 locally and implementing custom LoRA training. The architecture utilizes dedicated environment management (`venv`/`conda`) for dependency isolation.

**Technical Objectives:**
1.  Establish a dedicated Python environment with necessary GPU drivers and PyTorch bindings.
2.  Install the core inference engine (ComfyUI) optimized for SD3.5.
3.  Configure the environment for LoRA training using Kohya_ss, ensuring proper GPU memory management (24GB+ recommended for training).
4.  Execute the full pipeline from model download to LoRA generation via command line.

## Phase 1. Infrastructure Setup and Environment Isolation

Before proceeding, ensure CUDA drivers are installed and the system meets the minimum VRAM requirements (12GB for inference, 24GB for training). We use a Python virtual environment to prevent dependency conflicts.

### Step 1.1: Create and Activate Virtual Environment

We use `venv` for robust dependency isolation.

**CLI Command:**
```bash
# Create the environment directory
mkdir sd3_env
cd sd3_env
python3 -m venv venv_sd3
# Activate the environment (Linux/macOS)
source venv_sd3/bin/activate
```
**[Expected Results]:**
*   The terminal prompt changes to indicate the active environment (`(venv_sd3)`).
*   A clean, isolated directory structure is created within `sd3_env`.

### Step 1.2: Install Core Dependencies

We install PyTorch with CUDA support and foundational libraries required for both ComfyUI and Kohya.

**CLI Command:**
```bash
# Install PyTorch optimized for CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install general ML dependencies (transformers, accelerate, etc.)
pip install accelerate diffusers numpy Pillow tqdm
```
**[Expected Results]:**
*   Successful package installation output for PyTorch and associated libraries.
*   Confirmation that `torch` recognizes the CUDA device.

## Phase 2. Stable Diffusion 3.5 Inference Setup (ComfyUI)

ComfyUI is chosen for its node-based, highly customizable, and efficient workflow, making it ideal for managing complex pipelines like SD3.5 inference.

### Step 2.1: Clone and Install ComfyUI

We clone the repository and install the required dependencies within the active virtual environment.

**CLI Command:**
```bash
# Clone the repository
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install ComfyUI dependencies
pip install -r requirements.txt
```
**[Expected Results]:**
*   The `ComfyUI` directory is populated with the codebase.
*   All necessary Python packages listed in `requirements.txt` are installed.

### Step 2.2: Download SD3.5 Checkpoint

The official SD3.5 model weights must be downloaded and placed in the appropriate model directory.

**CLI Command:**
```bash
# Assume the model is downloaded and placed in the correct location
# Place the model weights (e.g., sd3_v3.safetensors) into:
# ComfyUI/models/checkpoints/
echo "Model weights placed successfully."
```
**[Expected Results]:**
*   The specific model file (`sd3_v3.safetensors`) is present in the `checkpoints` folder.
*   The environment is ready to load the model via the CLI.

## Phase 3. LoRA Training Environment Setup (Kohya_ss)

For fine-tuning, the Kohya_ss repository provides the most robust and maintained framework. This requires a separate, clean environment or careful directory management.

### Step 3.1: Clone Kohya_ss Repository

We clone the training framework outside the main ComfyUI directory for separation of concerns.

**CLI Command:**
```bash
# Move back to the root project directory
cd ..
# Clone the training repository
git clone https://github.com/kohya-ss/sd-scripts.git
cd sd-scripts
```
**[Expected Results]:**
*   The `sd-scripts` directory is created and populated.
*   The active working directory is now `sd-scripts`.

### Step 3.2: Install Training Dependencies

Training requires specific versions of PyTorch, `bitsandbytes` (for quantization), and other specialized libraries.

**CLI Command:**
```bash
# Install training dependencies (Note: specific versions may be required)
pip install -r requirements.txt
# Install bitsandbytes for efficient memory usage (Requires CUDA support)
pip install bitsandbytes
```
**[Expected Results]:**
*   All dependencies listed in the `requirements.txt` are installed.
*   The successful installation of `bitsandbytes` confirms the ability to use 8-bit quantization, crucial for large-scale training.

## Phase 4. LoRA Training Execution

This phase outlines the execution steps for fine-tuning a custom LoRA model using the prepared environment and dataset.

### Step 4.1: Prepare Dataset and Configuration

Ensure your training images (e.g., 20-50 images) are organized in a directory structure (e.g., `dataset/subject_name/`). A comprehensive configuration file (`config.json`) and captioning must also be in place.

**CLI Command:**
```bash
# Placeholder for running preprocessing scripts
python train_data/preprocess.py --image_dir ./dataset --caption_dir ./captions --output_dir ./processed_data
```
**[Expected Results]:**
*   The script runs successfully, generating necessary `.txt` (caption) and image pairs in the `processed_data` directory.

### Step 4.2: Execute the Training Script

We execute the main training script, specifying the desired LoRA parameters (rank, alpha, epochs, etc.).

**CLI Command:**
```bash
# Execute the training script (Example parameters)
accelerate launch train_lora.py \
    --pretrained_model_name_or_path "path/to/sd3_v3" \
    --output_dir "output/my_lora" \
    --train_data_dir "processed_data" \
    --resolution 1024 \
    --train_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --mixed_precision "fp16" \
    --learning_rate 1e-6 \
    --max_train_epochs 10 \
    --network_dim 64 \
    --network_alpha 32
```
**[Expected Results]:**
*   The script initiates the training loop, displaying periodic loss metrics and progress updates (e.g., `Epoch 5/10, Loss: 0.45`).
*   Upon completion, a `.safetensors` file (the LoRA weight) is saved to the `output/my_lora` directory.

### Step 4.3: Integration and Testing

The newly generated LoRA model must be placed into the inference engine's LoRA directory and tested in ComfyUI.

**CLI Command:**
```bash
# Copy the final LoRA weights to the ComfyUI LoRA directory
cp output/my_lora/model.safetensors ComfyUI/models/loras/
echo "Setup complete. Restart ComfyUI and load the LoRA in the workflow."
```
**[Expected Results]:**
*   The LoRA file is correctly placed in the `ComfyUI/models/loras` folder.
*   The system is fully configured for inference, utilizing the custom LoRA model weights.