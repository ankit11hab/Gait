from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username already exists')

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# Module Form
class ModuleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Submit')


# PDF Form
class PdfForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    pdf = FileField('PDF', validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Submit')


# Image Form
class ImageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')


# Video Form
class VideoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    video = FileField('Video', validators=[FileAllowed(['mp4', 'mov', 'wmv', 'avi'])])
    submit = SubmitField('Submit')