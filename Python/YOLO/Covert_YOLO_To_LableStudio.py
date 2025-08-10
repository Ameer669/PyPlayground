import os
import json
from PIL import Image


images_dir = r"D:\Games\military vehicle.v6i.yolov8\train\images"      
labels_dir = r"D:\Games\military vehicle.v6i.yolov8\train\labels"      
output_file = "labelstudio_output.json"


label_name = "object"

output = []

for fname in os.listdir(labels_dir):
    if not fname.endswith(".txt"):
        continue

    img_name = fname.replace(".txt", ".jpg")  
    img_path = os.path.join(images_dir, img_name)
    label_path = os.path.join(labels_dir, fname)

    if not os.path.exists(img_path):
        print(f"Photos Not Found {img_path}")
        continue

    img = Image.open(img_path)
    width, height = img.size

    with open(label_path, "r") as f:
        lines = f.readlines()

    results = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue

        class_id, x_center, y_center, w, h = map(float, parts)

        x = (x_center - w / 2) * 100
        y = (y_center - h / 2) * 100
        width_percent = w * 100
        height_percent = h * 100

        results.append({
            "value": {
                "rectanglelabels": [label_name],
                "x": x,
                "y": y,
                "width": width_percent,
                "height": height_percent
            },
            "from_name": "label",
            "to_name": "image",
            "type": "rectanglelabels"
        })

    output.append({
        "data": {
            "image": f"/data/local-files/?d={os.path.join(images_dir, img_name)}"
        },
        "annotations": [{
            "result": results
        }]
    })

with open(output_file, "w") as out:
    json.dump(output, out, indent=4)

print(f"✅ Converted {len(output)} Image Photo: {output_file}")
