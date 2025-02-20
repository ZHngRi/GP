# -*- coding: utf-8 -*-
import os

from flask import Flask, Response
from flask_script import Manager

from Dao.CameraApp import camera_app
from Dao.DetectionApp import detectionApp
from Database import config
from Database.dbs import db
from Dao.UserApp import userApp


app = Flask(__name__)



app = Flask(__name__)
# def make_shell_context():
#     return dict(app=app, db=db, user=User)
with app.app_context():
    app.secret_key = os.urandom(24)
    app.register_blueprint(userApp)
    app.register_blueprint(camera_app)
    app.register_blueprint(detectionApp)
    app.config.from_object(config)
    manager = Manager(app)
    db.init_app(app)
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0')