import sqlite3
from flask import Flask, render_template, request, g,session, redirect, url_for, escape, flash

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

@app.route('/tests')
def tests():
	if 'username' in session:
		return render_template("tests.html")
	return redirect(url_for('login'))

@app.route('/links')
def links():
	if 'username' in session:
		return render_template("links.html")
	return redirect(url_for('login'))

@app.route('/feedback')
def feedback():
	if 'username' in session:
		if session.get('instructor'):
			db = get_db()
			db.row_factory = make_dicts
			feedbacks = query_db("SELECT question, comment FROM feedback WHERE username = ?",[session['username']], one=False)
			db.close()
			return render_template("feedback.html", feedbacks = feedbacks)
		elif session.get('student'):
			db = get_db()
			db.row_factory = make_dicts
			instructors = query_db("SELECT username FROM instructors", one=False)
			print(instructors)
			return render_template("feedback.html",instructors = instructors, message=request.args.get('message'))
	return redirect(url_for('login'))

@app.route('/remark')
def remark():
	if 'username' in session:
		if session.get('instructor'):
			db = get_db()
			db.row_factory = make_dicts
			remarks = query_db("SELECT username, mark_id, comment, status FROM remark_requests", one=False)
			db.close()
			return render_template("remark.html", remarks = remarks)
		if session.get('student'):
			db = get_db()
			requests = query_db("SELECT mark_id, status FROM remark_requests where username=?"
				, [session['username']], one=False)
			db.close()
			return render_template("remark.html", requests = requests)
	return redirect(url_for('login'))

@app.route('/markAsDone', methods=['GET','POST'])
def markAsDone():
	if 'username' in session:
		if request.method=="POST":
			mark_id=request.form.get('mark_id')
			print(mark_id)
			db=get_db()
			db.row_factory = make_dicts
			query_db("update remark_requests set status = 'addressed' where username = ? and mark_id = ?"
				, [session.get('username'), mark_id])
			db.commit()
			db.close()
			print("hello")
			return redirect(url_for('remark'))
		else:
			return redirect(url_for('remark'))
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
				"SELECT mark_id, mark FROM marks WHERE username = ?",[session['username']] , one=False)
			db.close()
			return render_template("grades.html", student_grades = student_grades)
		if instructor_session:
			instructor_grades = query_db(
				"select s.username,	sum(case when m.mark_id = 'Q1' then m.mark end) Q1,	sum(case when m.mark_id = 'Q2' then m.mark end) Q2,	sum(case when m.mark_id = 'Q3' then m.mark end) Q3,	sum(case when m.mark_id = 'Q4' then m.mark end) Q4,	sum(case when m.mark_id = 'A1' then m.mark end) A1,	sum(case when m.mark_id = 'A2' then m.mark end) A2,	sum(case when m.mark_id = 'A3' then m.mark end) A3,	sum(case when m.mark_id = 'Final' then m.mark end) Final from students s left outer join marks m on m.username=s.username group by s.username", one=False)
			db.close()
			return render_template("grades.html", instructor_grades = instructor_grades)
	
	return redirect(url_for('login'))

@app.route('/remarkRequest', methods=['GET','POST'])
def remarkRequest():
	if 'username' in session:

		student_session = session.get('student')
		instructor_session = session.get('instructor')
		username = session.get('username')
		assignment = request.form.get('aName')
		reason = request.form.get('reason')
		

			# else:
		db = get_db()
		db.row_factory = make_dicts
			# insert into db

		if request.method=='POST':
			if (assignment == 'Select an evaluation') or (reason == ''):
				# message="Please fill all the fields provided"
				flash("*Please fill all the fields provided")
				return redirect(url_for("remark"))

			query_db("INSERT INTO remark_requests (username, mark_id, comment, status) VALUES (?, ?, ?, 'in progress')", [
				username, assignment, reason])
			db.commit()
			db.close()
			message="Your remark request has been submitted!"
			flash("Your remark request has been submitted!")
			return redirect(url_for("remark", message=message))
	return redirect(url_for('login'))

