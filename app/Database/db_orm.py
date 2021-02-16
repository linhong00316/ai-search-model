# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from app import db



class TblModel(db.Model):
    __tablename__ = 'Tbl_model'

    id_model = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), server_default=db.FetchedValue())
    sex = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    mail = db.Column(db.String(100))
    face_encoding = db.Column(db.JSON)
    pic_path = db.Column(db.String(100))

    def get_dict(self):
        return {
            'id_model':self.id_model,
            'name':self.name,
            'sex':self.sex,
            'mail':self.mail,
            'face_encoding':self.face_encoding,
            'pic_path':self.pic_path
        }