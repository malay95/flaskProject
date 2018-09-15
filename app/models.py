from app import db,login
from datetime import datetime 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	stat = db.relationship('Stats', backref='User', lazy='dynamic')
	activity = db.relationship('UserActivity', backref='User', lazy='dynamic')

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Stats(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	login_timestamp = db.Column(db.DateTime, index=True)
	logout_timestamp = db.Column(db.DateTime, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Stat {}>'.format(self.user_id)

class UserActivity(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	eventName = db.Column(db.String(32))
	parameter = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<UserActivity {}>'.format(self.eventName)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))
