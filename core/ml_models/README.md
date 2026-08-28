# Face detection / recognition models

These ONNX models come from [opencv/opencv_zoo](https://github.com/opencv/opencv_zoo)
(Apache License 2.0) and are loaded via OpenCV's `cv2.dnn`-based
`FaceDetectorYN` / `FaceRecognizerSF` APIs (available in `opencv-python` since
4.8.0, no `opencv-contrib-python` or separate ONNX runtime required).

- `face_detection_yunet_2023mar.onnx` - [YuNet](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet) face detector
- `face_recognition_sface_2021dec.onnx` - [SFace](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface) face embedding model

Both ship with prebuilt wheels for `opencv-python` on every actively
supported Python version (its wheels target the stable ABI, `cp37-abi3`, so
one wheel works from Python 3.7 through any newer 3.x release) - unlike the
`dlib`/`face_recognition` stack this replaced, nothing here needs a C/C++
compiler to install.
