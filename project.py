from app import app,db
from app.models import User,Stats,UserActivity

@app.shell_context_processor
def make_shell_context():
	return {'db':db, 'User':User, 'Stats':Stats, 'UserActivity':UserActivity}

if __name__ == '__main__':
	app.run()
