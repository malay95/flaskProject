from app import app,db
from flask import render_template, request, redirect, url_for, flash
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User,  Stats
from datetime import datetime


@app.route('/')
@app.route('/index')
@login_required
def index():
	posts = [
		{
			'author': {'username':'darsh'},
			'post':'saras'
		},
		{
			'author': {'username':'dharmin'},
			'post' : 'movie is cool'
		}
	]
	return render_template('index.html', title="Home Page", posts =posts)

@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('/index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('/login'))
		login_user(user)
		stat = Stats(login_timestamp = datetime.now())
		db.session.add(user)
		db.session.commit()
		next_page = request.args.get('next')
		# check if the value in the next parameter is null, next page or a whole domain
		# the domain in checked using netloc
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('/index')
		return redirect(next_page)
	return render_template('login.html',title='Sign In', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		stat = Stats(login_timestamp = datetime.now())
		db.session.add(user)
		db.session.add(user)
		db.session.commit()
		flash('congratulations, you are in the database')
		return redirect(url_for('index'))
	return render_template('register.html',title='register', form=form)

@app.route('/logout')
def logout():
	logout_user()
	stat = Stats(logout_timestamp = datetime.now())
	return redirect(url_for('index'))