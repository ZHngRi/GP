# -*- coding: utf-8 -*-
from flask import Flask
from flask_script import Manager
from Database import config
from Database.dbs import db
from Dao.UserApp import userApp


app = Flask(__name__)





app = Flask(__name__)
# def make_shell_context():
#     return dict(app=app, db=db, user=User)
with app.app_context():
    app.register_blueprint(userApp)
    app.config.from_object(config)
    manager = Manager(app)
    db.init_app(app)
    db.create_all()

# class User(db.Model):
#     __tablename__ = 'user'
#
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(32))
#     password = db.Column(db.String(24))
#     usertype = db.Column(db.String(32))
#     avatar = db.Column(db.String(24))
#     remark = db.Column(db.String(24))
#     phone = db.Column(db.String(24))
#     def __init__(self, id, name, password, usertype,avatar,remark,phone):
#         self.id = id
#         self.name = name
#         self.password = password
#         self.usertype = usertype
#         self.avatar = avatar
#         self.remark = remark
#         self.phone = phone
#
#     def get_id(self):
#         return self.id
#
#     def __repr__(self):
#         return '<User %r>' % self.name
#
#     def keys(self):
#         return ('id','name', 'password','usertype','avatar','remark','phone')
#
#     def __getitem__(self, item):
#         return getattr(self, item)
#
#
# @app.route('/login',methods=['GET','POST'])
# def login2():
#     data = request.json
#     print(data)
#     username = data.get('name')
#     password = data.get('password')
#     users = User.query.filter_by(name=username, password=password).first()
#     if users is not None and users.password == password:
#         # 登录成功
#         user_data = {
#             "name": username,
#             "usertype": users.usertype,  # 用户类型示例
#             "remark": users.remark,  # 用户备注信息示例
#             "avatar": users.avatar ,  # 用户头像示例
#             "phone":  users.phone  # 用户手机号示例
#         }
#         return jsonify({"status": 200, **user_data})
#     elif users is not None:
#         # 密码错误
#         return jsonify({"status": 1})
#     else:
#         # 用户名不存在  or  密码错误
#         return jsonify({"status": 2})
#
# @app.route('/user',methods=['GET','POST'])
# def getAllUser():
#     all_user = User.query.all();
#     list = [dict(i) for i in all_user]
#     return jsonify(list)
#
# @app.route('/user/update',methods=['POST'])
# def update_user():
#     try:
#         data = request.json
#         user_id = data.get('id')
#
#         user = User.query.get(user_id)
#         if user:
#             user.name = data.get('name')
#             user.password = data.get('password')
#             user.usertype = data.get('usertype')
#             user.avatar = data.get('avatar')
#             user.remark = data.get('remark')
#             user.phone = data.get('phone')
#
#             db.session.commit()
#             return jsonify(True), 200
#         else:
#             return jsonify(False), 404
#     except SQLAlchemyError as e:
#         db.session.rollback()  # 回滚会话，撤销所有未提交的更改
#         error = str(e.__dict__.get('orig') or e)
#         return jsonify({'error': error}), 500
#
# @app.route('/user/save', methods=['POST'])
# def add_user():
#     try:
#         data = request.json
#
#         user = User(
#             name=data.get('name'),
#             password=data.get('password'),
#             usertype=data.get('usertype'),
#             avatar=data.get('avatar'),
#             remark=data.get('remark'),
#             phone=data.get('phone')
#         )
#
#         db.session.add(user)
#         db.session.commit()
#
#         return jsonify(True), 200
#     except SQLAlchemyError as e:
#         db.session.rollback()  # 回滚会话，撤销所有未提交的更改
#         error = str(e.__dict__.get('orig') or e)
#         return jsonify({'error': error}), 500
#
# @app.route('/user/delete/<int:user_id>', methods=['POST'])
# def delete_user(user_id):
#     try:
#         user = User.query.get(user_id)
#         if user:
#             db.session.delete(user)
#             db.session.commit()
#             return jsonify(True), 200
#         else:
#             return jsonify(False), 404
#     except SQLAlchemyError as e:
#         db.session.rollback()  # 回滚会话，撤销所有未提交的更改
#         error = str(e.__dict__.get('orig') or e)
#         return jsonify({'error': error}), 500




