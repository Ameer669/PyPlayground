from ultralytics import YOLO
import os
import time
import cv2
import torch
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

class OptimizedYOLOProcessor:
    def __init__(self, model_path, class_id=2, device='auto', batch_size=32):
        self.class_id = class_id
        self.batch_size = batch_size
        
        # Auto-detect best device
        if device == 'auto':
            if torch.cuda.is_available():
                self.device = 'cuda'
                print(f"🚀 GPU: {torch.cuda.get_device_name()}")
            else:
                self.device = 'cpu'
                print("💻 Using CPU")
        else:
            self.device = device
        
        # Load and optimize model
        self.model = YOLO(model_path)
        self.model.to(self.device)
        
        if hasattr(self.model.model, 'half') and self.device == 'cuda':
            self.model.model.half()
            print("⚡ FP16 enabled")
        
        # Warm up
        print("🔥 Warming up...")
        dummy = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        self.model.predict(dummy, verbose=False, save=False)
    
    def process_batch(self, image_paths, conf=0.4):
        """Process batch of images"""
        return self.model.predict(
            source=image_paths, conf=conf, save=False, verbose=False,
            device=self.device, batch=min(self.batch_size, len(image_paths))
        )
    
    def save_labels_parallel(self, results, label_dir):
        """Save labels using threading"""
        def save_label(result):
            name = Path(result.path).stem
            label_path = os.path.join(label_dir, f"{name}.txt")
            
            if len(result.boxes) > 0:
                with open(label_path, "w") as f:
                    for box in result.boxes:
                        x, y, w, h = box.xywh[0].tolist()
                        f.write(f"{self.class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
                return name, True
            return name, False
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            results_data = list(executor.map(save_label, results))
        
        success = [name for name, ok in results_data if ok]
        failed = [name for name, ok in results_data if not ok]
        return len(success), failed

def get_file_stems(directory, extensions):
    """Get file stems from directory"""
    if not os.path.exists(directory):
        return set()
    return {p.stem for p in Path(directory).iterdir() if p.suffix.lower() in extensions}

def chunk_list(lst, size):
    """Split list into chunks"""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def get_optimal_batch_size():
    """Get optimal batch size based on GPU memory"""
    if torch.cuda.is_available():
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        return 64 if gpu_mem >= 8 else 32 if gpu_mem >= 4 else 16
    return 16

def cleanup_unmatched_images(image_dir, label_dir, cleanup_dir):
    """Remove images without corresponding labels"""
    image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    print(f"\n🧹 CHECKING FOR UNMATCHED IMAGES...")
    
    image_stems = get_file_stems(image_dir, image_exts)
    label_stems = get_file_stems(label_dir, {'.txt'})
    
    unmatched = image_stems - label_stems
    matched = len(image_stems & label_stems)
    
    print(f"   ✅ Matched: {matched} | ❌ Unmatched: {len(unmatched)}")
    
    if not unmatched:
        print("   🎉 All images have labels!")
        return 0
    
    # Show some examples
    examples = list(unmatched)[:5]
    print(f"   Examples: {', '.join(examples)}{' ...' if len(unmatched) > 5 else ''}")
    
    choice = input(f"   ❓ Move {len(unmatched)} unmatched images to cleanup folder? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("   🛑 Keeping unmatched images")
        return 0
    
    os.makedirs(cleanup_dir, exist_ok=True)
    moved = 0
    
    for stem in unmatched:
        for ext in image_exts:
            src = os.path.join(image_dir, f"{stem}{ext}")
            if os.path.exists(src):
                dst = os.path.join(cleanup_dir, f"{stem}{ext}")
                try:
                    shutil.move(src, dst)
                    moved += 1
                    break
                except Exception as e:
                    print(f"   ❌ Failed to move {stem}: {e}")
    
    print(f"   ✂️  Moved {moved} unmatched images to: {cleanup_dir}")
    return moved

def main():
    # Configuration
    model_path = r"D:\.IMLA\FacialExpression_yolov11\yolov12s-face.pt"
    image_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\vaild\images"
    label_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\vaild\labels"
    failed_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\vaild\failed_detection"
    cleanup_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\vaild\unmatched_images"
    
    # Settings
    batch_size = get_optimal_batch_size()
    initial_conf = 0.4
    retry_confs = [0.25, 0.15, 0.08]
    
    print("🚀 INTEGRATED YOLO PROCESSING PIPELINE")
    print(f"⚙️  Batch size: {batch_size}")
    
    # Validate inputs
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    if not os.path.exists(image_dir):
        print(f"❌ Image directory not found: {image_dir}")
        return
    
    # Create directories
    for dir_path in [label_dir, failed_dir, cleanup_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Get image files
    image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_files = [str(p) for p in Path(image_dir).iterdir() if p.suffix.lower() in image_exts]
    
    if not image_files:
        print(f"❌ No images found in {image_dir}")
        return
    
    print(f"📸 Found {len(image_files)} images")
    
    # Optional: Clean up unmatched images first
    cleanup_choice = input("🧹 Clean up images without labels before processing? (y/n): ").strip().lower()
    if cleanup_choice == 'y':
        moved = cleanup_unmatched_images(image_dir, label_dir, cleanup_dir)
        if moved > 0:
            # Refresh image list after cleanup
            image_files = [str(p) for p in Path(image_dir).iterdir() if p.suffix.lower() in image_exts]
            print(f"📸 Processing {len(image_files)} remaining images")
    
    # Initialize processor
    processor = OptimizedYOLOProcessor(model_path, batch_size=batch_size)
    
    # Statistics
    total_images = len(image_files)
    total_success = 0
    retry_count = 0
    
    start_time = time.time()
    
    # Initial batch processing
    print(f"\n🔍 Batch processing (conf={initial_conf})...")
    failed_images = []
    
    for batch_idx, batch in enumerate(chunk_list(image_files, batch_size)):
        print(f"⚡ Batch {batch_idx + 1}/{(len(image_files) + batch_size - 1) // batch_size}")
        
        results = processor.process_batch(batch, initial_conf)
        success_count, batch_failed = processor.save_labels_parallel(results, label_dir)
        
        total_success += success_count
        failed_images.extend([os.path.join(image_dir, f"{name}.png") for name in batch_failed])
        
        # Progress
        processed = (batch_idx + 1) * len(batch)
        if processed > total_images:
            processed = total_images
        success_rate = (total_success / processed) * 100
        print(f"   Progress: {processed}/{total_images} | Success: {success_rate:.1f}%")
    
    # Retry failed images
    if failed_images:
        print(f"\n🔄 Retrying {len(failed_images)} failed images...")
        remaining = failed_images.copy()
        
        for conf in retry_confs:
            if not remaining:
                break
            
            print(f"   Trying conf={conf}...")
            current_failed = []
            
            for batch in chunk_list(remaining, batch_size // 2):
                results = processor.process_batch(batch, conf)
                success_count, batch_failed = processor.save_labels_parallel(results, label_dir)
                
                total_success += success_count
                retry_count += success_count
                current_failed.extend([os.path.join(image_dir, f"{name}.png") for name in batch_failed])
            
            recovered = len(remaining) - len(current_failed)
            print(f"   Recovered: {recovered} images")
            remaining = current_failed
        
        # Save permanently failed images
        if remaining:
            print(f"📁 Saving {len(remaining)} failed images...")
            
            def save_failed(img_path):
                name = Path(img_path).stem
                img = cv2.imread(img_path)
                if img is not None:
                    cv2.imwrite(os.path.join(failed_dir, f"{name}.jpg"), img)
                return name
            
            with ThreadPoolExecutor(max_workers=8) as executor:
                final_failed = list(executor.map(save_failed, remaining))
    
    # Final statistics
    end_time = time.time()
    total_time = end_time - start_time
    final_failed_count = len(remaining) if failed_images else 0
    success_rate = (total_success / total_images) * 100
    
    # Final report
    print("\n" + "="*50)
    print("🎯 PROCESSING COMPLETE")
    print("="*50)
    print(f"📊 Results: {total_success}/{total_images} successful ({success_rate:.1f}%)")
    print(f"🔄 Recovered via retry: {retry_count}")
    print(f"❌ Final failures: {final_failed_count}")
    print(f"⚡ Speed: {total_images/total_time:.1f} images/sec")
    print(f"🕒 Total time: {total_time:.1f}s")
    
    if final_failed_count == 0:
        print("🎉 ALL IMAGES SUCCESSFULLY PROCESSED!")
    
    # Optional: Final cleanup of unmatched images
    final_cleanup = input(f"\n🧹 Final cleanup of unmatched images? (y/n): ").strip().lower()
    if final_cleanup == 'y':
        cleanup_unmatched_images(image_dir, label_dir, cleanup_dir)
    
    print("="*50)

if __name__ == "__main__":
    main()