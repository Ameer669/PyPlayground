from ultralytics import YOLO
import shutil

model = YOLO(r"D:\.IMLA\FacialExpression_yolov11\my_model.pt")

# Fine-Tuning (train,validate)
results = model.train(
    data=r"D:\.IMLA\FacialExpression_yolov11\archive\train\happy\data.yaml",
    #split="test",
    epochs=50,  
    imgsz=640,
    batch=8, 
    lr0=0.001,
    pretrained=True,
    name="finetune",
    project=r"D:\.IMLA\FacialExpression_yolov11\runs\detect"
)

src = r"D:\.IMLA\FacialExpression_yolov11\runs\detect\finetune\weights\best.pt"
dst = r"D:\.IMLA\FacialExpression_yolov11\my_model_finetuned.pt"
shutil.move(src, dst)

finetuned = YOLO(dst)
test_results = finetuned(
    source=r"D:\.IMLA\FacialExpression_yolov11\test\images",
    conf=0.35,
    show=False,
    save=True,
    project=r"D:\.IMLA\FacialExpression_yolov11\runs\detect",
    name="finetune-test"
)
