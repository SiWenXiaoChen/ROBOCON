# python
# 陈涛
# 开发时间：$[DATE] $[TIME]
import numpy as np
import cv2  # opencv库
import serial  # python串口库
import serial.tools.list_ports
import threading
from threading import Thread
import time
import multiprocessing
import random

"""可更改变量"""
color_lower = np.array([60, 141, 25])  # HSV阈值低
color_upper = np.array([174, 255, 255])  # HSV阈值高
video = 0  # 视频来源，usb摄像头一般为0
Area = 3000  # 预定义正对色块大小
width = 640  # 分辨率宽
height = 480  # 分辨率高
light_com_name = "COM6"  # 激光模块串口号,字符串格式
mpu_com_name = "COM7"  # 单片机模块串口号，字符串格式
mode = "fast"  # 设置激光测距模式，标准->"standard"，慢速->"slow"，快速->"fast"

"""不可更改变量"""
cap = cv2.VideoCapture(video, cv2.CAP_DSHOW)  # 捕捉视频
cap.set(3, width)  # 设置分辨率宽640
cap.set(4, height)  # 设置分辨率高480
light_on_flag = False  # 激光打开标注
light_off_flag = False  # 激光关闭标志
dis = 0  # 距离
accuracy = 0  # 精准度

"""一些全局变量"""
bais_x=0 #横坐标偏差
x_last = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
p_last = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Q = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]  # 系统噪声
R = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]  # 测量噪声
y = [[], [], [], [], [], [], [], [], [], []]
Distance = []
color_dist = {
              'forward_yellow_blind_path': {'Lower': np.array([57, 166, 59]), 'Upper': np.array([119, 255, 255])},
              'chin_yellow_blind_path': {'Lower': np.array([10, 40, 120]), 'Upper': np.array([40, 255, 255])},
              }


def kalman_2(z_measure, i):
    global x_last, p_last, Q, R
    x_mid = x_last[i]
    p_mid = p_last[i] + Q[i]
    kg = p_mid / (p_mid + R[i])
    x_now = x_mid + kg * (z_measure - x_mid)
    p_now = (1 - kg) * p_mid
    p_last[i] = p_now
    x_last[i] = x_now
    return x_now, p_last[i], x_last[i]

class Realsense(object):
    def object_color_detect(object_color):
        '''
        detect the color boject
        '''
        global depth_frame, color_image
        hsvFrame = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        # HSV
        color_lower = np.array(color_dist[object_color]["Lower"], np.uint8)
        color_upper = np.array(color_dist[object_color]["Upper"], np.uint8)
        color_mask = cv2.inRange(hsvFrame, color_lower, color_upper)
        cv2.imshow("color_mask", color_mask)

        color_mask = cv2.medianBlur(color_mask, 7)  # 中值滤波

        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # 矩形结构
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # 椭圆结构
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))  # 十字形结构

        color_mask = cv2.dilate(color_mask, kernel)  # 膨胀
        kernel = np.ones((10, 10), np.uint8)
        # color_mask = cv2.erode(color_mask, kernel)  # 腐蚀

        res = cv2.bitwise_and(color_image, color_image, mask=color_mask)
        cv2.imshow("Color Detection res in Real-Time", res)

        # Creating contour to track red color
        contours, hierarchy = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        try:

            # 最小外接正矩形
            c = max(contours, key=cv2.contourArea)
            left_x, left_y, width, height = cv2.boundingRect(c)

            bound_rect = np.array([[[left_x, left_y]], [[left_x + width, left_y]],
                                   [[left_x + width, left_y + height]], [[left_x, left_y + height]]])
            box_list = bound_rect.tolist()
            cv2.drawContours(color_image, [bound_rect], -1, (255, 255, 255), 2)

        except ValueError:
            box_list = []

        return box_list

    def object_distance_measure(bbox_list):
        global depth_frame, color_image, p_last, x_last
        if bbox_list != []:
            # print(type(bbox_list))
            print(bbox_list)
            left = bbox_list[0][0][0]
            right = bbox_list[1][0][0]
            top = bbox_list[1][0][1]
            bottom = bbox_list[3][0][1]
            width = right - left
            height = bottom - top
            centre_x = (left + width) / 2
            centre_y = (top + height) / 2
            # 测距的区域
            roi_lx = int(left + width / 4)
            roi_rx = int(right - width / 4)
            roi_ty = int(top + height / 4)
            roi_by = int(bottom - height / 4)
            # print(roi_lx, roi_rx, roi_ty, roi_by)
            color_image = cv2.rectangle(color_image, (roi_lx, roi_ty), (roi_rx, roi_by), (255, 255, 0), 3)

            center_x = int(roi_lx + width / 2)
            center_y = int(roi_ty + height / 2)
            cv2.circle(color_image, (center_x, center_y), 5, (0, 0, 255), 0)

            depth_points = []
            depth_means = []
            print(centre_x, centre_y)
            # 获取目标框内的物体距离，并进行均值滤波.
            if 160 < centre_x < 210 and 100 < centre_y < 155:
                for j in range(20):
                    rand_x = random.randint(roi_lx, roi_rx)  # 生成roi_lx到roi_rx之间的随机整数
                    rand_y = random.randint(roi_ty, roi_by)
                    depth_point = round(depth_frame.get_distance(rand_x, rand_y) * 100, 2)  # 返回浮点数的四舍五入值
                    if depth_point != 0:
                        depth_points.append(depth_point)
                depth_object = np.mean(depth_points)
                Distance.append(depth_object)
                for i in range(10):
                    depth_object, p_last[i], x_last[i] = kalman_2(depth_object, i)
                    y[i].append(depth_object)
                if depth_object >= 30:
                    print("The camera is facing an object mean ", int(depth_object), " cm away.")
                else:
                    print("The camera is facing an object mean <30 cm away.")


