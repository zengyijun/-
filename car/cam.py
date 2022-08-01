import time
import sys
import cv2
from flask import Flask, render_template, Response
from object_detector import ObjectDetector
from object_detector import ObjectDetectorOptions
import threading
import utils
import log

outputFrame = None
lock = threading.Lock()
cap = cv2.VideoCapture(-1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


app = Flask(__name__)
# 装饰器，指示本页面的初始界面
@app.route("/")
def index():
  return render_template("index.html")

# 初始化摄像头，启动帧生成线程和服务器线程
def init_cam(type):
  t = None
  if type == "with_detect":
    t = threading.Thread(target=run_detect, args=("efficientdet_lite0.tflite", 2))
    t.daemon = True
  elif type == "normal":
    t = threading.Thread(target=cam)
    t.daemon = True
  t.start()
  app.run(host= "0.0.0.0", port = 5000,debug=True, threaded=True, use_reloader=False)


def cam():
  global outputFrame, lock, cap
  i = 0
  while True:
    # 不断地获取图像
    success, frame = cap.read()
    if not success:
      print("error")
      continue
    with lock:
      outputFrame = frame.copy()

def run_detect(model: str, num_threads: int) -> None:
  global outputFrame, lock, cap
  # Variables to calculate FPS
  counter, fps = 0, 0
  start_time = time.time()
  # Visualization parameters
  row_size = 20  # pixels
  left_margin = 24  # pixels
  text_color = (0, 0, 255)  # red
  font_size = 1
  font_thickness = 1
  fps_avg_frame_count = 10
  # Initialize the object detection model
  options = ObjectDetectorOptions(
      num_threads=num_threads,
      score_threshold=0.3,
      max_results=3,
      enable_edgetpu=False)
  detector = ObjectDetector(model_path=model, options=options)
  # Continuously capture images from the camera and run inference
  while True:
    success, image = cap.read()
    if not success:
      continue
    counter += 1
    image = cv2.flip(image, 1)# 对图片进行水平翻转
    # Run object detection estimation using the model.
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    detections = detector.detect(rgb_image)
    # Draw keypoints and edges on input image（框出识别到的物体并在上面标记出其名称）
    image = utils.visualize(image, detections)
    # Calculate the FPS
    if counter % fps_avg_frame_count == 0:
      end_time = time.time()
      fps = fps_avg_frame_count / (end_time - start_time)
      start_time = time.time()
    # Show the FPS
    fps_text = 'FPS = {:.1f}'.format(fps)
    text_location = (left_margin, row_size)
    cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                font_size, text_color, font_thickness)
    # 用于在网页输出
    with lock:
      outputFrame = image.copy()

def generate():
  global outputFrame, lock
  while True:
    with lock:
      if outputFrame is None:
        continue
      (success, images) = cv2.imencode(".jpg", outputFrame)
      if not success:
        continue
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n'+bytearray(images) + b'\r\n')
    
@app.route("/video_feed")
def video_feed():
  return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")
