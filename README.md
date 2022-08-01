# raspberry pi物联小车控制程序

本程序实现了如下的功能：
1. 接收来自服务器的http post请求，并拆解其中的json数据，转到相应地代码执行
2. 控制小车的前进、后退、左转、右转
3. 实现打开摄像头，并通过一个流式传输的网页进行实时视频观看；摄像头本身具有物品检测的功能。此功能使用了[tensorflow lite官方](https://github.com/tensorflow/examples/tree/master/lite/examples/object_detection/raspberry_pi)提供的示例代码。
4. 实现对车身上的温度传感器等的控制、实现实时的GPS坐标的采集
5. 实现相关数据的反馈
6. 当网络不可用时，用蓝牙将数据包发送给临近的小车，由其代为传送
7. 蓝牙传输中的自定义的RSA数据加密
