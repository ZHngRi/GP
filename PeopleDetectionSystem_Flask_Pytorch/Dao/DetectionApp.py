# -*- coding: utf-8 -*-
import numpy as np
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from Dao.Camera import Camera
from Dao.Detection import Detection
from Dao.User import User
from Database.dbs import db
from flask import Blueprint

from peoplePred import load_and_predict

detectionApp = Blueprint('detection', __name__, template_folder='templates')


def update_detection(detection):
    try:
        db.session.merge(detection)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error occurred: {e}")
        db.session.rollback()
        return False
def save_detection(detection):
    try:
        db.session.add(detection)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error occurred: {e}")
        db.session.rollback()
        return False

def select_by_date_cam(date, inout1, cam):
    # 执行查询
    result = Detection.query.filter_by(date=date, inout1=inout1, camera=cam).first()
    return result

def select_by_date(date, inout1):
    result = Detection.query.filter_by(date=date, inout1=inout1).all()
    return result

def select_by_month_cam(month, inout1, camera_id):
    result_in = Detection.query.filter(
        and_(
            Detection.date.like(f"{month}%"),  # 使用通配符来匹配给定月份的所有日期
            # Detection.inout1 == inout1,
            Detection.camera == camera_id
        )
    ).all()
    return result_in


from datetime import datetime, timedelta, date


@detectionApp.route('/detection/detail/<page>/<per_page>')
def detail(page,per_page):

    page = int(page)
    per_page = int(per_page)
    detections = Detection.query.paginate(page=page, per_page=per_page, error_out=False)  # Correct way to call paginate()

    detection_list = []
    for detection in detections.items:
        detection = dict(detection)
        date_string = detection['date']
        detection['date'] = date_string.strftime("%Y-%m-%d")

        '''时间格式'''
        detection_list.append(detection)

    result = {
        'total': detections.total,
        'per_page': detections.per_page,
        'records': detection_list
    }
    return jsonify(result)


@detectionApp.route('/detection/update', methods=['POST'])
def update():
    data = request.json

    # 检查密钥是否匹配
    if data.get('key') == '123':
        # 获取当前日期和小时
        now = datetime.now()
        str1 = now.strftime("%Y-%m-%d")
        str2 = now.strftime("%H")

        # 查询记录
        result = Detection.query.filter_by(date=str1, inout1=data.get('inout1'), camera=data.get('camera')).first()
        column_names = {
            '00': 'one', '01': 'two', '02': 'three', '03': 'four', '04': 'five',
            '05': 'six', '06': 'seven', '07': 'eight', '08': 'nine', '09': 'ten',
            '10': 'eleven', '11': 'twelve', '12': 'thirteen', '13': 'fourteen',
            '14': 'fifteen', '15': 'sixteen', '16': 'seventeen', '17': 'eighteen',
            '18': 'nineteen', '19': 'twenty', '20': 'twentyone', '21': 'twentytwo',
            '22': 'twentythree', '23': 'twentyfour'
        }
        # 如果没有找到记录，则创建新记录并插入数据库
        if result is None:
            det = Detection(date=now, camera=data.get('camera'),inout1=data.get('inout1'))
            db.session.add(det)
            db.session.commit()
            result = Detection.query.filter_by(date=str1, inout1=data.get('inout1'), camera=data.get('camera')).first()
        # 根据当前小时更新对应的列


        column_name = column_names.get(str2)

        current_value = getattr(result, column_name)
        if current_value is None:
            current_value = 0
        setattr(result, column_name, current_value + 1)

        # 更新数据库中的记录
        db.session.commit()

        return "200"
    else:
        return "-1"


@detectionApp.route('/detection/sum')
def sum_all():
    result_in = Detection.query.filter_by(inout1 = 0) #总计人浏览量 查询0进入的即可
    sum_value = sum(s.sum() for s in result_in)
    return str(sum_value)

@detectionApp.route('/detection/nowpeople')
def now_people():
    d1 = datetime.now()
    str1 = d1.strftime('%Y-%m-%d')  # 日期

    # 查询记录
    result_in = select_by_date(str1, "0")#当天inout1为0的所有记录
    result_out = select_by_date(str1, "1")

    now_people = 0
    for s in result_in:
        now_people += s.sum()
    for s in result_out:
        now_people -= s.sum()

    return jsonify(now_people)




