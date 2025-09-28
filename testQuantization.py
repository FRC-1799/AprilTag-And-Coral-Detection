from ultralytics import YOLO
from rknn.api import RKNN


model = YOLO('Models/frcYolo11s_rknn_model/frcYolo11s.pt')

model.export(format='onnx', imgsz=640, dynamic=False, simplify=True, opset=12)

rknn = RKNN()
rknn.config(
    mean_values=[[0, 0, 0]],
    std_values=[[255, 255, 255]],
    target_platform='rk3588',
    quantized_dtype='w8a8',
)

ret = rknn.load_onnx(model='Models/frcYolo11s_rknn_model/frcYolo11s.onnx')
if ret != 0:
    print('Failed to load ONNX model')
    exit(ret)

ret = rknn.build(do_quantization=True, dataset="dataset.txt")
if ret != 0:
    print('Build failed')
    exit(ret)

ret = rknn.export_rknn('placeholderRknn.rknn')
if ret != 0:
    print('Export failed')
    exit(ret)

rknn.release()
print('✅ RKNN model exported successfully!')

