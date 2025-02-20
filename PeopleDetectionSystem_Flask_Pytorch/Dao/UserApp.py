# -*- coding: utf-8 -*-
import os

from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from Dao.User import User
from Database.dbs import db
from flask import Blueprint,session
allow_through = ['/login', '/logout']

userApp = Blueprint('user', __name__, template_folder='templates')

@userApp.route('/login',methods=['GET','POST'])
def login():
    data = request.json
    print(data)
    username = data.get('name')
    password = data.get('password')
    users = User.query.filter_by(name=username, password=password).first()
    if users is not None and users.password == password:
        # 登录成功
        user_data = {
            "name": username,
            "usertype": users.usertype,  # 用户类型示例
            "remark": users.remark,  # 用户备注信息示例
            "avatar": users.avatar ,  # 用户头像示例
            "phone":  users.phone  # 用户手机号示例
        }
        session['usertype'] = users.usertype
        return jsonify({"status": 200, **user_data})
    elif users is not None:
        return jsonify({"status": 1})
    else:
        return jsonify({"status": 2})

@userApp.route('/user',methods=['GET','POST'])
def getAllUser():
    all_user = User.query.all();
    list = [dict(i) for i in all_user]
    return jsonify(list)

@userApp.route('/user/update',methods=['POST'])
def update_user():
    try:
        data = request.json
        user_id = data.get('id')

        user = User.query.get(user_id)
        if user:
            user.name = data.get('name')
            user.password = data.get('password')
            user.usertype = data.get('usertype')
            user.avatar = data.get('avatar')
            user.remark = data.get('remark')
            user.phone = data.get('phone')
            db.session.commit()
            return jsonify(True), 200
        else:
            return jsonify(False), 404
    except SQLAlchemyError as e:
        db.session.rollback()  # 回滚会话，撤销所有未提交的更改
        error = str(e.__dict__.get('orig') or e)
        return jsonify({'error': error}), 500

@userApp.route('/user/save', methods=['POST'])
def add_user():
    try:
        data = request.json

        user = User(
            id=data.get('id'),
            name=data.get('name'),
            password=data.get('password'),
            usertype=data.get('usertype'),
            avatar=data.get('avatar'),
            remark=data.get('remark'),
            phone=data.get('phone')
        )

        db.session.add(user)
        db.session.commit()

        return jsonify(True), 200
    except SQLAlchemyError as e:
        db.session.rollback()  # 回滚会话，撤销所有未提交的更改
        error = str(e.__dict__.get('orig') or e)
        return jsonify({'error': error}), 500

@userApp.route('/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify(True), 200
        else:
            return jsonify(False), 404
    except SQLAlchemyError as e:
        db.session.rollback()  # 回滚会话，撤销所有未提交的更改
        error = str(e.__dict__.get('orig') or e)
        return jsonify({'error': error}), 500
from flask import request, jsonify

@userApp.before_request
def check_authorization():
    # 除了登录请求外，其他请求只有管理员才能访问
    current_path = request.path
    if current_path in allow_through:
        return
    usertype = session.get("usertype")
    if usertype is None:  # 未登录
        if request.path == "/api/user/login":  # 登录请求则放行
            return
        else:  # 其他情况 拦截
            return jsonify(message="Unauthorized"), 401
    elif usertype == "administrator":  # 管理员放行
        return
    elif usertype == "common":
        if request.path == "/api/user/login":  # 登录后重新登录也可以
            return
        else:  # 其他情况 拦截
            return jsonify(message="Forbidden"), 403
    else:
        return jsonify(message="Unauthorized"), 401
