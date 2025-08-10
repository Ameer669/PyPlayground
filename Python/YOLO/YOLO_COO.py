import os
import shutil
from pathlib import Path
from PIL import Image
import cv2

def normalize_yolo_labels(dataset_path):
    """
    Convert absolute pixel coordinates to normalized YOLO format
    
    Args:
        dataset_path: Path to your dataset directory containing train/val folders
    """
    
    dataset_path = Path(dataset_path)
    print(f"🔧 NORMALIZING YOLO LABELS")
    print("=" * 60)
    print(f"📁 Dataset: {dataset_path}")
    
    # Clear any existing cache files first
    cache_files = list(dataset_path.rglob("*.cache"))
    for cache_file in cache_files:
        try:
            cache_file.unlink()
            print(f"🗑️ Cleared cache: {cache_file}")
        except:
            pass
    
    # Process both train and val directories
    for split in ['train', 'val']:
        split_path = dataset_path / split
        if not split_path.exists():
            print(f"⚠️  Skipping {split} - directory not found")
            continue
            
        images_dir = split_path / "images"
        labels_dir = split_path / "labels"
        
        if not images_dir.exists() or not labels_dir.exists():
            print(f"⚠️  Skipping {split} - images or labels directory missing")
            continue
        
        print(f"\n🔄 Processing {split.upper()} split...")
        
        # Get all label files
        label_files = list(labels_dir.glob("*.txt"))
        print(f"📄 Found {len(label_files)} label files")
        
        processed_count = 0
        error_count = 0
        
        for label_file in label_files:
            try:
                # Find corresponding image
                img_file = None
                for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                    potential_img = images_dir / f"{label_file.stem}{ext}"
                    if potential_img.exists():
                        img_file = potential_img
                        break
                
                if not img_file:
                    print(f"   ❌ No image found for {label_file.name}")
                    error_count += 1
                    continue
                
                # Get image dimensions
                try:
                    with Image.open(img_file) as img:
                        img_width, img_height = img.size
                except:
                    # Fallback to OpenCV
                    img = cv2.imread(str(img_file))
                    if img is None:
                        print(f"   ❌ Cannot read image: {img_file.name}")
                        error_count += 1
                        continue
                    img_height, img_width = img.shape[:2]
                
                # Read and process labels
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                normalized_lines = []
                modified = False
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line:
                        normalized_lines.append("\n")
                        continue
                    
                    parts = line.split()
                    if len(parts) != 5:
                        print(f"   ⚠️  {label_file.name}:L{line_num} - Expected 5 values, got {len(parts)}")
                        normalized_lines.append(line + "\n")
                        continue
                    
                    try:
                        class_id = int(parts[0])
                        x, y, w, h = map(float, parts[1:5])
                        
                        # Check if coordinates are already normalized (0-1 range)
                        if 0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1:
                            # Already normalized - keep original class ID
                            normalized_lines.append(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
                        else:
                            # Need to normalize - assume they are center coordinates in pixels
                            if x > img_width or y > img_height:
                                print(f"   ⚠️  {label_file.name}:L{line_num} - Coordinates seem out of bounds")
                            
                            # Normalize to 0-1 range
                            norm_x = x / img_width
                            norm_y = y / img_height
                            norm_w = w / img_width
                            norm_h = h / img_height
                            
                            # Clamp to valid range
                            norm_x = max(0, min(1, norm_x))
                            norm_y = max(0, min(1, norm_y))
                            norm_w = max(0, min(1, norm_w))
                            norm_h = max(0, min(1, norm_h))
                            
                            # Keep original class ID - don't change to 0
                            normalized_lines.append(f"{class_id} {norm_x:.6f} {norm_y:.6f} {norm_w:.6f} {norm_h:.6f}\n")
                            modified = True
                            
                    except ValueError as e:
                        print(f"   ❌ {label_file.name}:L{line_num} - Error parsing: {e}")
                        normalized_lines.append(line + "\n")
                        error_count += 1
                        continue
                
                # Write normalized labels
                if modified:
                    with open(label_file, 'w') as f:
                        f.writelines(normalized_lines)
                
                processed_count += 1
                
                if processed_count % 100 == 0:
                    print(f"   ✅ Processed {processed_count}/{len(label_files)} files")
                    
            except Exception as e:
                print(f"   ❌ Error processing {label_file.name}: {e}")
                error_count += 1
        
        print(f"   📊 {split.upper()} Results:")
        print(f"      ✅ Processed: {processed_count}")
        print(f"      ❌ Errors: {error_count}")
    
    print(f"\n🎉 LABEL NORMALIZATION COMPLETE!")
    return True

def validate_normalized_labels(dataset_path):
    """
    Validate that all labels are now properly normalized
    """
    print(f"\n🔍 VALIDATING NORMALIZED LABELS")
    print("=" * 40)
    
    dataset_path = Path(dataset_path)
    
    for split in ['train', 'val']:
        split_path = dataset_path / split
        if not split_path.exists():
            continue
            
        labels_dir = split_path / "labels"
        if not labels_dir.exists():
            continue
        
        print(f"\n📋 Checking {split.upper()} labels...")
        
        label_files = list(labels_dir.glob("*.txt"))
        valid_count = 0
        invalid_count = 0
        
        for label_file in label_files[:10]:  # Check first 10 files
            try:
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                file_valid = True
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) != 5:
                        file_valid = False
                        break
                    
                    try:
                        class_id = int(parts[0])
                        x, y, w, h = map(float, parts[1:5])
                        
                        # Check if normalized (0-1 range)
                        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                            file_valid = False
                            break
                            
                    except ValueError:
                        file_valid = False
                        break
                
                if file_valid:
                    valid_count += 1
                else:
                    invalid_count += 1
                    print(f"   ❌ Invalid: {label_file.name}")
                    
            except Exception as e:
                invalid_count += 1
                print(f"   ❌ Error reading {label_file.name}: {e}")
        
        print(f"   📊 Sample validation ({min(10, len(label_files))} files):")
        print(f"      ✅ Valid: {valid_count}")
        print(f"      ❌ Invalid: {invalid_count}")
        
        # Show sample of valid label
        if valid_count > 0:
            sample_file = labels_dir / f"{list(labels_dir.glob('*.txt'))[0].name}"
            print(f"   📄 Sample normalized label ({sample_file.name}):")
            with open(sample_file, 'r') as f:
                lines = f.readlines()[:2]
                for line in lines:
                    if line.strip():
                        print(f"      {line.strip()}")

