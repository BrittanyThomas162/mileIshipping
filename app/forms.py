from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp
from .models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=10, message="Phone number must be 10 digits."),
        Regexp(r'^\d{10}$', message="Phone number must be 10 digits without any special characters.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long."),
        Regexp(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,}', message="Password must contain at least one digit, one lowercase letter, one uppercase letter, and one special character.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use. Please use a different one.')
