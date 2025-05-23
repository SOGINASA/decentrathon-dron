import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True)
    city_lat = db.Column(db.Float, nullable=False)
    city_lng = db.Column(db.Float, nullable=False)    
    is_admin = False
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True)
    is_admin = True
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Drone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.String(100), primary_key=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_location = db.Column(db.String(100), nullable=False)
    end_location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False) # 'in_progress', 'completed', 'in_queue'
    cost = db.Column(db.Integer, nullable=False)

if __name__ == '__main__':
    db.create_all()