from ultralytics import YOLO
import os
import time
import cv2
import torch
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp
from functools import partial
import numpy as np

class OptimizedYOLOProcessor:
    def __init__(self, model_path, class_id=2, device='auto', batch_size=32):
        self.class_id = class_id
        self.batch_size = batch_size
        
        # Auto-detect best device
        if device == 'auto':
            if torch.cuda.is_available():
                self.device = 'cuda'
                print(f"🚀 Using GPU: {torch.cuda.get_device_name()}")
            else:
                self.device = 'cpu'
                print("💻 Using CPU")
        else:
            self.device = device
        
        # Load model with optimizations
        self.model = YOLO(model_path)
        self.model.to(self.device)
        
        # Enable optimization features
        if hasattr(self.model.model, 'half') and self.device == 'cuda':
            self.model.model.half()  # Use FP16 for faster inference
            print("⚡ Enabled FP16 precision")
        
        # Warm up model
        self._warmup_model()
    
    def _warmup_model(self):
        """Warm up model with dummy input"""
        print("🔥 Warming up model...")
        dummy_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        self.model.predict(dummy_img, verbose=False, save=False)
        print("✅ Model warmed up")
    
    def preprocess_images_batch(self, image_paths, target_size=640):
        """Preprocess images in batch for faster inference"""
        images = []
        valid_paths = []
        
        for img_path in image_paths:
            img = cv2.imread(img_path)
            if img is not None:
                # Resize to model input size for consistency
                img_resized = cv2.resize(img, (target_size, target_size))
                images.append(img_resized)
                valid_paths.append(img_path)
        
        return images, valid_paths
    
    def process_batch_optimized(self, image_paths, conf_threshold=0.4):
        """Process a batch of images with optimizations"""
        if not image_paths:
            return []
        
        # Batch prediction - much faster than individual predictions
        results = self.model.predict(
            source=image_paths,
            conf=conf_threshold,
            save=False,
            verbose=False,
            stream=False,  # Process all at once
            device=self.device,
            batch=min(self.batch_size, len(image_paths))
        )
        
        return results
    
    def save_labels_batch(self, results, label_dir):
        """Save labels in batch using threading"""
        def save_single_label(result):
            name = Path(result.path).stem
            label_path = os.path.join(label_dir, f"{name}.txt")
            
            if len(result.boxes) > 0:
                with open(label_path, "w") as f:
                    for box in result.boxes:
                        xywh = box.xywh[0].tolist()
                        x, y, w, h = xywh
                        f.write(f"{self.class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
                return name, True
            return name, False
        
        # Use threading for I/O operations
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(save_single_label, result) for result in results]
            
            success_count = 0
            failed_images = []
            
            for future in as_completed(futures):
                name, success = future.result()
                if success:
                    success_count += 1
                else:
                    failed_images.append(name)
        
        return success_count, failed_images

