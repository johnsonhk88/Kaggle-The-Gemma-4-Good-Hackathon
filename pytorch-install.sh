pip uninstall torch torchvision torchaudio -y 

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128


# Install the version that supports V100 but works with your 12.8 driver
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126