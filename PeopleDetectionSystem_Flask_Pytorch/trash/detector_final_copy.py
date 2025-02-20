import cv2
import requests
import torch
import numpy as np
import torchvision
from numpy import random
from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import non_max_suppression, scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import select_device


class Detector:

    def __init__(self):
        self.img_size = 640
        self.threshold = 0.4
        self.stride = 1

        self.weights = './weight/yolov5l6.pt'

        self.device = '0' if torch.cuda.is_available() else 'cpu'
        self.device = select_device(self.device)
        model = attempt_load(self.weights, map_location=self.device)
        model.to(self.device).eval()
        model.half()

        self.m = model
        self.names = model.module.names if hasattr(
            model, 'module') else model.names

        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
    def preprocess(self, img):

        img0 = img.copy()
        img = letterbox(img, new_shape=self.img_size)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half()
        img /= 255.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        return img0, img

    def detect(self, im ,camera_id):

        im0, img = self.preprocess(im)
        # print(img)
        pred = self.m(img, augment=False)[0]
        # print(pred)
        pred = pred.float()
        pred = non_max_suppression(pred, self.threshold, 0.6)
        boxes = []
        for det in pred:

            if det is not None and len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                for *x, conf, cls_id in det:
                    if self.names[int(cls_id)] =='person':
                        x1, y1 = int(x[0]), int(x[1])
                        x2, y2 = int(x[2]), int(x[3])
                        boxes.append((x1, y1, x2, y2, cls_id, conf))


        data = {
            "key": "123",
            "inout1": "0",
            "camera": str(camera_id)
        }
        try:
            requests.post("http://localhost:3001/api/detection/update", json=data)  # 发post请求,以json字符串参数格式
        except:
            return boxes
        return boxes

    def bbox(self , det,im,camera_id):
        for *xyxy, cls, conf in reversed(det):
            label = f'{self.names[int(cls)]} {conf:.2f}'
            plot_one_box(xyxy, im, label=label, color=self.colors[int(cls)], line_thickness=1)
        return im

    def output(self,img0,camera_id):
        bbox = self.detect(img0,camera_id)
        output = self.bbox(bbox,img0,camera_id)
        return output , bbox

if __name__ == '__main__':
    d = Detector()
    img = cv2.imread('')
    img_nor = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    im = d.output(img_nor)
    cv2.imshow('ss3',im)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


# cv2.error: OpenCV(4.7.0)

