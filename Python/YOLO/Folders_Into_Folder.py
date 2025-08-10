import os
import shutil


folders = [
    r"D:\.IMLA\archive\train\angry",
    r"D:\.IMLA\archive\train\fearful",
    r"D:\.IMLA\archive\train\happy",
    r"D:\.IMLA\archive\train\neutral",
    r"D:\.IMLA\archive\train\sad"
]

output = r"D:\.IMLA\archive\train\images"
os.makedirs(output, exist_ok=True)

extensions = ('.jpg', '.jpeg', '.png')

for folder in folders:
    for file in os.listdir(folder):
        if file.lower().endswith(extensions):
            src = os.path.join(folder, file)
            dst = os.path.join(output, file)
            if not os.path.exists(dst):
                shutil.copy(src, dst)

print("\n\n\n✅ Done.\n\n\n")
