###The Python.h error is still the same root cause — Triton/Torch Inductor is trying to JIT-compile kernels and can't find the Python headers.
#Even in non-Unsloth mode, Gemma 4's official HF implementation uses torch.compile aggressively (especially on the new # architecture with per-layer projections, KV sharing, etc.), so the same compilation step triggers.
# Install Python Dev Headers (Must Do)


sudo apt update
sudo apt install python3.12-dev build-essential -y

# Then clear all caches:
rm -rf ~/.triton/cache
rm -rf /tmp/torchinductor*
rm -rf ~/.cache/huggingface
rm -rf ~/.cache/torch