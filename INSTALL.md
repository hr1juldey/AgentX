# Installation Instructions

## Requirements Split

Dependencies have been split into two files to handle PyTorch CUDA installation properly:

- **`requirements-pytorch.txt`** - PyTorch with CUDA 13.0 support
- **`requirements-core.txt`** - All other dependencies

## Installation Order (IMPORTANT!)

Install in this order to avoid PyTorch conflicts:

```bash
# Step 1: Install PyTorch with CUDA 13.0 (using uv pip with custom index)
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# Step 2: Install everything else (using standard uv add or uv pip)
uv pip install -r requirements-core.txt
```

**OR with `uv add` (for project dependencies):**

```bash
# Step 1: Install PyTorch with CUDA 13.0
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# Step 2: Add core packages to project
uv add -r requirements-core.txt
```

## Why This Split?

PyTorch with CUDA requires a special wheel index (`https://download.pytorch.org/whl/cu130`).

If you mix PyTorch CUDA packages with regular PyPI packages in a single `requirements.txt`, pip may:
- Pull the CPU-only version of PyTorch from PyPI
- Ignore the CUDA wheel index
- Cause version conflicts

## Verify Installation

```bash
# Check PyTorch has CUDA support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"

# Expected output:
# CUDA available: True
# CUDA version: 13.0

# Check other packages
python -c "import dspy, mem0, fastembed, qdrant_client; print('Core packages OK')"
```

## Troubleshooting

### PyTorch shows CUDA as False

You likely got the CPU version. Reinstall PyTorch:

```bash
uv pip uninstall torch torchvision torchaudio
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
```

### Version Conflicts

If you see dependency errors, try:

```bash
# Create fresh virtual environment with uv
uv venv .venv
source .venv/bin/activate

# Install in correct order
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
uv pip install -r requirements-core.txt
```

## GPU Info

Your system has:
- **GPU:** NVIDIA GeForce RTX 3060
- **VRAM:** 12GB
- **CUDA Version:** 13.0
- **Driver:** 580.82.09

This setup is optimized for your hardware configuration.
