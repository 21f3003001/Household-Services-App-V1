# models.py
from sqlalchemy import ForeignKey
from sqlalchemy import func, Enum
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    date_created = db.Column(db.DateTime, default=func.now(), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='Active')  # Possible values: 'Active', 'Blocked'
    role = db.Column(db.String(50), nullable=False)
    

    def set_password(self, password):
        self.password = generate_password_hash(password)

class ProfessionalStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ServiceProfessional(UserMixin, db.Model):
    __tablename__ = 'service_professionals'
    
    prof_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)  # Auto-increment primary key
    username = db.Column(db.String(255), unique=True, nullable=False)  # Unique username
    password = db.Column(db.String(200), nullable=False)  # Store hashed password
    prof_name = db.Column(db.String(250), nullable=False)  # Name of the professional
    service_type = db.Column(db.String(100), nullable=False)  # Type of service offered
    experience = db.Column(db.String(100), nullable=False)  # Years of experience
    address = db.Column(db.Text, nullable=False)  # Address
    contact = db.Column(db.String(15), nullable=False)  # Contact number
    pincode = db.Column(db.String(10), nullable=False)  # Pincode/ZIP code
    date_created = db.Column(db.DateTime, default=func.now(), nullable=False)  # Automatically set to current timestamp
    status = db.Column(db.Text, default=ProfessionalStatus.PENDING, nullable=False)  # Status stored as text
    role = db.Column(db.String(50), default='service_professional', nullable=False)

    service_requests = db.relationship('ServiceRequest', backref='service_professionals', lazy=True)


    def __repr__(self):
        return f"<ServiceProfessional(prof_id={self.prof_id}, name='{self.name}', service_type='{self.service_type}', status='{self.status}')>"

    # Helper to validate status
    @staticmethod
    def is_valid_status(status):
        """Check if the given status is valid."""
        return status in [e.value for e in ProfessionalStatus]

    # Setter for status with validation
    def set_status(self, status):
        """Set the status for the professional, ensuring it is valid."""
        if isinstance(status, ProfessionalStatus):
            self.status = status.value
        elif isinstance(status, str) and self.is_valid_status(status):
            self.status = status
        else:
            raise ValueError(f"Invalid status value: {status}")

    # Getter to return the status as an enum
    def get_status(self):
        """Get the status as a ProfessionalStatus enum."""
        return ProfessionalStatus(self.status)


#user_id = db.Column(db.Integer, ForeignKey('users.user_id'), nullable=True)
    #service_id = db.Column(db.Integer, ForeignKey('service.service_id'), nullable=True)

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    user = db.relationship('User', backref='customer_profile')

#Customer_dashboard
#Admin_dashboard

class Service(db.Model):
    __tablename__ = 'service'
    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), default=1, nullable=True)
    prof_id = db.Column(db.Integer, db.ForeignKey('service_professionals.prof_id'), default=1, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    new_service_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.String(255), nullable=True)

    # professionals = db.relationship('ServiceProfessional', backref='service', lazy=True)

    def __repr__(self):
        return f"<Service {self.name}>"


class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    req_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id'), nullable=True)
    prof_id = db.Column(db.Integer, db.ForeignKey('service_professionals.prof_id'), nullable=True)
    status = db.Column(db.String(20), default='Requested', nullable=False)
    rating = db.Column(db.Integer)
    remarks = db.Column(db.String(255))
    requested_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    close_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    service = db.relationship('Service', backref='requests')
    professional = db.relationship('ServiceProfessional', backref='requests')


    def __repr__(self):
        return f"<ServiceRequest {self.id}>"
    

    
