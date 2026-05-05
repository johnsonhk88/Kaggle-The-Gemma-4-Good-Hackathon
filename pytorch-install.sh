pip uninstall torch torchvision torchaudio -y 

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

pip install --upgrade torch torchaudio --index-url https://download.pytorch.org/whl/cu128

# install for window envirorment used at least driver
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130


# Install the version that supports V100 but works with your 12.8 driver
# 1. Remove the mismatched/incompatible packages
pip uninstall -y torch torchvision torchaudio torchao

# 2. Install PyTorch built with CUDA 12.6 (this version still includes sm_70 / V100 support)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# 3. Reinstall torchao (it will now pull the correct wheel for your new PyTorch + Python 3.12)
pip install torchao
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126