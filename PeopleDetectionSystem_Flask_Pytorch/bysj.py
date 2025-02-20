import numpy as np
import pymysql

import tracker
from Dao.Camera import Camera
from detector_final import Detector
import cv2
import threading
import requests
import json
import subprocess as sp

def convert_to_number(s):
    try:
        num = int(s)
        return num
    except ValueError:
        return s
#capture = cv2.VideoCapture(convert_to_number(ip)) 如果传入数字比如0就是本机，如果是字符串就不行

def ffmpeg_cmd(id,ip):
    rtmpUrl = "rtmp://127.0.0.1:1985/live/home" + str(id)               #这个数据库里有，但是这里只穿了id，ip
    outPath = 'E:/BiYe/nginx_1.7.11.3_Gryphon/hls/' + str(id) + '.m3u8' #这个数据库里有，但是这里只穿了id，ip

    capture = cv2.VideoCapture(convert_to_number(ip))
    codec_params = "-c:v libx264 -preset veryfast -tune zerolatency -pix_fmt yuv420p"
    command = (f"ffmpeg -f rawvideo -r 30 -pixel_format bgr24 -video_size {int(capture.get(3))}x{int(capture.get(4))} -framerate 30 "
               f"-i - {codec_params} -f flv {rtmpUrl}")
    # ffmpeg_cmd_hls = [ "ffmpeg", "-i", rtmpUrl,"-c:v", "libx264","-f", "hls", "-hls_time", "10","-hls_list_size", "6",outPath]
    # 设置管道
    ffmpeg_cmd_hls = ["ffmpeg", "-i", rtmpUrl, "-r", "30", "-c:v", "libx264", "-f", "hls", "-hls_time", "10",
                      "-hls_list_size", "6", outPath]

    p = sp.Popen(command, stdin=sp.PIPE)
    p1 = sp.Popen(ffmpeg_cmd_hls, stdin=sp.PIPE)
    return p, p1, capture


