from ultralytics import YOLO
from rknn.api import RKNN

# Converts trained model to ONNX format
# model = YOLO("Models/BestModel.pt")
# model.export(format="onnx",opset=12, simplify=True)

# Paths
ONNX_MODEL = "Models/BestModel.onnx"
RKNN_MODEL_NAME = "Models/ReefV1-640-640-yolov8n.rknn" # TODO: Change this later to be the model name
DATASET_PATH = "Models/dataset.txt"

# Initialize RKNN object
rknn = RKNN(verbose=True)

# Configuration for RK3588. This is the main chip used with PhotonVision, which is used in most Orange Pis (citation needed)
rknn.config(
    target_platform="rk3588",
    mean_values=[[0, 0, 0]],
    std_values=[[255, 255, 255]],
    quantized_dtype="w8a8"
)

# Load ONNX model
ret = rknn.load_onnx(model=ONNX_MODEL)
if ret != 0:
    print("Failed to load ONNX model.")
    exit(ret)

# Build the RKNN model with quantization
ret = rknn.build(do_quantization=True, dataset=DATASET_PATH)
if ret != 0:
    print("Failed to build RKNN model.")
    exit(ret)

# Export the RKNN model
ret = rknn.export_rknn(RKNN_MODEL_NAME)
if ret != 0:
    print("Failed to export RKNN model.")
    exit(ret)
