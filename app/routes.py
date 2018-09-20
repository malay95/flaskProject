from app import app,db
from flask import render_template, request, redirect, url_for, flash, session
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User,  Stats, UserActivity
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import numpy as np
import base64
import io
import pandas as pd
from bokeh.charts import Histogram, Bar
from bokeh.embed import components

token = 0
data = pd.DataFrame()



@app.route('/index')
@login_required
def index():
	if not current_user.is_authenticated:
		flash("user not logged in")
		return redirect(url_for('login'))
	stats = Stats.query.filter_by(user_id = current_user.get_id()).order_by(Stats.login_timestamp.desc()).limit(5).all()
	url = "https://stackoverflow.com/questions/tagged/java?sort=frequent&pageSize=15&token=" + current_user.get_id()
	data = save_data()	
	data['count/time'] = data['count/time'].apply(int)
	user_data = data[data['username'] == current_user.username]
	other_data = data[data['username'] != current_user.username]
	other_data['username'] = 'other'
	final_data = pd.concat([user_data,other_data])
	user_data = user_data.drop(['username'],axis=1)
	user_data['count/time'] = user_data['count/time'].apply(int)
	user_data = user_data.groupby(['eventName']).mean().reset_index()
	final_data = final_data.drop(['timestamp'],axis=1)
	final_data = final_data.groupby(['eventName','username']).mean().reset_index()
	final_data = final_data.rename(index=str, columns={'count/time':'parameter'})
	# print(final_data.to_dict('records'))
	return render_template('index.html', title="Home Page", stats =stats, user=current_user.get_id(), token=url, final_list = user_data, all_data=final_data.to_dict('records'))

@app.route('/readme')
def readme():
	return render_template('readme.html')

@app.route('/database_snap')
def database_snap():
	data = save_data()
	user_data = data[data['username']== current_user.username]
	return render_template('result.html', final_list=user_data)

@app.route('/')
@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user,True)
		print(user)
		# session['logged_in_user'] = True
		flash("User logged in.")
		stat = Stats(login_timestamp = datetime.now(), user_id=current_user.get_id())
		db.session.add(stat)
		db.session.commit()
		next_page = request.args.get('next')

		# check if the value in the next parameter is null, next page or a whole domain
		# the domain in checked using netloc
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
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
		stat = Stats(login_timestamp = datetime.now(), user_id=current_user.get_id())
		db.session.add(user)
		db.session.add(stat)
		db.session.commit()
		flash('congratulations, you are in the database')
		# session['logged_in_user'] = True
		return redirect(url_for('index'))
	return render_template('register.html',title='register', form=form)

@app.route('/logout')
@login_required
def logout():
	s = Stats.query.filter_by(user_id=current_user.get_id())	
	s[-1].logout_timestamp = datetime.now()
	db.session.commit()
	print(session)
	logout_user()
	session.clear()
	print(session)
	flash('You have successfully logged yourself out.')
	return redirect(url_for('login'))

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/api', methods=['GET','POST'])
def api():
	global token
	data = request.form
	if data.get('event') == 'store_token':
		print(data)
		token = data.get('token')
	elif data.get('event') == 'time event':
		log = UserActivity(eventName= data.get('event'), parameter=data.get('time'), user_id = token, timestamp=datetime.now())
		db.session.add(log)
		db.session.commit()
		flash('log added')
	else:
		print(data.get('event'))
		log = UserActivity.query.filter_by(eventName=data.get('event'), user_id = token).first()
		if log is not None:
			print(log)
			log.parameter +=1
			log.timestamp = datetime.now()
		else:
			log = UserActivity(eventName=data.get('event'), parameter = 1, user_id= token, timestamp=datetime.now())
			db.session.add(log)
		db.session.commit()
	print('token-{}'.format(token))
	return redirect(url_for('index'))

@app.route('/chart')
def graph():
	users = ['lll']
	#get the scroll_up of all the users and show a bar chart
	label = []
	for user in users:
		res = User.query.filter_by(username = user)
		label.append(res.id)
	events = ['scroll_down event', 'click event']
	values = []
	for event in events:
		v = []	
		for u in range(users+1):
			res = UserActivity.query.filter_by(eventName=event, user_id = u).first()
			if res is not None:
				v.append(res.parameter)
			else:
				v.append(0)
		values.append(v)
	colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
	return render_template('chart1.html', title="hello", max=17000, values=values, labels=labels, label=label)

@app.route('/matplot')
def matplot():
	users = ['lll','malay']
	res = User.query.with_entities(User.id).filter(User.username.in_(users)).all()
	user_ids = [x.id for x in res]
	print(user_ids)
	events = ['scroll_down event', 'scroll_up event','star click event']
	y = [3,4,5]
	bars = []
	for e in events:
		bar = []
		for user in user_ids:
			res = UserActivity.query.filter_by(eventName=e, user_id=user).first()
			bar.append(0 if res is None else res.parameter)
		bars.append(bar)
	print(bars)
	graph_1_url = build_graph(events,y)
	return render_template('graphs.html', graphs = graph_1_url)

def build_graph(x,y):
	# plt.bar(x1,bars1, color='#7f6d5f', width=0.25, edgecolor='white', label='var1')
	# plt.bar(x2,bars2, color='#557f2f', width=0.25, edgecolor='white', label='var2')
	plt.bar(x,y,align='center')
	plt.xticks(x)
	plt.ylabel('Count')
	plt.savefig('./assets/img.png', format='png')


def save_data():
	users = User.query.all()
	final_list=[]
	for user in users:
		user_activities =  user.activity.all()
		for activity in user_activities:
			row = {}
			row['username'] = user.username
			row['eventName'] = activity.eventName
			row['count/time'] = activity.parameter
			row['timestamp'] = activity.timestamp
			final_list.append(row)
	df = pd.DataFrame(final_list)
	df = df[df['count/time'] != ""]
	df.to_csv('data.csv')
	return df

@app.route('/bo_graph')
def bo_graph():
	data = save_data()
	data_bo = data[data['eventName'] != "time event"]
	data_bo['count/time'] = data_bo['count/time'].apply(int)
	pv = pd.pivot_table(data=data_bo, index='username', values='count/time', columns = 'eventName')
	pv['username'] = pv.index
	current_event = request.args.get('event_name')
	if current_event == None:
		current_event = "scroll_up event"

	plot = create_figure(pv, current_event)
	script, div = components(plot)
	return render_template('bokeh.html', script=script, div=div, event_names = pv.columns[:-1], current_event = current_event)
	# return render_template('result.html', final_list=pv)

def create_figure(data, current_feature_name):
	p = Bar(data, values=current_feature_name, title=current_feature_name, color = 'username', legend='top_right', width=600, height=400)
	# Set the y axis label
	p.yaxis.axis_label = current_feature_name
	return p