def init(id,ip):
    p, p1, capture = ffmpeg_cmd(id,ip)

    mask_image_temp = np.zeros((int(capture.get(3)), int(capture.get(4))), dtype=np.uint8)
    '''
        创建一个黑色的空白图像mask_image_temp，大小与视频帧大小相同。
        capture.get(3)  宽度
    '''



    # 初始化2个撞线polygon
    list_pts_blue = [[int(capture.get(4))/2-10,0], [int(capture.get(4))/2-10,int(capture.get(3))], [int(capture.get(4))/2,0], [int(capture.get(4))/2,int(capture.get(3))]]
    ndarray_pts_blue = np.array(list_pts_blue, np.int32)
    polygon_blue_value_1 = cv2.fillPoly(mask_image_temp, [ndarray_pts_blue], color=1)

    polygon_blue_value_1 = polygon_blue_value_1[:, :, np.newaxis]
    '''的维度增加了一个新的轴，目的是为了适应后续的操作。'''

    # 填充第二个polygon
    mask_image_temp = np.zeros((int(capture.get(3)), int(capture.get(4))), dtype=np.uint8)


    list_pts_yellow = [[int(capture.get(4))/2+10,0], [int(capture.get(4))/2+10,int(capture.get(3))], [int(capture.get(4))/2,0], [int(capture.get(4))/2,int(capture.get(3))]]

    # list_pts_yellow = [[275,0], [275,636], [285,639], [285,0]]
    ndarray_pts_yellow = np.array(list_pts_yellow, np.int32)
    polygon_yellow_value_2 = cv2.fillPoly(mask_image_temp, [ndarray_pts_yellow], color=2)
    polygon_yellow_value_2 = polygon_yellow_value_2[:, :, np.newaxis]
    '''的维度增加了一个新的轴，目的是为了适应后续的操作。'''


    # 撞线检测用mask，包含2个polygon，（值范围 0、1、2），供撞线计算使用
    polygon_mask_blue_and_yellow = polygon_blue_value_1 + polygon_yellow_value_2

    # 蓝 色盘 b,g,r
    blue_color_plate = [255, 0, 0]
    # 蓝 polygon图片
    blue_image = np.array(polygon_blue_value_1 * blue_color_plate, np.uint8)

    # 黄 色盘
    yellow_color_plate = [0, 255, 255]
    # 黄 polygon图片
    yellow_image = np.array(polygon_yellow_value_2 * yellow_color_plate, np.uint8)

    # 彩色图片（值范围 0-255）
    color_polygons_image = blue_image + yellow_image
    color_polygons_image = cv2.resize(color_polygons_image,(int(capture.get(3)), int(capture.get(4))))

    # list 与蓝色polygon重叠
    list_overlapping_blue_polygon = []

    # list 与黄色polygon重叠
    list_overlapping_yellow_polygon = []

    # 进入数量
    down_count = 0
    # 离开数量
    up_count = 0


    # 初始化 yolov5
    detector = Detector()

    # 打开视频

    print(ip)

    while True:
        # 读取每帧图片
        _, im = capture.read()
        if im is None:
            print("can't read video")
            break

        list_bboxs = []
        bboxes = detector.detect(im)
        if len(bboxes) > 0:
            img = im.copy()
            try:
                list_bboxs = tracker.update(bboxes, im)
            except:
                pass
            output_image_frame = tracker.draw_bboxes(im, list_bboxs, line_thickness=None)

        else:
            # 如果画面中 没有bbox
            output_image_frame = im
        pass
        output_image_frame2 = output_image_frame.copy()
        if len(list_bboxs) > 0:



            # ----------------------判断撞线----------------------
            for item_bbox in list_bboxs:
                x1, y1, x2, y2, label, track_id= item_bbox
                # 撞线检测点，(x1，y1)，y方向偏移比例 0.0~1.0
                y1_offset = int(y2 - ((y2 - y1) * 0.5))
                '''竖着框框中间点'''
                # 撞线的点
                y = y1_offset
                x = x1
                if x >= int(capture.get(4)):
                    continue
                if polygon_mask_blue_and_yellow[y, x] == 1:
                    # print("in: ",y,x)
                    # 如果撞 蓝polygon
                    if track_id not in list_overlapping_blue_polygon:
                        list_overlapping_blue_polygon.append(track_id)

                    # 判断 黄polygon list 里是否有此 track_id
                    # 有此 track_id，则 认为是 外出方向
                    if track_id in list_overlapping_yellow_polygon:
                        # 外出+1
                        up_count += 1

                        data ={
                            "key":"123",
                            "inout1":"1",
                            "camera":str(id)
                        }
                        requests.post("http://localhost:3001/api/detection/update", json=data)  # 发post请求,以json字符串参数格式

                        print(f'类别: {label} | id: {track_id} | 上行撞线 | 上行撞线总数: {up_count} | 上行id列表: {list_overlapping_yellow_polygon}')

                        # 删除 黄polygon list 中的此id
                        list_overlapping_yellow_polygon.remove(track_id)

                        pass
                    else:
                        # 无此 track_id，不做其他操作
                        pass

                elif polygon_mask_blue_and_yellow[y, x] == 2:
                    # 如果撞 黄polygon
                    if track_id not in list_overlapping_yellow_polygon:
                        list_overlapping_yellow_polygon.append(track_id)
                    pass

                    # 判断 蓝polygon list 里是否有此 track_id
                    # 有此 track_id，则 认为是 进入方向
                    if track_id in list_overlapping_blue_polygon:
                        # 进入+1
                        down_count += 1

                        
                        data ={
                            "key":"123",
                            "inout1":"0",
                            "camera":str(id)
                        }
                        req = requests.post("http://localhost:3001/api/detection/update", json=data)  # 发post请求,以json字符串参数格式

                        print(f'类别: {label} | id: {track_id} | 下行撞线 | 下行撞线总数: {down_count} | 下行id列表: {list_overlapping_blue_polygon}')

                        # 删除 蓝polygon list 中的此id
                        list_overlapping_blue_polygon.remove(track_id)

                        pass
                    else:
                        # 无此 track_id，不做其他操作
                        pass
                    pass
                else:
                    pass
                pass

            pass

            # ----------------------清除无用id----------------------
            list_overlapping_all = list_overlapping_yellow_polygon + list_overlapping_blue_polygon
            for id1 in list_overlapping_all:
                is_found = False
                for _, _, _, _, _, bbox_id  in list_bboxs:
                    '''
                        _, _, _, _, _, bbox_id  _为占位符      x1, y1, x2, y2, label, track_id
                        不用管那种已经夸了线的，那些虽然这次不清除，但终究会出去黄蓝区域，到时候在清除
                    '''
                    if bbox_id == id1:
                        is_found = True
                        break

                if not is_found:
                    # 如果没找到，删除id
                    if id1 in list_overlapping_yellow_polygon:
                        list_overlapping_yellow_polygon.remove(id1)
                    pass
                    if id1 in list_overlapping_blue_polygon:
                        list_overlapping_blue_polygon.remove(id1)
            list_overlapping_all.clear()
            list_bboxs.clear()
        else:
            # 如果图像中没有任何的bbox，则清空list
            list_overlapping_blue_polygon.clear()
            list_overlapping_yellow_polygon.clear()
            pass
        pass

        #推送到流媒体服务器
        p.stdin.write(output_image_frame2.tostring())


        pass
    pass

    capture.release()





def get_all_cameras():
    # 建立数据库连接
    connection = pymysql.connect(host='localhost',port=3306, user='zhr', password='424512059', database='camera')
    # 创建游标对象
    cursor = connection.cursor()

    # 编写 SQL 查询语句
    sql_query = "SELECT * FROM camera"

    # 执行查询语句
    cursor.execute(sql_query)

    # 获取所有查询结果
    results = cursor.fetchall()

    # 关闭游标和数据库连接
    cursor.close()
    connection.close()

    # 将查询结果转换为 Camera 对象的列表
    cameras = []

    for row in results:
        def convert_to_number(s):
            try:
                num = int(s)
                return num
            except ValueError:
                return s
        # camera = Camera(*row)
        camera = Camera(id=row[0],
                        name=row[1],
                        ip=row[2],
                        positionx=row[3],
                        positiony=row[4],
                        describe1=row[5],
                        outputPath=row[6],
                        rtmp_server=row[7],
                        cap=1
                        )
        cameras.append(camera)

    return cameras




if __name__ == '__main__':
    req = get_all_cameras()

    for i in req:
        thread = threading.Thread(target=init,args=(i["id"],i["ip"]))
        thread.start()



    