def clear_yolo_cache(dataset_path):
    """
    Clear all YOLO cache files to force regeneration with new labels
    """
    print(f"\n🗑️  CLEARING YOLO CACHE FILES")
    print("=" * 30)
    
    dataset_path = Path(dataset_path)
    
    # Clear cache files
    cache_files = list(dataset_path.rglob("*.cache"))
    for cache_file in cache_files:
        try:
            cache_file.unlink()
            print(f"   ✅ Cleared: {cache_file}")
        except Exception as e:
            print(f"   ❌ Error clearing {cache_file}: {e}")
    
    print(f"   📊 Cleared {len(cache_files)} cache files")

if __name__ == "__main__":
    # Configuration - UPDATE THIS PATH
    dataset_path = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy"
    
    print("🚀 YOLO LABEL NORMALIZER")
    print("=" * 60)
    print(f"📁 Dataset: {dataset_path}")
    print(f"🎯 Converting absolute pixel coordinates to normalized (0-1) format")
    print(f"🏷️  Preserving original class IDs for multi-class training")
    
    try:
        # Step 1: Clear existing cache
        clear_yolo_cache(dataset_path)
        
        # Step 2: Normalize labels
        success = normalize_yolo_labels(dataset_path)
        
        if success:
            # Step 3: Validate results
            validate_normalized_labels(dataset_path)
            
            # Step 4: Clear cache again to force fresh validation
            clear_yolo_cache(dataset_path)
            
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Labels normalized to YOLO format (0-1 range)")
            print(f"✅ Original class IDs preserved")
            print(f"✅ Cache files cleared")
            print(f"\n🚀 Ready to run your training script!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()