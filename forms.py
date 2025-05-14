from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, IntegerField, TextAreaField, DateTimeField, SearchField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User, Team, Player

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class TeamRegistrationForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired(), Length(max=100)])
    division = SelectField('Division', choices=[
        ('senior_men', 'Senior Men'),
        ('senior_women', 'Senior Women'),
        ('junior_boys', 'Junior Boys'),
        ('junior_girls', 'Junior Girls')
    ], validators=[DataRequired()])
    founded_year = IntegerField('Founded Year', validators=[Optional()])
    logo = FileField('Team Logo', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Register Team')
    
    def validate_name(self, name):
        team = Team.query.filter_by(name=name.data).first()
        if team:
            raise ValidationError('Team name already taken. Please choose a different one.')

class PlayerRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    position = SelectField('Position', choices=[
        ('', 'Select Position'),
        ('goalkeeper', 'Goalkeeper'),
        ('defender', 'Defender'),
        ('midfielder', 'Midfielder'),
        ('forward', 'Forward')
    ], validators=[DataRequired()])
    jersey_number = IntegerField('Jersey Number', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    photo = FileField('Player Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    team_id = SelectField('Team', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register Player')

class EventRegistrationForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    location = StringField('Location', validators=[DataRequired(), Length(max=120)])
    start_date = DateTimeField('Start Date and Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_date = DateTimeField('End Date and Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    registration_deadline = DateTimeField('Registration Deadline', format='%Y-%m-%d %H:%M', validators=[Optional()])
    submit = SubmitField('Create Event')

class TeamEventRegistrationForm(FlaskForm):
    team_id = SelectField('Team', coerce=int, validators=[DataRequired()])
    event_id = SelectField('Event', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register Team for Event')

class NotificationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    content = TextAreaField('Content', validators=[DataRequired()])
    is_global = BooleanField('Send to all teams')
    target_team_id = SelectField('Target Team', coerce=int, validators=[Optional()])
    submit = SubmitField('Send Notification')
    
class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired(), Length(min=2, max=100)])
    category = SelectField('Category', choices=[
        ('all', 'All'),
        ('teams', 'Teams'),
        ('players', 'Players'),
        ('events', 'Events')
    ], default='all')
    submit = SubmitField('Search')
    
class AdminRegistrationForm(FlaskForm):
    username = StringField('Admin Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Admin Email', validators=[DataRequired(), Email()])
    password = PasswordField('Admin Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    admin_code = PasswordField('Admin Code', validators=[DataRequired()])
    submit = SubmitField('Register as Admin')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please use a different one.')
