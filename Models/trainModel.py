from ultralytics import YOLO

# Load a pre-trained YOLOv8 Nano model
model = YOLO("yolov8n.pt")  # Or "yolov8s.pt", "yolov8m.pt", etc.

# Train the model
model.train(
    data="C:\\Documents\\GitHub\\Note-Detection\\ImagesForTraining\\data.yaml",  # Update this to the actual path
    epochs=50,
    patience=10,
    imgsz=640,
    batch=4,                 # Optional: adjust based on your GPU
    workers=0,                # Optional: number of dataloader workers
    device="cpu"              # Optional: set to 'cpu' or '0', '1', etc. for specific GPUs
) # set resume=True if you want to resume training from a previous checkpoint
