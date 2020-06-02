from . import db
from sqlalchemy.dialects import postgresql

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask import current_app as app
from passlib.apps import custom_app_context as pwd_context

from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects.postgresql import ARRAY

class MutableList(Mutable, list):
    """
    https://kirang.in/post/creating-a-mutable-array-data-type-in-sqlalchemy/
    """
    def append(self, value):
        list.append(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000))
    password = db.Column(db.String(1000))
    is_admin = db.Column(db.Boolean, default=False)
    calculation_ids = db.Column(MutableList.as_mutable(ARRAY(db.Integer)))

    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def __repr__(self):
        return '<User {}>'.format(self.username)



class Calculation(db.Model):
    __tablename__ = 'calculations'
    id = db.Column(db.Integer, primary_key=True)
    array = db.Column(postgresql.ARRAY(db.Integer))
    calculations = db.Column(postgresql.ARRAY(db.Integer))
    
    # method for json serialization
    def serialize(self):
        return {
            'id': self.id, 
            'array': self.array,
            'calculations': self.calculations,
        }
