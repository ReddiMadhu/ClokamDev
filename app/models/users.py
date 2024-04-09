from datetime import datetime
from app.extensions import db

user_events = db.Table(
    'user_events',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)
user_community = db.Table(
    'user_community',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('community_id', db.Integer, db.ForeignKey('community.id'), primary_key=True)
)
#User Schema
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50),nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contact = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Text(), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, default=0)
    awards = db.Column(db.Integer, default=0)
    hours = db.Column(db.Integer, default=0)
    date_of_birth = db.Column(db.Date)
    interested_in_volunteer = db.Column(db.Boolean, default=False)
    lives_in = db.Column(db.String(100))
    language = db.Column(db.String(50))
    profile_picture = db.deferred(db.Column(db.LargeBinary))
    events = db.relationship('Event', secondary=user_events, backref='users', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    
    def _init_(self,first_name,last_name,email, contact, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.contact = contact
        self.password = password

    
    def get_fullName(self):
        return f"{self.last_name}{self.first_name}"
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'contact': self.contact,
            'role': self.role,
            'points': self.points,
            'awards': self.awards,
            'hours': self.hours,
            'date_of_birth': self.date_of_birth.strftime('%d/%m/%Y') if self.date_of_birth else None,
            'interested_in_volunteer': self.interested_in_volunteer,
            'lives_in': self.lives_in,
            'language': self.language,
        }

class Community(db.Model):
    __tablename__ = 'community'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    reg_id = db.Column(db.String(50))
    link = db.Column(db.String(200))
    team = db.Column(db.String(200))
    about = db.Column(db.String(500))
    contact = db.Column(db.String(100))
    profile = db.deferred(db.Column(db.LargeBinary))
    users = db.relationship('User', secondary=user_community, backref='communities', lazy='dynamic')
    events = db.relationship('Event', backref='community', lazy='dynamic')
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "reg_id": self.reg_id,
            "link": self.link,
            "team": self.team,
            "about": self.about,
            "contact": self.contact,
            "user_id": self.user_id,
        }
# Event Model
class Event(db.Model):
    __tablename__ = 'event'
    name = db.Column(db.String(100), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    place = db.Column(db.String(200), nullable=False)
    profile = db.deferred(db.Column(db.LargeBinary))
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "date": self.date,
            "place": self.place,
            "community_id": self.community_id
            # Add other relevant attributes
        }
# Association table for users and events


#Token Table
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(500), nullable=True)  # Specify the maximum length for VARCHAR
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Token {self.jti}>"

    def save(self):
        db.session.add(self)
        db.session.commit()


# Join Request Model
class JoinRequest(db.Model):
    __tablename__ = 'join_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    user = db.relationship('User', backref='join_requests')
    community = db.relationship('Community', backref='join_requests')