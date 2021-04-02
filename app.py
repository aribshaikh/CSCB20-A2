import sqlite3
from flask import Flask, render_template, request, g,session, redirect, url_for, escape

DATABASE = 'assignment3.db'

# connects to the database
def get_db():
    # if there is a database, use it
    db = getattr(g, '_database', None)
    if db is None:
        # otherwise, create a database to use
        db = g._database = sqlite3.connect(DATABASE)
    return db

# converts the tuples from get_db() into dictionaries
# (don't worry if you don't understand this code)
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# given a query, executes and returns the result
# (don't worry if you don't understand this code)
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# tells Flask that "this" is the current running app
app = Flask(__name__)
app.secret_key=b'abbas'

# this function gets called when the Flask app shuts down
# tears down the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()

@app.route('/')
def index():
	if 'username' in session:
		return render_template("index.html")
	return redirect(url_for('login'))

@app.route('/calendar')
def calendar():
	if 'username' in session:
		return render_template("calendar.html")
	return redirect(url_for('login'))

@app.route('/lectures')
def lectures():
	if 'username' in session:
		return render_template("lectures.html")
	return redirect(url_for('login'))

@app.route('/tutorials')
def tutorials():
	if 'username' in session:
		return render_template("tutorials.html")
	return redirect(url_for('login'))

@app.route('/assignments')
def assignments():
	if 'username' in session:
		return render_template("assignments.html")
	return redirect(url_for('login'))

@app.route('/feedback')
def tests():
	if 'username' in session:
		return render_template("feedback.html")
	return redirect(url_for('login'))

@app.route('/remark')
def links():
	if 'username' in session:
		return render_template("remark.html")
	return redirect(url_for('login'))

@app.route('/grades')
def retrieveGrades():
	if 'username' in session:
		student_session = session.get('student')
		instructor_session = session.get('instructor')
		db = get_db()
		db.row_factory = make_dicts
		if student_session:
			student_grades = query_db(
				"SELECT mark_id, mark FROM marks WHERE susername = ?",[session['username']] , one=False)
			db.close()
			return render_template("grades.html", student_grades = student_grades)

	
	return render_template("grades.html")

@app.route('/remarkRequest', methods=['GET','POST'])
def remarkRequest():
	# if 'username' in session:

	student_session = session.get('student')
	instructor_session = session.get('instructor')
	render_template('grades.html')
	username = session.get('student')
	assignment = request.form.get('aName')
	reason = request.form.get('reason')
		# if (assignment == 'Select an evaluation') or (reason == ''):
		# 	return redirect(url_for('remark'))

		# else:
	db = get_db()
	db.row_factory = make_dicts
		# insert into db

	if request.method=='POST':

		query_db("INSERT INTO remark_requests (susername, mark_id, comment) VALUES (?, ?, ?)", [
			username, assignment, reason])
		db.commit()
		db.close()
		return redirect("/grades")
	return redirect("/login")

@app.route('/sendFeedback', methods=['GET','POST'])
def sendFeedback():
	# if 'username' in session:

	student_session = session.get('student')
	instructor_session = session.get('instructor')
	instructor = request.form.get('instructorname')
	feedback1 = request.form.get('feedback1')
	feedback2 = request.form.get('feedback2')
	feedback3 = request.form.get('feedback3')
	feedback4 = request.form.get('feedback4')


		# if (assignment == 'Select an evaluation') or (reason == ''):
		# 	return redirect(url_for('remark'))

		# else:
	db = get_db()
	db.row_factory = make_dicts
		# insert into db

	if request.method=='POST':

		query_db("INSERT INTO feedback (iusername, question, comment) VALUES (?, ?, ?)", [
			instructor, 'What do you like about the instructor teaching?', feedback1])
		db.commit()
		db.close()
		return redirect("/")
	return redirect("/login")

@app.route('/register',methods=['GET','POST'])
def register():
	if 'username' in session:
		return redirect(url_for('index'))
	elif request.method=="POST":
		username=request.form['username']
		password=request.form['password']
		usertype=request.form['usertype']+"s"
		lecsession=request.form['session']
		sql1 = "select * from ?"
		results = query_db(sql1, [usertype])
		if len(username)<1:
			error="please enter a username"
			return render_template("register.html", error=error)
		elif len(password)<1:
			error="please enter a password"
			return render_template("register.html", error=error)
		elif usertype not in ("students", "instructors"):
			error="please pick a user type"
			return render_template("register.html", error=error)
		for result in results:
			if result[0]==username:
				error=username+"is already taken, please pick a different one"
				return render_template("register.html", error=error)
		sql2="insert into ? values('?','?', '?')"
		insert=query_db(sql2, [usertype, username, password, lecsession])
		return redirect(url_for('login'))	
	else:
		return render_template("register.html")

@app.route('/login',methods=['GET','POST'])
def login():
	error=None
	if request.method=='POST':
		sql = """
			SELECT *
			FROM students
			"""
		
		# For the student case
		session['student'] = True
		session['instructor'] = False

		results = query_db(sql, args=(), one=False)
		for result in results:
			if result[0]==request.form['username']:
				if result[1]==request.form['password']:
					session['username']=request.form['username']
					return redirect(url_for('index'))
		error="Incorrect username or password"
		return render_template('login.html', error=error)
	elif 'username' in session:
		return redirect(url_for('index'))
	else:
		return render_template("login.html")

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('login'))

if __name__=="__main__":
	app.run(debug=True,host='0.0.0.0')