class Comcontrol(serial.Serial):  # 定义串口控制类,继承串口类
    def __init__(self, port, baudrate, bytesize, stopbits, timeout, parity):  # 实例初始化
        super(Comcontrol, self).__init__()
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.timeout = timeout
        self.parity = parity
        """建立串口连接"""
        """设置串口参数：串口号，波特率，数据长度，停止位,延迟时间，校验位"""
        self.com = serial.Serial(port=self.port,
                                 baudrate=self.baudrate,
                                 bytesize=self.bytesize,
                                 stopbits=self.stopbits,
                                 timeout=self.timeout,
                                 parity=self.parity)

    def light_on(self):
        """开启激光"""
        """由产品手册得知，往模块发送大写字母O即可开启激光"""
        self.com.write("O".encode())
        data = self.com.read(10).decode('utf-8')
        print(data)
        if data == "O,OK!\r\n":  # 开启成功返回True
            return True
        else:
            return False

    def light_off(self):
        """关闭激光"""
        """由产品手册得知，往模块发送大写字母C即可开启激光"""
        self.com.write("C".encode())
        data = self.com.read(10).decode('utf-8')
        print(data)
        if data == "C,OK!\r\n":  # 关闭成功返回True
            return True
        else:
            return False

    def measure(self, mode):
        """测量距离，入口参数：串口实例，测量模式"""
        """由产品手册得知，测量模式为：D->标准模式，M->慢速模式，F->快速模式"""
        """由产品手册得知，读取从串口返回数据为：'12.345m,0079'字符串类型"""
        distance = 0  # 距离定义
        ac = 0  # 精准度定义
        if mode == "standard":
            self.com.write("D".encode())
            if self.com.in_waiting:
                data = self.com.read(100).decode('utf-8')  # 得到返回字符串
                distance = int(data[3] + data[5:8])  # 处理得到距离，单位mm
                ac = int(data[10:-1])  # 处理得到准确度，数值越小越准确
        elif mode == "slow":
            self.com.write("M".encode())
            if self.com.in_waiting:
                data = self.com.read(100).decode('utf-8')
                distance = int(data[3] + data[5:8])
                ac = int(data[10:-1])
        elif mode == "fast":
            #self.com.write("iFACM".encode())
            if self.com.in_waiting:
                data = self.com.read(10).decode('utf-8')
                #distance.append(data)
                distance = int(data[2])*1 + int(data[4])*0.1 + int(data[5])*0.01 + int(data[6])*0.001
                ac = int(data[6])*0.001
        return distance, ac