# @app.route('/camera')
# @login_required
# def index():
#     # 提供多个视频流的URL
#     stream_urls = [
#         'http://localhost/hls/output1.m3u8',
#         'http://localhost/hls/output1.m3u8',
#         'http://localhost/hls/output1.m3u8',
#         'http://localhost/hls/output1.m3u8',
#         # ... 添加更多视频流的URL
#     ]
#     return render_template('index.html', name=session.get('User_name'),stream_urls=stream_urls)
#

import threading

import cv2
import subprocess
import atexit

import pymysql
from detector_final import Detector
from Dao.Camera import Camera
class VideoStreamerThread(threading.Thread):
    def __init__(self, video_stream):
        super().__init__()
        self.video_stream = video_stream

    def run(self):
        self.video_stream.start_streaming()
# class Camera:
#     def __init__(self, ip=0, id=0,
#                  rtmp_server="rtmp://127.0.0.1:1985/live/home",
#                  outputPath="E:/BiYe/nginx_1.7.11.3_Gryphon/hls/output.m3u8"):
#         self.ip = ip
#         self.id = id
#         self.rtmp_server = rtmp_server
#         self.outputPath = outputPath
#         self.cap = cv2.VideoCapture(self.ip)
#
#     def release(self):
#         if self.cap.isOpened():
#             self.cap.release()

class VideoStreamer:
    def __init__(self, camera, detector=Detector()):
        self.camera = camera
        self.ffmpeg_process = None
        self.ffmpeg_process_hls = None
        self.detector = detector
        self.codec_params = "-c:v libx264 -preset veryfast -tune zerolatency -pix_fmt yuv420p"

    def start_streaming(self):
        ffmpeg_cmd = f"ffmpeg -f rawvideo -pixel_format bgr24 -video_size {int(self.camera.cap.get(3))}x{int(self.camera.cap.get(4))} -framerate 30 -i - {self.codec_params} -f flv {self.camera.rtmp_server}"
        ffmpeg_cmd_hls = [
            "ffmpeg",
            "-i", self.camera.rtmp_server,
            "-c:v", "libx264",
            "-f", "hls",
            "-hls_time", "10",
            "-hls_list_size", "6",
            self.camera.outputPath
        ]

        self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, shell=True, stdin=subprocess.PIPE)
        self.ffmpeg_process_hls = subprocess.Popen(ffmpeg_cmd_hls, stdin=subprocess.PIPE)

        try:
            self._stream_loop()
        except KeyboardInterrupt:
            self.stop_streaming()

    def _stream_loop(self):
        step = 0
        bbox = None
        sild = 40
        while True:
            ret, frame = self.camera.cap.read()
            if step % sild == 0:
                frame, bbox = self.detector.output(frame)
            else:
                frame = self.detector.bbox(bbox, frame)

            processed_frame = frame
            self.ffmpeg_process.stdin.write(processed_frame.tobytes())

            step = (step + 1) % 100

    def stop_streaming(self):
        self.camera.release()

        if self.ffmpeg_process:
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()

        if self.ffmpeg_process_hls:
            self.ffmpeg_process_hls.stdin.close()
            self.ffmpeg_process_hls.wait()

        cv2.destroyAllWindows()
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
        print(row)
        camera = Camera(*row)
        camera.cap = cv2.VideoCapture(camera.ip)
        cameras.append(camera)
        # print(dict(camera))
    return cameras
if __name__ == "__main__":

    cameras = get_all_cameras()

    d = Detector()
    # cameras = Camera.query.all()
    camera = Camera(id=1,
                    ip=0,
                    name='test',
                    outputPath='E:/BiYe/nginx_1.7.11.3_Gryphon/hls/1.m3u8',
                    rtmp_server=f"rtmp://127.0.0.1:1985/live/home2",
                     describe1='',
                     positionx='',
                     positiony='',
                    # cap = cv2.VideoCapture(0)
                     )
    print(dict(camera))
    # camera2 = Camera(id=0,
    #                 ip=0,
    #                 outputPath='E:/BiYe/nginx_1.7.11.3_Gryphon/hls/output2.m3u8',
    #                 rtmp_server=f"rtmp://127.0.0.1:1985/live/home2")

    # v1 = VideoStreamer(camera, detector=d)
    # v2 = VideoStreamer(camera2, detector=d)

    video_streams = []
    for i in cameras:
        v = VideoStreamer(i, detector=d)
        video_streams.append(v)
    # Register cleanup function to be called upon program termination
    atexit.register(lambda: [e.stop_streaming() for e in video_streams])

    threads = [VideoStreamerThread(stream) for stream in video_streams]
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


















