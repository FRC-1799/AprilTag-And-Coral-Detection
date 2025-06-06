import rknn.api
rknn = rknn.api.RKNN()
rknn.load_rknn('/home/lidar/Documents/github/AprilTag-And-Coral-Detection/Models/ReefV1-640-640-yolov8n.rknn')
rknn.init_runtime(target="rk3588")
outputs = rknn.inference(inputs=["/home/lidar/Downloads/2025_REEFSCAPE.v1i.yolov8/train/images/frame_0140_jpg.rf.cb0558a3e566a5d74ac13cd0eb0e11f0.jpg"])
print(len(outputs))
print([o.shape for o in outputs])