def white_balance(img, mode=5):
    """白平衡处理（默认为5, 1均值、2完美反射、3灰度世界、4基于图像分析的偏色检测及颜色校正、5动态阈值）"""
    # 读取图像
    b, g, r = cv2.split(img)
    # 均值变为三通道
    h, w, c = img.shape
    if mode == 1:
        # 默认均值  ---- 简单的求均值白平衡法
        b_avg, g_avg, r_avg = cv2.mean(b)[0], cv2.mean(g)[0], cv2.mean(r)[0]
        # 求各个通道所占增益
        k = (b_avg + g_avg + r_avg) / 3
        kb, kg, kr = k / b_avg, k / g_avg, k / r_avg
        b = cv2.addWeighted(src1=b, alpha=kb, src2=0, beta=0, gamma=0)
        g = cv2.addWeighted(src1=g, alpha=kg, src2=0, beta=0, gamma=0)
        r = cv2.addWeighted(src1=r, alpha=kr, src2=0, beta=0, gamma=0)
        output_img = cv2.merge([b, g, r])
    elif mode == 2:
        # 完美反射白平衡 ---- 依赖ratio值选取而且对亮度最大区域不是白色的图像效果不佳。
        output_img = img.copy()
        sum_ = np.double() + b + g + r
        hists, bins = np.histogram(sum_.flatten(), 766, [0, 766])
        Y = 765
        num, key = 0, 0
        ratio = 0.01
        while Y >= 0:
            num += hists[Y]
            if num > h * w * ratio / 100:
                key = Y
                break
            Y = Y - 1

        sumkey = np.where(sum_ >= key)
        sum_b, sum_g, sum_r = np.sum(b[sumkey]), np.sum(g[sumkey]), np.sum(r[sumkey])
        times = len(sumkey[0])
        avg_b, avg_g, avg_r = sum_b / times, sum_g / times, sum_r / times

        maxvalue = float(np.max(output_img))
        output_img[:, :, 0] = output_img[:, :, 0] * maxvalue / int(avg_b)
        output_img[:, :, 1] = output_img[:, :, 1] * maxvalue / int(avg_g)
        output_img[:, :, 2] = output_img[:, :, 2] * maxvalue / int(avg_r)
    elif mode == 3:
        # 灰度世界假设
        b_avg, g_avg, r_avg = cv2.mean(b)[0], cv2.mean(g)[0], cv2.mean(r)[0]
        # 需要调整的RGB分量的增益
        k = (b_avg + g_avg + r_avg) / 3
        kb, kg, kr = k / b_avg, k / g_avg, k / r_avg
        ba, ga, ra = b * kb, g * kg, r * kr

        output_img = cv2.merge([ba, ga, ra])
    elif mode == 4:
        # 基于图像分析的偏色检测及颜色校正
        I_b_2, I_r_2 = np.double(b) ** 2, np.double(r) ** 2
        sum_I_b_2, sum_I_r_2 = np.sum(I_b_2), np.sum(I_r_2)
        sum_I_b, sum_I_g, sum_I_r = np.sum(b), np.sum(g), np.sum(r)
        max_I_b, max_I_g, max_I_r = np.max(b), np.max(g), np.max(r)
        max_I_b_2, max_I_r_2 = np.max(I_b_2), np.max(I_r_2)
        [u_b, v_b] = np.matmul(np.linalg.inv([[sum_I_b_2, sum_I_b], [max_I_b_2, max_I_b]]), [sum_I_g, max_I_g])
        [u_r, v_r] = np.matmul(np.linalg.inv([[sum_I_r_2, sum_I_r], [max_I_r_2, max_I_r]]), [sum_I_g, max_I_g])
        b0 = np.uint8(u_b * (np.double(b) ** 2) + v_b * b)
        r0 = np.uint8(u_r * (np.double(r) ** 2) + v_r * r)
        output_img = cv2.merge([b0, g, r0])
    elif mode == 5:
        # 动态阈值算法 ---- 白点检测和白点调整
        # 只是白点检测不是与完美反射算法相同的认为最亮的点为白点，而是通过另外的规则确定
        def con_num(x):
            if x > 0:
                return 1
            if x < 0:
                return -1
            if x == 0:
                return 0

        yuv_img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        # YUV空间
        (y, u, v) = cv2.split(yuv_img)
        max_y = np.max(y.flatten())
        sum_u, sum_v = np.sum(u), np.sum(v)
        avl_u, avl_v = sum_u / (h * w), sum_v / (h * w)
        du, dv = np.sum(np.abs(u - avl_u)), np.sum(np.abs(v - avl_v))
        avl_du, avl_dv = du / (h * w), dv / (h * w)
        radio = 0.5  # 如果该值过大过小，色温向两极端发展

        valuekey = np.where((np.abs(u - (avl_u + avl_du * con_num(avl_u))) < radio * avl_du)
                            | (np.abs(v - (avl_v + avl_dv * con_num(avl_v))) < radio * avl_dv))
        num_y, yhistogram = np.zeros((h, w)), np.zeros(256)
        num_y[valuekey] = np.uint8(y[valuekey])
        yhistogram = np.bincount(np.uint8(num_y[valuekey].flatten()), minlength=256)
        ysum = len(valuekey[0])
        Y = 255
        num, key = 0, 0
        while Y >= 0:
            num += yhistogram[Y]
            if num > 0.1 * ysum:  # 取前10%的亮点为计算值，如果该值过大易过曝光，该值过小调整幅度小
                key = Y
                break
            Y = Y - 1

        sumkey = np.where(num_y > key)
        sum_b, sum_g, sum_r = np.sum(b[sumkey]), np.sum(g[sumkey]), np.sum(r[sumkey])
        num_rgb = len(sumkey[0])

        b0 = np.double(b) * int(max_y) / (sum_b / num_rgb)
        g0 = np.double(g) * int(max_y) / (sum_g / num_rgb)
        r0 = np.double(r) * int(max_y) / (sum_r / num_rgb)

        output_img = cv2.merge([b0, g0, r0])
    else:
        raise TypeError('mode should be in [1,2,3,4,5]. Got {}'.format(mode))
    output_img = np.uint8(np.clip(output_img, 0, 255))
    return output_img




