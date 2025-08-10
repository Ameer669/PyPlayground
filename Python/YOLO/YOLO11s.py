from ultralytics import YOLO
import os
import time
import cv2

model = YOLO(r"D:\.IMLA\FacialExpression_yolov11\yolov12s-face.pt")
image_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\test\images"
label_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\test\labels"
os.makedirs(label_dir, exist_ok=True)
failed_dir = r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\test\labels-n"
os.makedirs(failed_dir, exist_ok=True)

# Class ID ['anger', 'fear', 'happy', 'neutral', 'sad']
happy_id = 2

# Start timer
start_time = time.time()

# Prediction is used
results = model.predict(source=image_dir, conf=0.4, save=False)

total_images = len(results)
no_face_images = []

for r in results:
    name = os.path.splitext(os.path.basename(r.path))[0]
    label_path = os.path.join(label_dir, f"{name}.txt")

    if len(r.boxes) > 0:
        with open(label_path, "w") as f:
            for box in r.boxes:
                xywh = box.xywh[0].tolist()
                x, y, w, h = xywh
                f.write(f"{happy_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
        print(f"[✓] YOLO-labeled as happy: {name}")
    else:
        no_face_images.append(r.path)
        print(f"[✗] No face detected: {name}")


max_attempts = 18
conf_start = 0.4
conf_step = 0.02
failed_images = []

for img_path in no_face_images:
    name = os.path.splitext(os.path.basename(img_path))[0]
    label_path = os.path.join(label_dir, f"{name}.txt")

    attempt = 0
    detected = False
    conf = conf_start

    while not detected and attempt < max_attempts:
        retry_result = model.predict(source=img_path, conf=conf, save=False)[0]

        if len(retry_result.boxes) > 0:
            with open(label_path, "w") as f:
                for box in retry_result.boxes:
                    xywh = box.xywh[0].tolist()
                    x, y, w, h = xywh
                    f.write(f"{happy_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
            print(f"[✓] Recovered face for: {name} at conf={conf:.2f}")
            detected = True
        else:
            attempt += 1
            conf = max(0.05, conf - conf_step)
            print(f"[…] Retry {attempt} failed for: {name} | conf={conf:.2f}")

    if not detected:
        # Load the image
        img = cv2.imread(img_path)

        # Option 1: Save the entire image as "failed"
        failed_out_path = os.path.join(failed_dir, f"{name}.jpg")
        cv2.imwrite(failed_out_path, img)

        # Option 2: (if YOLO gave bad boxes and you want to crop center)
        # h, w, _ = img.shape
        # cropped = img[h//4:3*h//4, w//4:3*w//4]
        # cv2.imwrite(failed_out_path, cropped)

        failed_images.append(name)
        print(f"[🚫] Still failed after {max_attempts} attempts: {name}")


# End timer
end_time = time.time()
total_time = end_time - start_time
avg_time_ms = (total_time / total_images) * 1000 if total_images else 0

# Summary of failed images
if failed_images:
    print(f"\n🧨 Total failed images: {len(failed_images)}")
    print("🖼️ Failed image names:")
    for img_name in failed_images:
        print(f" - {img_name}")
else:
    print("\n🔥 All images successfully labeled!\n")
    
delete_failed = input("\n❓ Do you want to delete the failed images from 'images/' folder? (y/n): ").strip().lower()

if delete_failed == "y":
    for img_name in failed_images:
        original_path = os.path.join(image_dir, f"{img_name}.png")
        try:
            os.remove(original_path)
            print(f"🗑️ Deleted: {img_name}.png")
        except FileNotFoundError:
            print(f"⚠️ Not found: {img_name}.png")
        except Exception as e:
            print(f"❌ Error deleting {img_name}.png: {e}")
else:
    print("🛑 Skipped deletion. All failed images remain in 'images/' folder.")
    
print(f"\n✅ Done using YOLO-based face detection.")
print(f"🕒 Total time: {total_time:.2f} seconds")
print(f"📸 Avg per image: {avg_time_ms:.2f} ms\n")
