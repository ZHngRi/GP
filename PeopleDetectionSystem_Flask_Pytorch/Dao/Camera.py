import cv2

from Database.dbs import db

class Camera(db.Model):
    __tablename__ = 'camera'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    ip = db.Column(db.String(100))
    positionx = db.Column(db.Float)
    positiony = db.Column(db.Float)
    describe1 = db.Column(db.String(100))
    outputPath = db.Column(db.String(100))
    rtmp_server = db.Column(db.String(100))

    def __init__(self, id,name, ip, positionx, positiony, describe1, outputPath, rtmp_server,cap):
        self.id = id
        self.name = name
        self.ip = ip
        self.positionx = positionx
        self.positiony = positiony
        self.describe1 = describe1
        self.outputPath = outputPath
        self.rtmp_server =rtmp_server
        self.cap = cap

    def keys(self):
        return ('id', 'name', 'ip', 'positionx', 'positiony', 'describe1', 'outputPath', 'rtmp_server')

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        return f'<Camera {self.name}>'

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
