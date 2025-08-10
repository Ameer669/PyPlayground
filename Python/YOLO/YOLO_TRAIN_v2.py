from ultralytics import YOLO
import torch
import shutil
import os
import time
import yaml
import json
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime
import cv2
import numpy as np

class OptimizedYOLOTrainer:
    def __init__(self, base_model_path, project_root, target_class=None):
        self.base_model_path = base_model_path
        self.project_root = Path(project_root)
        self.target_class = target_class
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Setup directories with class-specific naming
        class_suffix = f"_{self.target_class}" if self.target_class else ""
        self.runs_dir = self.project_root / "runs" / "detect"
        self.models_dir = self.project_root / "models" / f"class_models{class_suffix}"
        self.reports_dir = self.project_root / "reports" / f"class_reports{class_suffix}"
        
        for dir_path in [self.runs_dir, self.models_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Device optimization
        self.device = self._setup_device()
        
        # Training statistics with class info
        self.training_stats = {
            'target_class': self.target_class,
            'start_time': None,
            'end_time': None,
            'total_time': None,
            'best_metrics': {},
            'final_metrics': {},
            'model_size': None,
            'epochs_completed': 0,
            'class_distribution': {}
        }
    
    def _setup_device(self):
        """Setup optimal device configuration"""
        if torch.cuda.is_available():
            device = 'cuda'
            gpu_name = torch.cuda.get_device_name()
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"🚀 GPU: {gpu_name} ({gpu_memory:.1f}GB)")
            
            # Clear GPU cache
            torch.cuda.empty_cache()
            
            # Enable optimizations
            torch.backends.cudnn.benchmark = True
            print("⚡ CUDA optimizations enabled")
        else:
            device = 'cpu'
            print("💻 Using CPU (consider GPU for faster training)")
        
        return device
    
    def _validate_dataset_structure(self, data_config):
        """Comprehensive dataset structure validation and fixing"""
        print(f"🔍 COMPREHENSIVE DATASET VALIDATION")
        print("-" * 40)
        
        issues_found = []
        fixes_applied = []
        
        # Get paths from config
        train_images_path = Path(data_config['train']).parent / "images"
        train_labels_path = Path(data_config['train']).parent / "labels"
        
        val_images_path = None
        val_labels_path = None
        if 'val' in data_config:
            val_images_path = Path(data_config['val']).parent / "images"
            val_labels_path = Path(data_config['val']).parent / "labels"
        
        print(f"📁 Train images: {train_images_path}")
        print(f"📁 Train labels: {train_labels_path}")
        if val_images_path:
            print(f"📁 Val images: {val_images_path}")
            print(f"📁 Val labels: {val_labels_path}")
        
        # Check directory existence
        if not train_images_path.exists():
            issues_found.append(f"Training images directory missing: {train_images_path}")
        if not train_labels_path.exists():
            issues_found.append(f"Training labels directory missing: {train_labels_path}")
            train_labels_path.mkdir(parents=True, exist_ok=True)
            fixes_applied.append(f"Created missing labels directory: {train_labels_path}")
        
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        train_images = [f for f in train_images_path.glob("*") if f.suffix.lower() in image_extensions] if train_images_path.exists() else []
        
        if not train_images:
            issues_found.append(f"No valid images found in: {train_images_path}")
            return issues_found, fixes_applied, 0, 0
        
        # Check image-label matching
        print(f"🔍 Checking {len(train_images)} training images...")
        valid_pairs = 0
        invalid_labels = []
        missing_labels = []
        
        for img_file in train_images:
            label_file = train_labels_path / f"{img_file.stem}.txt"
            
            if not label_file.exists():
                missing_labels.append(img_file.name)
                continue
            
            # Validate label format
            try:
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                valid_label = True
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) != 5:
                        invalid_labels.append(f"{label_file.name}:L{line_num} - Expected 5 values, got {len(parts)}")
                        valid_label = False
                        continue
                    
                    # Check if all parts are numbers
                    try:
                        class_id = int(parts[0])
                        x, y, w, h = map(float, parts[1:5])
                        
                        # Check if values are in valid ranges
                        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                            invalid_labels.append(f"{label_file.name}:L{line_num} - Coordinates out of range [0,1]")
                            valid_label = False
                        
                        if class_id >= data_config['nc']:
                            invalid_labels.append(f"{label_file.name}:L{line_num} - Class ID {class_id} >= num_classes {data_config['nc']}")
                            valid_label = False
                            
                    except ValueError:
                        invalid_labels.append(f"{label_file.name}:L{line_num} - Non-numeric values")
                        valid_label = False
                
                if valid_label:
                    valid_pairs += 1
                    
            except Exception as e:
                invalid_labels.append(f"{label_file.name} - Error reading file: {e}")
        
        # Report findings
        print(f"✅ Valid image-label pairs: {valid_pairs}")
        print(f"❌ Images missing labels: {len(missing_labels)}")
        print(f"❌ Invalid label files: {len(invalid_labels)}")
        
        if missing_labels:
            issues_found.append(f"{len(missing_labels)} images missing labels")
            print("📋 Missing labels (first 10):")
            for img in missing_labels[:10]:
                print(f"   - {img}")
            if len(missing_labels) > 10:
                print(f"   ... and {len(missing_labels) - 10} more")
        
        if invalid_labels:
            issues_found.append(f"{len(invalid_labels)} invalid label entries")
            print("📋 Invalid labels (first 10):")
            for error in invalid_labels[:10]:
                print(f"   - {error}")
            if len(invalid_labels) > 10:
                print(f"   ... and {len(invalid_labels) - 10} more")
        
        return issues_found, fixes_applied, valid_pairs, len(train_images)
    
    def _fix_dataset_issues(self, data_yaml_path):
        """Attempt to fix common dataset issues"""
        print(f"\n🔧 ATTEMPTING TO FIX DATASET ISSUES")
        print("-" * 40)
        
        # Clear any existing cache files
        cache_files = list(Path(data_yaml_path).parent.rglob("*.cache"))
        for cache_file in cache_files:
            try:
                cache_file.unlink()
                print(f"🗑️  Cleared cache: {cache_file}")
            except:
                pass
        
        # Try to create missing validation split if not exists
        with open(data_yaml_path, 'r') as f:
            data_config = yaml.safe_load(f)
        
        if 'val' not in data_config:
            train_path = Path(data_config['train']).parent
            val_path = train_path.parent / "val"
            
            if not val_path.exists():
                # Create validation split from training data
                print("📁 Creating validation split from training data...")
                val_images = val_path / "images"
                val_labels = val_path / "labels"
                val_images.mkdir(parents=True, exist_ok=True)
                val_labels.mkdir(parents=True, exist_ok=True)
                
                # Move 20% of training data to validation
                train_images = list((train_path / "images").glob("*"))
                val_count = max(1, len(train_images) // 5)  # 20% for validation
                
                import random
                random.shuffle(train_images)
                val_images_to_move = train_images[:val_count]
                
                for img_file in val_images_to_move:
                    # Move image
                    shutil.move(str(img_file), str(val_images / img_file.name))
                    
                    # Move corresponding label if exists
                    label_file = train_path / "labels" / f"{img_file.stem}.txt"
                    if label_file.exists():
                        shutil.move(str(label_file), str(val_labels / label_file.name))
                
                # Update data.yaml
                data_config['val'] = str(val_path / "labels")
                with open(data_yaml_path, 'w') as f:
                    yaml.dump(data_config, f, default_flow_style=False)
                
                print(f"✅ Created validation split with {val_count} images")
        
        return data_config
    
    def _validate_data_yaml(self, data_yaml_path):
        """Validate and analyze data.yaml"""
        print(f"📋 VALIDATING DATA CONFIGURATION")
        print("=" * 50)
        
        if not os.path.exists(data_yaml_path):
            raise FileNotFoundError(f"Data YAML not found: {data_yaml_path}")
        
        with open(data_yaml_path, 'r') as f:
            data_config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['train', 'nc', 'names']
        for field in required_fields:
            if field not in data_config:
                raise ValueError(f"Missing required field in data.yaml: {field}")
        
        print(f"📄 Data YAML content:")
        for key, value in data_config.items():
            print(f"   {key}: {value}")
        
        # Comprehensive dataset validation
        issues_found, fixes_applied, valid_pairs, total_images = self._validate_dataset_structure(data_config)
        
        # If issues found, attempt fixes
        if issues_found:
            print(f"\n⚠️  ISSUES FOUND: {len(issues_found)}")
            for issue in issues_found:
                print(f"   - {issue}")
            
            fix_choice = input(f"\n🔧 Attempt to fix dataset issues? (y/n): ").strip().lower()
            if fix_choice == 'y':
                data_config = self._fix_dataset_issues(data_yaml_path)
                # Re-validate after fixes
                issues_found, fixes_applied, valid_pairs, total_images = self._validate_dataset_structure(data_config)
        
        if valid_pairs == 0:
            raise RuntimeError(f"No valid image-label pairs found! Please check your dataset structure.")
        
        # Final validation counts
        train_path = Path(data_config['train']).parent / "images"
        val_path = Path(data_config['val']).parent / "images" if 'val' in data_config else None
        
        train_count = len([f for f in train_path.glob("*") if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}]) if train_path.exists() else 0
        val_count = len([f for f in val_path.glob("*") if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}]) if val_path and val_path.exists() else 0
        
        print(f"\n✅ FINAL VALIDATION RESULTS:")
        print(f"   📸 Training images: {train_count}")
        print(f"   📸 Validation images: {val_count}")
        print(f"   🏷️  Classes: {data_config['nc']} {data_config['names']}")
        print(f"   ✅ Valid pairs: {valid_pairs}")
        
        # Store class distribution info
        self.training_stats['class_distribution'] = {
            'total_classes': data_config['nc'],
            'class_names': data_config['names'],
            'target_class': self.target_class,
            'train_images': train_count,
            'val_images': val_count,
            'valid_pairs': valid_pairs
        }
        
        # Validate target class
        if self.target_class and self.target_class not in data_config['names']:
            print(f"⚠️  Warning: Target class '{self.target_class}' not found in class names!")
        elif self.target_class:
            class_index = data_config['names'].index(self.target_class)
            print(f"🎯 Training specifically for class: '{self.target_class}' (index: {class_index})")
        
        return data_config, train_count, val_count
    
    def _calculate_optimal_settings(self, train_count, gpu_memory_gb=None):
        """Calculate optimal training settings based on dataset size and hardware"""
        if gpu_memory_gb is None and torch.cuda.is_available():
            gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        # Optimal batch size based on GPU memory and dataset size
        if gpu_memory_gb and gpu_memory_gb >= 8:
            batch_size = min(32, max(4, train_count // 100))
        elif gpu_memory_gb and gpu_memory_gb >= 4:
            batch_size = min(16, max(4, train_count // 150))
        else:
            batch_size = min(8, max(2, train_count // 200))
        
        # Optimal epochs based on dataset size
        if train_count > 5000:
            epochs = 100
        elif train_count > 1000:
            epochs = 150
        else:
            epochs = 200
        
        # Learning rate based on batch size
        lr0 = 0.01 * (batch_size / 16)  # Scale with batch size
        
        # Image size optimization
        imgsz = 640 if gpu_memory_gb and gpu_memory_gb >= 6 else 416
        
        settings = {
            'batch': batch_size,
            'epochs': epochs,
            'lr0': lr0,
            'imgsz': imgsz
        }
        
        print(f"⚙️  Optimized settings:")
        for key, value in settings.items():
            print(f"   {key}: {value}")
        
        return settings
    
    def train_model(self, data_yaml_path, custom_settings=None):
        """Train model with optimizations"""
        class_info = f" for class '{self.target_class}'" if self.target_class else ""
        print(f"🎯 STARTING OPTIMIZED YOLO FINE-TUNING{class_info}")
        print("="*60)
        
        # Validate data
        data_config, train_count, val_count = self._validate_data_yaml(data_yaml_path)
        
        # Calculate optimal settings
        optimal_settings = self._calculate_optimal_settings(train_count)
        
        # Override with custom settings if provided
        if custom_settings:
            optimal_settings.update(custom_settings)
            print(f"🔧 Applied custom settings: {custom_settings}")
        
        # Load model
        print(f"📥 Loading base model: {self.base_model_path}")
        model = YOLO(self.base_model_path)
        
        # Training configuration
        train_config = {
            'data': str(data_yaml_path),
            'epochs': optimal_settings['epochs'],
            'imgsz': optimal_settings['imgsz'],
            'batch': optimal_settings['batch'],
            'lr0': optimal_settings['lr0'],
            'pretrained': True,
            'optimizer': 'AdamW',  # Better than SGD for fine-tuning
            'close_mosaic': 10,  # Disable mosaic in last 10 epochs
            'mixup': 0.1,  # Data augmentation
            'copy_paste': 0.1,  # Advanced augmentation
            'device': self.device,
            'workers': min(8, os.cpu_count()),  # Optimal data loading
            'exist_ok': True,
            'name': f"finetune_{self.target_class}_{self.timestamp}" if self.target_class else f"finetune_{self.timestamp}",
            'project': str(self.runs_dir),
            'save_period': 10,  # Save checkpoint every 10 epochs
            'patience': 30,  # Early stopping patience
            'save': True,
            'plots': True
        }
        
        print(f"🚀 Training configuration:")
        for key, value in train_config.items():
            if key not in ['data']:  # Don't print long paths
                print(f"   {key}: {value}")
        
        # Start training
        self.training_stats['start_time'] = time.time()
        print(f"\n⏰ Training started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            results = model.train(**train_config)
            
            self.training_stats['end_time'] = time.time()
            self.training_stats['total_time'] = self.training_stats['end_time'] - self.training_stats['start_time']
            self.training_stats['epochs_completed'] = train_config['epochs']
            
            # Extract metrics
            if hasattr(results, 'results_dict'):
                self.training_stats['final_metrics'] = results.results_dict
            
            print(f"✅ Training completed in {self.training_stats['total_time']/3600:.2f} hours")
            
            return results, train_config['name']
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            self.training_stats['end_time'] = time.time()
            self.training_stats['total_time'] = self.training_stats['end_time'] - self.training_stats['start_time']
            raise
    
    def save_best_model(self, run_name):
        """Save and organize the best model"""
        print(f"\n📦 Saving best model...")
        
        # Source paths
        run_dir = self.runs_dir / run_name
        best_weights = run_dir / "weights" / "best.pt"
        last_weights = run_dir / "weights" / "last.pt"
        
        if not best_weights.exists():
            print(f"❌ Best weights not found: {best_weights}")
            return None
        
        # Destination path with class name
        class_suffix = f"_{self.target_class}" if self.target_class else ""
        model_name = f"finetuned{class_suffix}_{self.timestamp}.pt"
        dst_path = self.models_dir / model_name
        
        # Copy best model
        shutil.copy2(best_weights, dst_path)
        
        # Get model size
        model_size_mb = dst_path.stat().st_size / (1024 * 1024)
        self.training_stats['model_size'] = model_size_mb
        
        print(f"✅ Best model saved: {dst_path}")
        print(f"📊 Model size: {model_size_mb:.2f} MB")
        
        return dst_path
    
    def test_model(self, model_path, test_images_dir, conf_threshold=0.35):
        """Test the fine-tuned model"""
        class_info = f" for class '{self.target_class}'" if self.target_class else ""
        print(f"\n🧪 TESTING FINE-TUNED MODEL{class_info}")
        print("="*40)
        
        if not os.path.exists(test_images_dir):
            print(f"❌ Test images directory not found: {test_images_dir}")
            return None
        
        # Count test images
        test_images = list(Path(test_images_dir).glob("*"))
        test_count = len([f for f in test_images if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}])
        
        print(f"📸 Testing on {test_count} images")
        print(f"🎯 Confidence threshold: {conf_threshold}")
        
        # Load model and run inference
        model = YOLO(model_path)
        
        test_start = time.time()
        
        results = model.predict(
            source=test_images_dir,
            conf=conf_threshold,
            save=True,
            show=False,
            project=str(self.runs_dir),
            name=f"test_{self.target_class}_{self.timestamp}" if self.target_class else f"test_{self.timestamp}",
            device=self.device,
            verbose=False
        )
        
        test_time = time.time() - test_start
        
        # Analyze results
        total_detections = sum(len(r.boxes) if r.boxes is not None else 0 for r in results)
        images_with_detections = sum(1 for r in results if r.boxes is not None and len(r.boxes) > 0)
        
        detection_rate = (images_with_detections / test_count) * 100 if test_count > 0 else 0
        avg_detections_per_image = total_detections / test_count if test_count > 0 else 0
        inference_speed = test_count / test_time if test_time > 0 else 0
        
        test_stats = {
            'test_images': test_count,
            'images_with_detections': images_with_detections,
            'total_detections': total_detections,
            'detection_rate': detection_rate,
            'avg_detections_per_image': avg_detections_per_image,
            'inference_time': test_time,
            'inference_speed': inference_speed
        }
        
        print(f"📊 Test Results:")
        print(f"   Detection rate: {detection_rate:.1f}%")
        print(f"   Total detections: {total_detections}")
        print(f"   Avg detections/image: {avg_detections_per_image:.2f}")
        print(f"   Inference speed: {inference_speed:.1f} images/sec")
        
        return test_stats, results
    
    def generate_comprehensive_report(self, test_stats=None):
        """Generate comprehensive training and testing report"""
        print(f"\n📊 GENERATING COMPREHENSIVE REPORT")
        print("="*50)
        
        # Prepare report data
        report_data = {
            'timestamp': self.timestamp,
            'training_stats': self.training_stats,
            'test_stats': test_stats,
            'system_info': {
                'device': self.device,
                'pytorch_version': torch.__version__,
                'cuda_available': torch.cuda.is_available()
            }
        }
        
        if torch.cuda.is_available():
            report_data['system_info']['gpu_name'] = torch.cuda.get_device_name()
            report_data['system_info']['gpu_memory_gb'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        # Save JSON report with class-specific naming
        class_suffix = f"_{self.target_class}" if self.target_class else ""
        json_report_path = self.reports_dir / f"training_report{class_suffix}_{self.timestamp}.json"
        with open(json_report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        # Generate text report with class-specific naming
        txt_report_path = self.reports_dir / f"training_report{class_suffix}_{self.timestamp}.txt"
        
        with open(txt_report_path, 'w') as f:
            class_title = f" - {self.target_class.upper()}" if self.target_class else ""
            
            # 1. Define the report file path FIRST
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"comprehensive_report_{timestamp}.txt"
    
            # 2. Then open and write to the file
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"🎯 YOLO FINE-TUNING COMPREHENSIVE REPORT{class_title}\n")
                
            f.write("="*60 + "\n\n")
            
            f.write(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"🆔 Session ID: {self.timestamp}\n")
            if self.target_class:
                f.write(f"🎯 Target Class: {self.target_class}\n")
            f.write("\n")
            
            # System Information
            f.write("💻 SYSTEM INFORMATION\n")
            f.write("-" * 30 + "\n")
            f.write(f"Device: {self.device}\n")
            f.write(f"PyTorch Version: {torch.__version__}\n")
            if torch.cuda.is_available():
                f.write(f"GPU: {torch.cuda.get_device_name()}\n")
                f.write(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB\n")
            f.write("\n")
            
            # Class-specific information
            if 'class_distribution' in self.training_stats:
                f.write("🏷️  CLASS INFORMATION\n")
                f.write("-" * 30 + "\n")
                cd = self.training_stats['class_distribution']
                f.write(f"Target Class: {cd.get('target_class', 'All classes')}\n")
                f.write(f"Total Classes: {cd.get('total_classes', 'Unknown')}\n")
                f.write(f"Class Names: {cd.get('class_names', 'Unknown')}\n")
                f.write(f"Training Images: {cd.get('train_images', 'Unknown')}\n")
                f.write(f"Validation Images: {cd.get('val_images', 'Unknown')}\n")
                f.write("\n")
            
            # Training Statistics
            f.write("🏋️ TRAINING STATISTICS\n")
            f.write("-" * 30 + "\n")
            if self.training_stats['total_time']:
                f.write(f"Training Time: {self.training_stats['total_time']/3600:.2f} hours\n")
                f.write(f"Epochs Completed: {self.training_stats['epochs_completed']}\n")
                if self.training_stats['model_size']:
                    f.write(f"Final Model Size: {self.training_stats['model_size']:.2f} MB\n")
            f.write("\n")
            
            # Test Results
            if test_stats:
                f.write("🧪 TEST RESULTS\n")
                f.write("-" * 30 + "\n")
                f.write(f"Test Images: {test_stats['test_images']}\n")
                f.write(f"Detection Rate: {test_stats['detection_rate']:.1f}%\n")
                f.write(f"Total Detections: {test_stats['total_detections']}\n")
                f.write(f"Avg Detections/Image: {test_stats['avg_detections_per_image']:.2f}\n")
                f.write(f"Inference Speed: {test_stats['inference_speed']:.1f} images/sec\n")
                f.write("\n")
            
            # Performance Summary
            f.write("📈 PERFORMANCE SUMMARY\n")
            f.write("-" * 30 + "\n")
            if test_stats and self.training_stats['total_time']:
                f.write(f"Overall Success: {'✅ Excellent' if test_stats['detection_rate'] > 90 else '🔄 Needs Improvement'}\n")
                f.write(f"Training Efficiency: {test_stats['test_images']/(self.training_stats['total_time']/3600):.1f} test_images per training hour\n")
        
        print(f"📊 Reports saved:")
        print(f"   JSON: {json_report_path}")
        print(f"   Text: {txt_report_path}")
        
        return json_report_path, txt_report_path

def quick_dataset_check(data_yaml_path):
    """Quick dataset structure checker - run this first!"""
    print("🔍 QUICK DATASET STRUCTURE CHECK")
    print("="*50)
    
    if not os.path.exists(data_yaml_path):
        print(f"❌ Data YAML not found: {data_yaml_path}")
        return False
    
    with open(data_yaml_path, 'r') as f:
        data_config = yaml.safe_load(f)
    
    print(f"📄 Data YAML content:")
    for key, value in data_config.items():
        print(f"   {key}: {value}")
    
    # Check directory structure
    base_path = Path(data_yaml_path).parent
    expected_structure = {
        'train/images': base_path / "train" / "images",
        'train/labels': base_path / "train" / "labels",
        'val/images': base_path / "val" / "images" if 'val' in data_config else None,
        'val/labels': base_path / "val" / "labels" if 'val' in data_config else None,
    }
    
    print(f"\n📁 Directory structure check:")
    all_good = True
    for name, path in expected_structure.items():
        if path is None:
            continue
        if path.exists():
            count = len([f for f in path.glob("*") if f.suffix.lower() in {'.jpg', '.png', '.txt'}])
            print(f"   ✅ {name}: {count} files")
        else:
            print(f"   ❌ {name}: MISSING")
            all_good = False
    
    # Quick label format check
    train_labels = base_path / "train" / "labels"
    if train_labels.exists():
        label_files = list(train_labels.glob("*.txt"))
        if label_files:
            sample_label = label_files[0]
            print(f"\n📄 Sample label file: {sample_label.name}")
            try:
                with open(sample_label, 'r') as f:
                    lines = f.readlines()[:3]  # First 3 lines
                for i, line in enumerate(lines, 1):
                    parts = line.strip().split()
                    if len(parts) == 5:
                        print(f"   ✅ Line {i}: {line.strip()}")
                    else:
                        print(f"   ❌ Line {i}: {line.strip()} (Expected 5 values, got {len(parts)})")
                        all_good = False
            except Exception as e:
                print(f"   ❌ Error reading label file: {e}")
                all_good = False
    
    if all_good:
        print(f"\n🎉 Dataset structure looks good!")
    else:
        print(f"\n⚠️  Issues found - the training script will attempt to fix them")
    
    return all_good

def main():
    # Configuration
    base_model_path = r"D:\.IMLA\FacialExpression_yolov11\models\class_models_happy\finetuned_happy_20250726_153354.pt"
    project_root = r"D:\.IMLA\FacialExpression_yolov11"
    data_yaml_path = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\data.yaml"
    test_images_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\test\images"
    
    target_class = "happy"  # ['anger', 'fear', 'happy', 'neutral', 'sad']
    
    # 🔍 QUICK DATASET CHECK FIRST
    print("🚀 STEP 1: Quick Dataset Check")
    dataset_ok = quick_dataset_check(data_yaml_path)
    
    if not dataset_ok:
        continue_choice = input(f"\n❓ Dataset issues detected. Continue with training? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print("🛑 Training cancelled. Please fix dataset issues first.")
            return
    
    # Custom settings optimized for single-class training
    """custom_settings = None"""
    # In your main() function, replace custom_settings with:
    custom_settings = {
        'epochs': 7,           # Reduce from 120
        'batch': 32,            # Increase batch size
        'imgsz': 320,           # Image size (640,416,320)
        'cache': True,          # Cache images in RAM for faster loading
        'device': 0,            # Use specific GPU (if you have multiple)
        'workers': 8,           # Increase data loading workers
        'patience': 15,         # Reduce early stopping patience
        'save_period': 20,      # Save less frequently
        'val': False,           # Skip validation during training (validate at end)
        'plots': False,         # Disable plots during training
        'verbose': False,       # Reduce logging verbosity
        
        # Performance optimizations
        'amp': True,            # Enable Automatic Mixed Precision
        'fraction': 0.8,        # Use full dataset
        'profile': False,       # Disable profiling
        'overlap_mask': False,  # Disable if not needed
        'mask_ratio': 4,        # Reduce mask processing
        'dropout': 0.0,         # Disable dropout for speed
        'lr0': 0.01,           # Higher learning rate for faster convergence
        'warmup_epochs': 3,     # Reduce warmup
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'box': 7.5,            # Reduce box loss weight
        'cls': 0.5,            # Reduce classification loss weight
        'dfl': 1.5,            # Reduce DFL loss weight
        'pose': 12.0,          # Pose loss weight
        'kobj': 1.0,           # Keypoint objectness loss weight
        'label_smoothing': 0.0, # Disable label smoothing
        'nbs': 64,             # Nominal batch size
        'hsv_h': 0.015,        # Reduce augmentation
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 0.0,        # Disable rotation augmentation
        'translate': 0.1,      # Reduce translation augmentation
        'scale': 0.5,          # Reduce scaling augmentation
        'shear': 0.0,          # Disable shear augmentation
        'perspective': 0.0,    # Disable perspective augmentation
        'flipud': 0.0,         # Disable vertical flip
        'fliplr': 0.5,         # Keep horizontal flip
        'mosaic': 0.0,         # Disable mosaic augmentation
        'mixup': 0.0,          # Disable mixup
        'copy_paste': 0.0      # Disable copy-paste augmentation
    }
    
    try:
        print(f"\n🚀 STEP 2: Training Setup")
        print(f"🎯 TRAINING CLASS: {target_class.upper()}")
        print("="*60)
        
        # Initialize trainer with target class
        trainer = OptimizedYOLOTrainer(base_model_path, project_root, target_class)
        
        # Train model
        train_results, run_name = trainer.train_model(
            data_yaml_path, 
            custom_settings=custom_settings
        )
        
        # Save best model
        best_model_path = trainer.save_best_model(run_name)
        
        if best_model_path:
            # Test model
            test_stats, test_results = trainer.test_model(
                best_model_path, 
                test_images_dir,
                conf_threshold=0.35
            )
            
            # Generate comprehensive report
            json_report, txt_report = trainer.generate_comprehensive_report(test_stats)
            
            print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"📁 Best model: {best_model_path}")
            print(f"📊 Reports: {trainer.reports_dir}")
            
        else:
            print(f"❌ Failed to save model")
            
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()