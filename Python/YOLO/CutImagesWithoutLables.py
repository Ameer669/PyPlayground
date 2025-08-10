import os
import shutil
from pathlib import Path

def get_file_stems(directory, extensions):
    """Get file stems (names without extensions) from directory"""
    stems = set()
    if os.path.exists(directory):
        for file_path in Path(directory).iterdir():
            if file_path.suffix.lower() in extensions:
                stems.add(file_path.stem)
    return stems

def cut_unlabeled_images():
    # Configuration
    images_folder = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\train\images"
    labels_folder = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\train\labels"
    output_folder = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\train\unlabeled_images"
    
    # Supported file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    label_extensions = {'.txt'}
    
    print("🔍 FINDING IMAGES WITHOUT LABELS")
    print("="*50)
    
    # Validate input directories
    if not os.path.exists(images_folder):
        print(f"❌ Images folder not found: {images_folder}")
        return
    
    if not os.path.exists(labels_folder):
        print(f"❌ Labels folder not found: {labels_folder}")
        return
    
    # Create output directory
    os.makedirs(output_folder, exist_ok=True)
    print(f"📁 Created output folder: {output_folder}")
    
    # Get all image and label file stems
    print(f"\n📸 Scanning images in: {images_folder}")
    image_stems = get_file_stems(images_folder, image_extensions)
    print(f"   Found {len(image_stems)} image files")
    
    print(f"\n🏷️  Scanning labels in: {labels_folder}")
    label_stems = get_file_stems(labels_folder, label_extensions)
    print(f"   Found {len(label_stems)} label files")
    
    # Find images without corresponding labels
    unlabeled_stems = image_stems - label_stems
    labeled_stems = image_stems & label_stems
    
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"   ✅ Images with labels: {len(labeled_stems)}")
    print(f"   ❌ Images without labels: {len(unlabeled_stems)}")
    print(f"   📈 Label coverage: {(len(labeled_stems)/len(image_stems)*100):.1f}%")
    
    if not unlabeled_stems:
        print(f"\n🎉 All images have corresponding labels! Nothing to cut.")
        return
    
    # Show which images will be moved
    print(f"\n📋 IMAGES TO BE MOVED ({len(unlabeled_stems)}):")
    for i, stem in enumerate(sorted(unlabeled_stems), 1):
        print(f"   {i:3d}. {stem}")
        if i == 10 and len(unlabeled_stems) > 10:
            print(f"   ... and {len(unlabeled_stems) - 10} more")
            break
    
    # Confirm action
    confirm = input(f"\n❓ Move {len(unlabeled_stems)} images to '{output_folder}'? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("🛑 Operation cancelled.")
        return
    
    # Move unlabeled images
    print(f"\n✂️  CUTTING UNLABELED IMAGES...")
    moved_count = 0
    failed_moves = []
    
    for stem in unlabeled_stems:
        # Find the actual image file (could have different extensions)
        source_file = None
        for ext in image_extensions:
            potential_path = os.path.join(images_folder, f"{stem}{ext}")
            if os.path.exists(potential_path):
                source_file = potential_path
                break
        
        if source_file:
            try:
                # Determine destination path
                file_ext = Path(source_file).suffix
                dest_file = os.path.join(output_folder, f"{stem}{file_ext}")
                
                # Move file (cut)
                shutil.move(source_file, dest_file)
                moved_count += 1
                print(f"   ✂️  Moved: {stem}{file_ext}")
                
            except Exception as e:
                failed_moves.append((stem, str(e)))
                print(f"   ❌ Failed to move {stem}: {e}")
        else:
            failed_moves.append((stem, "File not found"))
            print(f"   ⚠️  File not found: {stem}")
    
    # Final report
    print(f"\n" + "="*50)
    print(f"📊 FINAL REPORT")
    print(f"="*50)
    print(f"✅ Successfully moved: {moved_count}/{len(unlabeled_stems)} images")
    print(f"📁 Moved to: {output_folder}")
    
    if failed_moves:
        print(f"\n❌ FAILED MOVES ({len(failed_moves)}):")
        for stem, error in failed_moves:
            print(f"   - {stem}: {error}")
    
    # Show updated statistics
    remaining_images = len(image_stems) - moved_count
    if remaining_images > 0:
        coverage = (len(labeled_stems) / remaining_images) * 100
        print(f"\n📈 UPDATED STATISTICS:")
        print(f"   Images remaining in source: {remaining_images}")
        print(f"   Images with labels: {len(labeled_stems)}")
        print(f"   Label coverage: {coverage:.1f}%")
    
    print(f"\n🎯 Operation completed!")

def restore_unlabeled_images():
    """Optional function to restore moved images back to original folder"""
    images_folder = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\test\images"
    output_folder = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\test\unlabeled_images"
    
    if not os.path.exists(output_folder):
        print(f"❌ Unlabeled images folder not found: {output_folder}")
        return
    
    unlabeled_files = list(Path(output_folder).iterdir())
    if not unlabeled_files:
        print(f"📁 No files to restore in: {output_folder}")
        return
    
    print(f"🔄 RESTORE UNLABELED IMAGES")
    print(f"Found {len(unlabeled_files)} files to restore")
    
    confirm = input(f"❓ Restore all files back to '{images_folder}'? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("🛑 Restore cancelled.")
        return
    
    restored_count = 0
    for file_path in unlabeled_files:
        try:
            dest_path = os.path.join(images_folder, file_path.name)
            shutil.move(str(file_path), dest_path)
            restored_count += 1
            print(f"   🔄 Restored: {file_path.name}")
        except Exception as e:
            print(f"   ❌ Failed to restore {file_path.name}: {e}")
    
    print(f"\n✅ Restored {restored_count}/{len(unlabeled_files)} files")

if __name__ == "__main__":
    print("📂 IMAGE-LABEL MATCHING TOOL")
    print("="*50)
    print("1. Cut unlabeled images")
    print("2. Restore unlabeled images")
    
    choice = input("\nSelect option (1/2): ").strip()
    
    if choice == "1":
        cut_unlabeled_images()
    elif choice == "2":
        restore_unlabeled_images()
    else:
        print("❌ Invalid choice. Running cut operation by default...")
        cut_unlabeled_images()