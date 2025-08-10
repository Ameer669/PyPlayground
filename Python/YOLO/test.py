import torch
import sys

def check_pytorch_setup():
    print("🔍 CHECKING YOUR CURRENT PYTORCH SETUP")
    print("="*50)
    
    # Basic info
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print(f"🔥 PyTorch version: {torch.__version__}")
    
    # CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"🚀 CUDA available: {cuda_available}")
    
    if cuda_available:
        print(f"📱 GPU device: {torch.cuda.get_device_name()}")
        print(f"💾 GPU memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
        print("✅ You're ready for GPU acceleration!")
    else:
        print("⚠️  Running on CPU only")
        
        # Check if CUDA-capable GPU exists
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                print("💡 NVIDIA GPU detected but PyTorch can't use it")
                print("🔧 Consider installing GPU-enabled PyTorch")
            else:
                print("💻 No NVIDIA GPU detected - CPU processing is your only option")
        except:
            print("💻 NVIDIA drivers not found - likely no compatible GPU")
    
    # Performance test
    print(f"\n⚡ QUICK PERFORMANCE TEST")
    device = 'cuda' if cuda_available else 'cpu'
    
    # Create test tensor
    x = torch.randn(1000, 1000).to(device)
    
    import time
    start = time.time()
    for _ in range(100):
        y = torch.mm(x, x)
    end = time.time()
    
    print(f"📊 Matrix multiplication test: {(end-start)*1000:.1f}ms")
    print(f"🎯 Using device: {device}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if cuda_available:
        print("✅ Your setup is optimized! You can use the GPU-accelerated code.")
    else:
        print("🔧 For 10-50x speed boost, consider:")
        print("   1. Check if you have NVIDIA GPU: run 'nvidia-smi' in terminal")
        print("   2. Install GPU PyTorch: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        print("   3. Or use CPU optimizations in the code")

if __name__ == "__main__":
    check_pytorch_setup()