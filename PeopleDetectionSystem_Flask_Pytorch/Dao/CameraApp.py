from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import SQLAlchemyError

from Database.dbs import db
from Dao.Camera import Camera

camera_app = Blueprint('camera', __name__)

allow_through=['/camera', '/camera/<int:camera_id>']

@camera_app.route('/camera', methods=['GET'])
def get_all_cameras():
    cameras = Camera.query.all()

    camera_list = [dict(camera) for camera in cameras]
    return jsonify(camera_list)

@camera_app.route('/camera/<int:camera_id>', methods=['GET'])
def get_camera(camera_id):
    camera = Camera.query.get(camera_id)
    if camera:
        return jsonify(dict(camera))
    else:
        return jsonify({"message": "Camera not found"}), 404

@camera_app.route('/camera/save', methods=['POST'])
def add_camera():
    try:
        data = request.json
        camera = Camera(
            id = data.get('id'),
            name=data.get('name'),
            ip=data.get('ip'),
            positionx=data.get('positionx'),
            positiony=data.get('positiony'),
            describe1=data.get('describe1'),
            outputPath=data.get('outputPath'),
            rtmp_server=data.get('rtmp_server')
        )

        db.session.add(camera)
        db.session.commit()

        return jsonify(True), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e.__dict__.get('orig') or e)
        return jsonify({'error': error}), 500

@camera_app.route('/camera/update', methods=['post'])
def update_camera():
    try:
        data = request.json
        camera_id = data.get('id')

        camera = Camera.query.get(camera_id)
        if camera:
            camera.name = data.get('name')
            camera.ip = data.get('ip')
            camera.positionx = data.get('positionx')
            camera.positiony = data.get('positiony')
            camera.describe1 = data.get('describe1')
            camera.outputPath = data.get('outputPath')

            db.session.commit()
            return jsonify(True), 200
        else:
            return jsonify(False), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e.__dict__.get('orig') or e)
        return jsonify({'error': error}), 500

@camera_app.route('/camera/delete/<int:camera_id>', methods=['post'])
def delete_camera(camera_id):
    try:
        camera = Camera.query.get(camera_id)
        if camera:
            db.session.delete(camera)
            db.session.commit()
            return jsonify(True), 200
        else:
            return jsonify(False), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e.__dict__.get('orig') or e)
        return jsonify({'error': error}), 500


@camera_app.before_request
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
    elif usertype == "visitor":
        if request.path == "/api/user/login":  # 登录后重新登录也可以
            return
        else:  # 其他情况 拦截
            return jsonify(message="Forbidden"), 403
    else:
        return jsonify(message="Unauthorized"), 401