@app.route('/sendFeedback', methods=['GET','POST'])
def sendFeedback():
	if 'username' in session:

		student_session = session.get('student')
		instructor_session = session.get('instructor')
		instructor = request.form.get('instructorname')
		feedback1 = request.form.get('feedback1')
		feedback2 = request.form.get('feedback2')
		feedback3 = request.form.get('feedback3')
		feedback4 = request.form.get('feedback4')

		db = get_db()
		db.row_factory = make_dicts
			# insert into db

		if request.method=='POST':
			if (instructor == 'Select an instructor') or (feedback1 == '') or (feedback2 == '') or (feedback3 == '') or (feedback4 == '') :
				flash("*Please fill all the fields provided")
				return redirect(url_for('feedback'))

			query_db("INSERT INTO feedback (username, question, comment) VALUES (?, ?, ?)", [
				instructor, 'What do you like about the instructor teaching?', feedback1])
			query_db("INSERT INTO feedback (username, question, comment) VALUES (?, ?, ?)", [
				instructor, 'What do you recommend the instructor to do to improve their teaching?', feedback2])	
			query_db("INSERT INTO feedback (username, question, comment) VALUES (?, ?, ?)", [
				instructor, 'What do you like about the labs?', feedback3])	
			query_db("INSERT INTO feedback (username, question, comment) VALUES (?, ?, ?)", [
				instructor, 'What do you recommend the lab instructors to do to improve their lab teaching?', feedback4])	

			db.commit()
			db.close()
			message="Your anonymous feedback has been submitted successfully!"
			flash("Your anonymous feedback has been submitted successfully!")
			return redirect(url_for("feedback", message=message))
	return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
	if 'username' in session:
		return redirect(url_for('index'))
	elif request.method=='POST':
		username=request.form.get('username')
		password=request.form.get('password')
		usertype=request.form.get('usertype')
		if usertype is not None:
			usertype+="s"
		lecsession=request.form.get('session')
		if len(username)<1:
			error="please enter a username"
			return render_template("register.html", error=error)
		elif len(password)<1:
			error="please enter a password"
			return render_template("register.html", error=error)
		elif usertype not in ("students", "instructors"):
			error="please pick a user type"
			return render_template("register.html", error=error)
		if usertype == "students":
			sql1 = "SELECT * FROM students"
		elif usertype == "instructors":
			sql1 = "SELECT * FROM instructors"
		
		db = get_db()
        # db.row_factory = make_dicts
		results = query_db(sql1, args=(), one=False)
		for result in results:
			if result[0]==username:
				error="username "+username+" is already taken, please pick a different one"
				return render_template("register.html", error=error)
		if usertype == "students":
			sql2="insert into students values(?,?,?)"
			query_db(sql2, [username, password, lecsession])
			session['student'] = True
			session['instructor'] = False
		elif usertype == "instructors":
			sql2="insert into instructors values(?,?,?)"
			query_db(sql2, [username, password, lecsession])
			session['student'] = False
			session['instructor'] = True
		db.commit()
		db.close()
		session['username']=request.form['username']
		return redirect(url_for('index'))
	else:
		return render_template("register.html")

@app.route('/login',methods=['GET','POST'])
def login():
	error=None
	if request.method=='POST':
		db = get_db()
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
					db.close()
					return redirect(url_for('index'))
		error="Incorrect username or password"
		return render_template('login.html', error=error)
	elif 'username' in session:
		return redirect(url_for('index'))
	else:
		return render_template("login.html")

@app.route('/instructorLogin',methods=['GET','POST'])
def instructorLogin():
	error=None
	if request.method=='POST':
		db = get_db()
		sql = """
			SELECT *
			FROM instructors
			"""
		
		# For the student case
		session['student'] = False
		session['instructor'] = True

		results = query_db(sql, args=(), one=False)
		for result in results:
			if result[0]==request.form['username']:
				if result[1]==request.form['password']:
					session['username']=request.form['username']
					db.close()
					return redirect(url_for('index'))
		error="Incorrect username or password"
		return render_template('instructorLogin.html', error=error)
	elif 'username' in session:
		return redirect(url_for('index'))
	else:
		return render_template("instructorLogin.html")

@app.route('/logout')
def logout():
	session.pop('username', None)
	session.pop('student', None)
	session.pop('instructor', None)
	return redirect(url_for('login'))

if __name__=="__main__":
	app.run(debug=True,host='0.0.0.0')
