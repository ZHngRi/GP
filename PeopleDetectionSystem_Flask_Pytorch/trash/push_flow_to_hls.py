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
        sild = 15
        while True:
            ret, frame = self.camera.cap.read()
            if step % sild == 0:
                frame, bbox = self.detector.output(frame,self.camera.id)
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
    cursor = connection.cursor()
    sql_query = "SELECT * FROM camera"
    cursor.execute(sql_query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
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
                        cap = cv2.VideoCapture(convert_to_number(row[2]))
                        )
        cameras.append(camera)

    return cameras
if __name__ == "__main__":
    cameras = get_all_cameras()
    d = Detector()
    video_streams = []
    for i in cameras:
        print(dict(i))
        v = VideoStreamer(i, detector=d)
        video_streams.append(v)
    # Register cleanup function to be called upon program termination
    atexit.register(lambda: [e.stop_streaming() for e in video_streams])

    threads = [VideoStreamerThread(stream) for stream in video_streams]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

