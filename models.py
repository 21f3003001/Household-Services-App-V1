# models.py
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

class ServiceProfessional(db.Model):
    __tablename__ = 'service_professionals'
    
    prof_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Set autoincrement=True
    #user_id = db.Column(db.Integer, ForeignKey('users.user_id'), nullable=True)
    #service_id = db.Column(db.Integer, ForeignKey('service.service_id'), nullable=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  # Use func.current_date()
    


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    user = db.relationship('User', backref='customer_profile')

#Customer_dashboard
#Admin_dashboard

class Service(db.Model):
    __tablename__ = 'service'
    service_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    #prof_id = db.Column(db.Integer, db.ForeignKey('service_professionals.prof_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.String(255), nullable=True)

    # professionals = db.relationship('ServiceProfessional', backref='service', lazy=True)

    def __repr__(self):
        return f"<Service {self.name}>"


class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.Integer, primary_key=True)
    prof_id = db.Column(db.Integer, db.ForeignKey('service_professionals.prof_id'), nullable=True)  # Updated to reference service_professionals
    requested_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(1), nullable=False)  # R (Requested), A (Accepted), C (Closed)

    # Reference to the assigned professional (using the correct class name ServiceProfessional)
    assigned_professional = db.relationship('ServiceProfessional', backref='service_requests')

    def __repr__(self):
        return f"<ServiceRequest {self.id}>"
    

    
