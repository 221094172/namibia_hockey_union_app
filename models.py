from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association table for players and teams
player_team = db.Table('player_team',
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

# Association table for teams and events
team_event = db.Table('team_event',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teams = db.relationship('Team', backref='manager', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    division = db.Column(db.String(50), nullable=False)
    founded_year = db.Column(db.Integer)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logo_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    players = db.relationship('Player', secondary=player_team, lazy='subquery',
                            back_populates='teams')
    events = db.relationship('Event', secondary=team_event, lazy='subquery',
                           backref=db.backref('teams', lazy=True))
    
    def __repr__(self):
        return f'<Team {self.name}>'

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(64))
    jersey_number = db.Column(db.Integer)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    photo_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add explicit relationship to Team model via player_team association table
    teams = db.relationship('Team', secondary=player_team, lazy='subquery',
                         back_populates='players')
    
    def __repr__(self):
        return f'<Player {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref='created_events')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Event {self.name}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref='notifications')
    is_global = db.Column(db.Boolean, default=False)
    target_team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    target_team = db.relationship('Team', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title}>'