def chunk_list(lst, chunk_size):
    """Split list into chunks for batch processing"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def get_optimal_batch_size():
    """Calculate optimal batch size based on available memory"""
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
        if gpu_memory >= 8:
            return 64
        elif gpu_memory >= 4:
            return 32
        else:
            return 16
    else:
        return 16  # Conservative for CPU

def main():
    # Configuration
    model_path = r"D:\.IMLA\FacialExpression_yolov11\yolov12s-face.pt"
    image_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\test\images"
    label_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\test\labels"
    failed_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\test\labels-n"
    
    # Optimization settings
    batch_size = get_optimal_batch_size()
    initial_conf = 0.4
    retry_confs = [0.3, 0.2, 0.1, 0.05]  # Fewer, strategic retry attempts
    
    print("🚀 OPTIMIZED YOLO FACE DETECTION PIPELINE")
    print(f"⚙️  Batch size: {batch_size}")
    
    # Validate inputs
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    # Create directories
    os.makedirs(label_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)
    
    # Get image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [
        str(p) for p in Path(image_dir).iterdir() 
        if p.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        print(f"❌ No images found in {image_dir}")
        return
    
    print(f"📸 Processing {len(image_files)} images")
    
    # Initialize processor
    processor = OptimizedYOLOProcessor(model_path, batch_size=batch_size)
    
    # Statistics
    total_images = len(image_files)
    total_success = 0
    total_failed = []
    retry_count = 0
    
    start_time = time.time()
    
    # Process in optimized batches
    print(f"\n🔍 Initial batch processing (conf={initial_conf})...")
    
    failed_images = []
    processed = 0
    
    for batch_idx, image_batch in enumerate(chunk_list(image_files, batch_size)):
        print(f"⚡ Processing batch {batch_idx + 1}/{(len(image_files) + batch_size - 1) // batch_size}")
        
        # Process batch
        results = processor.process_batch_optimized(image_batch, initial_conf)
        
        # Save labels in parallel
        success_count, batch_failed = processor.save_labels_batch(results, label_dir)
        
        total_success += success_count
        failed_images.extend([os.path.join(image_dir, f"{name}.png") for name in batch_failed])
        processed += len(image_batch)
        
        # Progress update
        success_rate = (total_success / processed) * 100
        print(f"   Progress: {processed}/{total_images} | Success: {success_rate:.1f}%")
    
    # Strategic retry for failed images
    if failed_images:
        print(f"\n🔄 Smart retry for {len(failed_images)} failed images...")
        
        remaining_failed = failed_images.copy()
        
        for conf in retry_confs:
            if not remaining_failed:
                break
                
            print(f"   Trying conf={conf}...")
            current_batch_failed = []
            
            # Process failed images in batches
            for batch in chunk_list(remaining_failed, batch_size // 2):  # Smaller batches for retries
                results = processor.process_batch_optimized(batch, conf)
                success_count, batch_failed = processor.save_labels_batch(results, label_dir)
                
                total_success += success_count
                retry_count += success_count
                current_batch_failed.extend([os.path.join(image_dir, f"{name}.png") for name in batch_failed])
            
            remaining_failed = current_batch_failed
            print(f"   Recovered: {len(failed_images) - len(remaining_failed)} images")
        
        # Handle permanently failed images
        if remaining_failed:
            print(f"📁 Saving {len(remaining_failed)} permanently failed images...")
            
            def save_failed_image(img_path):
                name = Path(img_path).stem
                img = cv2.imread(img_path)
                if img is not None:
                    failed_path = os.path.join(failed_dir, f"{name}.jpg")
                    cv2.imwrite(failed_path, img)
                return name
            
            # Save failed images in parallel
            with ThreadPoolExecutor(max_workers=8) as executor:
                total_failed = list(executor.map(save_failed_image, remaining_failed))
    
    # Calculate final statistics
    end_time = time.time()
    total_time = end_time - start_time
    success_rate = (total_success / total_images) * 100
    fail_rate = (len(total_failed) / total_images) * 100
    images_per_sec = total_images / total_time
    
    # Final report
    print("\n" + "="*60)
    print("🎯 OPTIMIZED PROCESSING REPORT")
    print("="*60)
    print(f"📊 RESULTS:")
    print(f"   Total images: {total_images}")
    print(f"   ✅ Successfully labeled: {total_success} ({success_rate:.1f}%)")
    print(f"   ❌ Failed: {len(total_failed)} ({fail_rate:.1f}%)")
    print(f"   🔄 Recovered via retry: {retry_count}")
    
    print(f"\n⚡ PERFORMANCE:")
    print(f"   Total time: {total_time:.2f} seconds")
    print(f"   Speed: {images_per_sec:.1f} images/second")
    print(f"   Avg per image: {(total_time / total_images * 1000):.1f} ms")
    
    if total_failed:
        print(f"\n❌ Failed images saved to: {failed_dir}")
    
    print("="*60)
    print("🎉 OPTIMIZATION COMPLETE!")

if __name__ == "__main__":
    main()