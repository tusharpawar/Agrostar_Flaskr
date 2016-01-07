#all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for,abort, render_template, flash

#to connect to db automatically
from contextlib import closing

#configuration
DATABASE ='/tmp/flaskr.db'
DEBU =True
SECRET_KEY ='development key'
USERNAME = 'admin'
PASSWORD='default'

#create application:
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

#for db_connection
def init_db():
	with closing(connect_db())as db:
		with app.open_resource('schema.sql',mode='r')as f:
			db.cursor().executescript(f.read())
		db.commit()


#decorators for db connection and closing
@app.before_request
def before_request():
	g.db=connect_db()

#@app.teardown_requet
def teardown_request():
	db=getattr(g,'db',None)
	if db is not None:
		db.close()

#views
@app.route('/')
def show_entries():
	try:
		cur=g.db.execute('select title,text from entries order by id desc')
		entries=[dict(title=row[0],text=row[1])for row in cur.fetchall()]
		print 'in show_entries'
		return render_template('show_entries.html',entries=entries)
	except Exception as e:
		print e


@app.route('/add',methods=['POST'])
def add_entry():
	if session.get('logged_in'):
		
		g.db.execute('insert into entries(title,text) values(?,?)',[request.form['title'],request.form['text']])
		g.db.commit()
		flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET','POST'])
def login():
        try:
		error=None
		if request.method=='POST':
			if request.form['username']!=app.config['USERNAME']:
				error='Invalid username'
				
			elif request.form['password']!=app.config['PASSWORD']:
				error='Invalid password'
			else:
			
				session['logged_in']=True
				
				flash('You were logged in')
		
				return redirect(url_for('show_entries'))
			print error
		return render_template('login.html',error=error)
	except Exception as e:
		print e




@app.route('/logout')
def logout():
	session.pop('logged_in',None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

		
if __name__ =='__main__':
	init_db()
	app.run()

