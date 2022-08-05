from enum import unique
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from main import db, login_manager,app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bookings = db.relationship('Booking',backref='user',lazy=True)
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"
    
class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(15), nullable=False)
    latitude = db.Column(db.Float,nullable=False)
    longitude = db.Column(db.Float,nullable=False)
    availability = db.Column(db.Integer,nullable=False)
    price = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String(5000))
    bookings = db.relationship('Booking',backref='hotel',lazy=True)
    
    def __repr__(self):
        return f"User('{self.name}', '{self.city}','{self.availability}')"
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    touirst_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable= False)
    hotel_id = db.Column(db.Integer,db.ForeignKey('hotel.id'), nullable= False)
    arrival = db.Column(db.DateTime,nullable=False)
    departure = db.Column(db.DateTime,nullable=False)
    rooms = db.Column(db.Integer,nullable=False)
    
    def __repr__(self):
        return f"User('{self.id}', '{self.touirst_id}','{self.hotel_id}')"