def draw_cross(x, y):
    """画图函数"""
    cv2.circle(frame, (x, y), 1, (255, 0, 255), 2)  # 半径足够小的圆就是画点
    cv2.line(frame, (int(x + 5), int(y)), (int(x + 10), int(y)), (255, 0, 255), 2)  # 画出断十字
    cv2.line(frame, (int(x - 5), int(y)), (int(x - 10), int(y)), (255, 0, 255), 2)
    cv2.line(frame, (int(x), int(y + 5)), (int(x), int(y + 10)), (255, 0, 255), 2)
    cv2.line(frame, (int(x), int(y - 5)), (int(x), int(y - 10)), (255, 0, 255), 2)
    # 打印出物体的坐标，坐标可以与单片机通信
    print(x, y)


def dis_ac_process(light_ser, mpu_ser):
    while True:
        global bais_x
        dis, accuracy = light_ser.measure(mode=mode)  # 选择模式测距
        print(dis, accuracy, "\r\n")  # 打印出距离和准确度
        mpu_ser.com.write("@".encode() + str(bais_x).encode() + "e".encode())  # 向单片机串口发送激光测出距离，帧头@
        mpu_ser.com.write("$".encode() + str(dis).encode() + "e".encode())  # 向单片机串口发送激光测距准确度，帧头$


