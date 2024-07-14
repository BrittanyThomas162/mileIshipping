from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db
from datetime import datetime, timezone


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer')

    authorized_pickup_list = db.relationship('AuthorizedPickUp', back_populates='user', lazy='dynamic')
    prealerts = db.relationship('Prealert', backref='user', lazy=True)
    packages = db.relationship('Package', back_populates='user', lazy=True)
    action_required = db.relationship('ActionRequired', back_populates='user', lazy=True)

    def __init__(self, first_name, last_name, email, phone, password, role='customer'):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        self.role = role

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<User %r>' % (self.email)


class ShippingRate(db.Model):
    __tablename__ = 'shipping_rates'
    id = db.Column(db.Integer, primary_key=True)
    pounds = db.Column(db.String(10), unique=True, nullable=False)
    usd = db.Column(db.Float, nullable=False)
    jmd = db.Column(db.Float, nullable=False)


class AuthorizedPickUp(db.Model):
    __tablename__ = 'authorized_pickups'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(15), nullable=False)
    id_type = db.Column(db.String(50), nullable=False)
    id_number = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', back_populates='authorized_pickup_list')


class Prealert(db.Model):
    __tablename__ = 'prealerts'  # Make sure the table name is correct
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    carrier = db.Column(db.String(50), nullable=False)
    tracking_number = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    value = db.Column(db.Float, nullable=True)
    invoice = db.Column(db.String(255), nullable=True)
    

class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    item_number = db.Column(db.String(20), unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False)
    sender = db.Column(db.String(100), nullable=True)
    date_received = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    invoice = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    user = db.relationship('User', back_populates='packages')


class ActionRequired(db.Model):
    __tablename__ = 'action_required'
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    item_number = db.Column(db.String(20), unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False)
    sender = db.Column(db.String(100), nullable=True)
    date_received = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    invoice = db.Column(db.String(255), nullable=True)
    reason = db.Column(db.String(255), nullable=False)
    action_needed = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    user = db.relationship('User', back_populates='action_required')
