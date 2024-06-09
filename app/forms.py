from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FieldList, FloatField, FormField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp, NumberRange, Optional
from .models import User
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

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
        

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=10, message="Phone number must be 10 digits."),
        Regexp(r'^\d{10}$', message="Phone number must be 10 digits without any special characters.")
    ])
    submit = SubmitField('Save Changes')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        print(current_user)
        if user and user.id != current_user.id:
            raise ValidationError('Email is already in use. Please use a different one.')


class RateForm(FlaskForm):
    pounds = StringField('Pounds', validators=[DataRequired()])
    usd = FloatField('USD', validators=[DataRequired(), NumberRange(min=0)])
    jmd = FloatField('JMD', validators=[DataRequired(), NumberRange(min=0)])

class UpdateRatesForm(FlaskForm):
    rates = FieldList(FormField(RateForm))
    submit = SubmitField('Save Changes')

class AuthorizePickUpForm(FlaskForm):
    id = HiddenField('ID')
    name = StringField('Name', validators=[DataRequired()])
    telephone = StringField('Telephone', validators=[DataRequired()])
    id_type = SelectField('ID Type', choices=[
        ('', 'Select'),
        ('Driver\'s License', 'Driver\'s License'),
        ('National ID', 'National ID'),
        ('Other', 'Other'),
        ('Passport', 'Passport')
    ], validators=[DataRequired()])
    id_number = StringField('ID Number', validators=[DataRequired()])
    submit = SubmitField('Save')


class PrealertForm(FlaskForm):
    carrier = SelectField('Carrier', choices=[
        ('', '-- Select Carrier --'),
        ('Amazon Logistics', 'Amazon Logistics'),
        ('China Post', 'China Post'),
        ('DHL', 'DHL'),
        ('DSG', 'DSG'),
        ('FedEx', 'FedEx'),
        ('Hong Kong Post', 'Hong Kong Post'),
        ('IBC', 'IBC'),
        ('Korea Post', 'Korea Post'),
        ('Lasership', 'Lasership'),
        ('Major Express', 'Major Express'),
        ('Royal Mail', 'Royal Mail'),
        ('TRX', 'TRX'),
        ('UPS', 'UPS'),
        ('US Postage', 'US Postage'),
        ('USPS', 'USPS'),
        ('Other', 'Other')
    ], validators=[DataRequired(message="Please select a carrier.")])
    
    tracking_number = StringField('Tracking Number', validators=[DataRequired(message="Tracking number is required.")])
    
    description = StringField('Description', validators=[DataRequired(message="Description is required.")])
    
    value = FloatField('Value', validators=[DataRequired(message="Value is required.")])
    
    invoice = FileField('Upload Invoice', validators=[
        FileRequired(message="Please upload an invoice."),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], message="Only PDF, JPG, JPEG, and PNG files are allowed.")
    ])
    
    submit = SubmitField('Submit')