def light_com_connect():           # 连接激光串口
    flag1 = False
    while flag1 is False:  # 没连接到激光模块串口则一直连接
        port_list = list(serial.tools.list_ports.comports())  # 搜索可用串口
        if len(port_list) == 0:  # 没有可用串口
            print("no useful COM\r\n")
        else:
            print("find com successful\r\n")
            for i in range(0, len(port_list)):
                port = port_list[i]  # 提取使用串口字符串
                port = str(port)
                print("you use: ", port[0:4], "\r\n")
                if port[0:4] == light_com_name:
                    light_ser = Comcontrol(port=light_com_name,  # 激光串口实例化
                                           baudrate=115200,
                                           bytesize=8,
                                           stopbits=1,
                                           timeout=0.6,
                                           parity='N')
                    flag1 = light_ser.com.is_open  # 激光模块是否打开标志
                    if flag1:
                        print("light connection success\r\n")
                        return light_ser
                else:
                    print("connection failed\r\n")


def mpu_com_connect():
    flag2 = False
    while flag2 is False:
        mpu_ser = Comcontrol(port=mpu_com_name,  # 单片机串口实例化
                             baudrate=115200,
                             bytesize=8,
                             stopbits=1,
                             timeout=0.8,
                             parity='N')
        flag2 = mpu_ser.com.is_open
        if flag2:
            print("mpu connection success\r\n")
            return mpu_ser




"""主进程用以开启子进程"""
if __name__ == '__main__':

    """连接激光串口"""
    light_ser = light_com_connect()

    """连接单片机串口"""
    #mpu_ser = mpu_com_connect()

    """开启激光测距进程"""
    #light_process = multiprocessing.Process(target=dis_ac_process, args=(light_ser, mpu_ser))
    #light_process = Thread(target=dis_ac_process, args=(light_ser, mpu_ser))
    #light_process.start()



    while True:
        ret, frame = cap.read()  # 解压一帧图像
        frame = cv2.GaussianBlur(frame, (5, 5), 0)  # 高斯滤波
        frame = white_balance(frame, 5)  # 进行自适应白平衡滤波，效果很好，帧率会降低
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # BGR格式转换成HSV颜色格式
        k = np.ones((10, 10), np.uint8)  # 开运算卷积核
        hsv1 = cv2.dilate(cv2.erode(hsv, k), k)  # 开运算，去除亮点
        mask = cv2.inRange(hsv, color_lower, color_upper)  # 得到mask，入口参数（图像，HSV颜色低值，HSV颜色高值）

        """寻找色块并绘制中心断十字，发送x，y与中心点的误差到单片机"""
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(cnts) > 0:  # 如果找到了颜色
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            #mask1 = np.ones_like(mask)
            #cv2.imshow("mask", mask1)
            if len(cnts) > 0:  # 如果找到了颜色
                cnt = max(cnts, key=cv2.contourArea)
                peri = cv2.arcLength(cnt, True)  # 计算得到弧长，形状是闭合的（True）
                approx = cv2.approxPolyDP(cnt, 0.015 * peri, True)  # 传入轮廓的点集
                bian = len(approx)
                if(bian > 4 and bian < 15):
                    peri = cv2.arcLength(cnt, True)  # 计算得到弧长，形状是闭合的（True）
                    approx = cv2.approxPolyDP(cnt, 0.015 * peri, True)  # 传入轮廓的点集
                    (x, y), radius = cv2.minEnclosingCircle(approx)
                    center_blue = (int(x), int(y))
                    radius = int(radius)
                    # res = cv.circle(frame,center, radius, (0, 255, 0), 2)
                    cv2.circle(frame, center_blue, radius, (0, 255, 0), 5)
                    cv2.circle(frame, center_blue, 1, (0, 0, 255), 5)
                    bais_x = center_blue[0] - width/2
                    #print(bais_x)
                    #mpu_ser.com.write("%".encode('utf-8') + str(bais_x).encode('utf-8') + "RC".encode('utf-8'))  # 向单片机串口发送x误差

                else:
                    print('莫得圆')

            else:
                print("find no color\r\n")
                pass
        cv2.imshow('frame', frame)  # 实时显示

        if cv2.waitKey(1) & 0xFF == 27:  # 等待1ms，检测按下esc退出
            break
cap.release()
cv2.destroyAllWindows()
serial.close()
