from ultralytics import YOLO
model = YOLO("Models/BestModel.pt")
model.export(format="onnx",opset=12, simplify=True)