@detectionApp.route('/detection/perday/<date>')
def per_day(date):
    cam = Camera.query.all()  # 查询有几个摄像头
    result = {}  # 新建字典用作返回结果

    # 初始化
    for c in cam:
        result[str(c.id)] = [0] * 24
        #生成一个字典 key 为是摄像头id v 内容为对应摄像头的人数，现在为0

    sum_cam = [0] * 24  # 新建数组存总人次
    '''
        进入为0
        出去为1
    '''
    result_in = select_by_date(date, "0")  #查询记录
    for d in result_in:
        result[str(d.camera)] = d.get_all_data()
        '''d.get_all_data() 返回一个列表为数字为从one - 24  对应数值'''

        for i in range(24):
            if d.get_all_data()[i] is not None:
                sum_cam[i] += d.get_all_data()[i]
                '''求每个点对应当天的总人数'''
    result['0'] = sum_cam  # 将总人次加入结果集，0表示总人次

    # 获取今天的日期和前两年的今天日期
    today_date = datetime.strptime(date, "%Y-%m-%d")
    prev_year_date = today_date - timedelta(days=365)
    prev_2_year_date = today_date - timedelta(days=2 * 365)

    # 格式化日期
    today_str = today_date.strftime("%Y-%m-%d")
    prev_year_str = prev_year_date.strftime("%Y-%m-%d")
    prev_2_year_str = prev_2_year_date.strftime("%Y-%m-%d")

    # 获取相应日期的数据
    prev_data = select_by_date(today_str, "0")
    prev_year_data = select_by_date(prev_year_str, "0")
    prev_2_year_data = select_by_date(prev_2_year_str, "0")

    # 按时间点汇总数据并计算平均值
    total_hours = 24
    avg_data = [0] * total_hours
    count = [0] * total_hours

    for data in (prev_data, prev_year_data, prev_2_year_data):
        for s in data:
            day_data = s.get_all_data()
            for i in range(24):
                if day_data[i] is not None:
                    avg_data[i] += day_data[i]
                    #同样的求总数
                    count[i] += 1

    for i in range(total_hours):
        if count[i] > 0:
            avg_data[i] /= count[i]
    avg_data = np.ceil(avg_data)
    # 预测结果
    model_path = 'my_weight/trained_model.pth'
    scaler_X_path = 'my_weight/scaler_X.pkl'
    scaler_y_path = 'my_weight/scaler_y.pkl'

    prediction = load_and_predict(model_path, scaler_X_path, scaler_y_path, avg_data)

    # 将预测结果转换为 Python 基本数据类型（避免 JSON 编码问题）
    result['pred'] = [int(p) for p in prediction]
    return jsonify(result)


@detectionApp.route('/detection/perweek/<yearweek>')
def per_week(yearweek):
    cam = Camera.query.all()
    result = {}
    for c in cam:
        row = [0, 0, 0, 0, 0, 0, 0]
        result[c.id] = row

    sum_week = [0, 0, 0, 0, 0, 0, 0]
    result[0] = sum_week

    current_date = datetime.strptime(yearweek, "%Y-%m-%d")


    days_to_monday = current_date.weekday()
    #从今天这个日期到这周1的天数
    # 计算本周星期一的日期
    monday_date = current_date - timedelta(days=days_to_monday)

    # 循环遍历一周的每一天
    for i in range(7):
        current_date = monday_date + timedelta(days=i)
        # 查询记录
        result_in = select_by_date(current_date.strftime('%Y-%m-%d'), "0")
        sum_week = 0
        for s in result_in:
            row = result[s.camera]  #先把原来的赋给row
            row[i] = s.sum()        #返回新的天的人数，这里面也有旧的天的人数，因为是以小时为时间粒度的，所以这里的一天就需要返回sum
            result[s.camera] = row  #在附回去
            sum_week += s.sum()     #这周周一。。。全部的人数

        row = result[0]             #先把原来一周前几天的总数的赋给row
        row[i] = sum_week           #返回新的天的人数，这里面也有旧的天的人数
        result[0] = row             #在附回去
    return jsonify(result)



@detectionApp.route('/detection/permonth/<yearmonth>')
def per_month(yearmonth):
    cam = Camera.query.all()

    day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # 每月的天数
    year = int(yearmonth[0:4])
    month = int(yearmonth[5:7])

    result = {}
    for c in cam:
        row = [0] * day[month - 1]
        result[c.id] = row

    sum_month = [0] * day[month - 1]
    result[0] = sum_month

    for i in range(day[month - 1]):
        result_in = select_by_date(f"{year}-{month}-{i + 1}", "0")
        sum_month = 0
        for s in result_in:
            row = result[s.camera]
            #原来情况
            row[i] = s.sum()
            #求当天的和
            result[s.camera] = row
            #重新赋值
            sum_month += s.sum()
        row = result[0]
        row[i] = sum_month
        result[0] = row

    return jsonify(result)

@detectionApp.route('/detection/peryear/<year>')
def per_year(year):
    cam = Camera.query.all()
    result = {}
    sum_values = [0] * 12

    for c in cam:
        row = [0] * 12
        for i in range(12):
            month = "{0}-{1:02d}".format(year, i + 1)                   #构建年月字符串，月份不足两位要在前面补0
            result_in = select_by_month_cam(month, "0", str(c.id))      #查询每月入的记录
            sum_month = sum(s.sum() for s in result_in)                         #计算每月总人次
            row[i] = sum_month
            sum_values[i] += sum_month                                          # 更新总和数组
        result[c.id] = row                                                      #一个摄像头的12个月的
    result[0] = sum_values                                                      # 将总人次加入集合, 0 表示总人次
    return result