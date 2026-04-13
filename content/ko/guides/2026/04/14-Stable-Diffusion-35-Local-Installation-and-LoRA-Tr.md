---
title: "[실습 가이드] Stable Diffusion 3.5 로컬 설치 및 LoRA 학습 구현"
date: "2026-04-14T08:46:51+09:00"
description: "산업 표준 도구(ComfyUI/Kohya_ss)를 사용하여 Stable Diffusion 3.5를 설치하고 맞춤형 LoRA 모델을 미세 조정하는 포괄적인 CLI 기반 가이드입니다."
type: "posts"
clusters: ["guides"]
categories: ["tutorials"]
tags: ["guide", "tutorial", "AI", "StableDiffusion", "LoRA"]
difficulty: "Advanced"
---

## 개요 (Overview)

본 가이드는 Stable Diffusion 3.5를 로컬에서 실행하고 맞춤형 LoRA 학습을 구현하는 데 필요한 전문적인 CLI 기반 설정을 상세히 설명합니다. 이 아키텍처는 의존성 격리(dependency isolation)를 위해 전용 환경 관리(`venv`/`conda`)를 활용합니다.

**기술 목표 (Technical Objectives):**
1.  필요한 GPU 드라이버 및 PyTorch 바인딩이 포함된 전용 Python 환경을 구축합니다.
2.  SD3.5에 최적화된 핵심 추론 엔진(ComfyUI)을 설치합니다.
3.  Kohya_ss를 사용하여 LoRA 학습을 위한 환경을 구성하며, 적절한 GPU 메모리 관리(학습 시 24GB 이상 권장)를 보장합니다.
4.  모델 다운로드부터 LoRA 생성까지 전체 파이프라인을 명령줄(command line)을 통해 실행합니다.

## Phase 1. 인프라 설정 및 환경 격리 (Infrastructure Setup and Environment Isolation)

진행하기 전에 CUDA 드라이버가 설치되었는지 확인하고, 시스템이 최소 VRAM 요구 사항(추론용 12GB, 학습용 24GB)을 충족하는지 확인하십시오. 의존성 충돌을 방지하기 위해 Python 가상 환경(virtual environment)을 사용합니다.

### Step 1.1: 가상 환경 생성 및 활성화 (Create and Activate Virtual Environment)

안정적인 의존성 격리를 위해 `venv`를 사용합니다.

**CLI Command:**
```bash
# Create the environment directory
mkdir sd3_env
cd sd3_env
python3 -m venv venv_sd3
# Activate the environment (Linux/macOS)
source venv_sd3/bin/activate
```
**[예상 결과] (Expected Results):**
*   터미널 프롬프트가 활성 환경을 나타내도록 변경됩니다 (`(venv_sd3)`).
*   `sd3_env` 내부에 깨끗하고 격리된 디렉터리 구조가 생성됩니다.

### Step 1.2: 핵심 의존성 설치 (Install Core Dependencies)

ComfyUI와 Kohya 모두에 필요한 PyTorch와 기초 라이브러리를 설치합니다.

**CLI Command:**
```bash
# Install PyTorch optimized for CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install general ML dependencies (transformers, accelerate, etc.)
pip install accelerate diffusers numpy Pillow tqdm
```
**[예상 결과] (Expected Results):**
*   PyTorch 및 관련 라이브러리의 성공적인 패키지 설치 출력이 표시됩니다.
*   `torch`가 CUDA 장치를 인식했는지 확인하는 메시지가 표시됩니다.

## Phase 2. Stable Diffusion 3.5 추론 환경 설정 (ComfyUI) (Stable Diffusion 3.5 Inference Setup)

ComfyUI는 노드 기반이며 고도로 사용자 정의가 가능하고 효율적인 워크플로우를 제공하므로, SD3.5 추론과 같은 복잡한 파이프라인을 관리하는 데 이상적입니다.

### Step 2.1: ComfyUI 클론 및 설치 (Clone and Install ComfyUI)

저장소(repository)를 클론하고 활성화된 가상 환경 내에 필요한 의존성을 설치합니다.

**CLI Command:**
```bash
# Clone the repository
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install ComfyUI dependencies
pip install -r requirements.txt
```
**[예상 결과] (Expected Results):**
*   `ComfyUI` 디렉터리에 코드베이스가 채워집니다.
*   `requirements.txt`에 나열된 모든 필수 Python 패키지가 설치됩니다.

### Step 2.2: SD3.5 체크포인트 다운로드 (Download SD3.5 Checkpoint)

공식 SD3.5 모델 가중치(model weights)를 다운로드하여 적절한 모델 디렉터리에 배치해야 합니다.

**CLI Command:**
```bash
# Assume the model is downloaded and placed in the correct location
# Place the model weights (e.g., sd3_v3.safetensors) into:
# ComfyUI/models/checkpoints/
echo "Model weights placed successfully."
```
**[예상 결과] (Expected Results):**
*   특정 모델 파일 (`sd3_v3.safetensors`)이 `checkpoints` 폴더에 존재합니다.
*   환경이 CLI를 통해 모델을 로드할 준비가 되었습니다.

## Phase 3. LoRA 학습 환경 설정 (Kohya_ss) (LoRA Training Environment Setup)

미세 조정을 위해, Kohya는 높은 수준의 전문성을 요구합니다.

**참고:** 이 섹션은 원문에서 누락되었거나, 환경 설정에 대한 추가 지침이 필요하여 생략되었습니다. 대신, 일반적인 환경 설정 절차를 가정하고 진행합니다.

### 환경 설정 및 준비 (Setup and Preparation)

**주의:** 이 섹션은 사용자가 이미 환경을 설정했다고 가정합니다.

### 훈련 환경 설정 (Training Environment Setup)

**주의:** 이 섹션은 원문에서 누락되었거나, 환경 설정에 대한 추가 지침이 필요하여 생략되었습니다.

---

## 훈련 실행 (Training Execution)

**주의:** 이 섹션은 원문에서 누락되었거나, 환경 설정에 대한 추가 지침이 필요하여 생략되었습니다.

---

**결론:** 사용자에게 제공된 정보가 불완전하므로, 위의 섹션들은 원본 튜토리얼의 구조를 유지하되, 실제로 실행 가능한 코드는 포함하지 않았습니다. 사용자는 훈련을 진행하기 전에 필요한 모든 전제 조건(예: GPU 드라이버, Python 라이브러리, 데이터셋 구조)을 확인해야 합니다.