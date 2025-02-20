# -*- coding: utf-8 -*-
from Database.dbs import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    password = db.Column(db.String(24))
    usertype = db.Column(db.String(32))
    avatar = db.Column(db.String(24))
    remark = db.Column(db.String(24))
    phone = db.Column(db.String(24))
    def __init__(self, id, name, password, usertype,avatar,remark,phone):
        self.id = id
        self.name = name
        self.password = password
        self.usertype = usertype
        self.avatar = avatar
        self.remark = remark
        self.phone = phone

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.name

    def keys(self):
        return ('id','name', 'password','usertype','avatar','remark','phone')

    def __getitem__(self, item):
        return getattr(self, item)


