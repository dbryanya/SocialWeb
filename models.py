from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    Fname = db.Column(db.String(64), nullable=False)
    Sname = db.Column(db.String(64), nullable=False)

    profile_pic = db.Column(db.String(200), nullable=True)
    about_me = db.Column(db.String(200), nullable=True)
    
    is_active = db.Column(db.Boolean(), default=True)

    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return self.is_active
    
    @property
    def is_anonymous(self):
        return True
    

from datetime import datetime
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
