import sqlite3

from flask import Flask, render_template, request, redirect, session, g

# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/

DATABASE = './assignment3.db'

a = 5
b = 8

# open and connect to database, return a db (connection)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# run a query
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=()):
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    # commit the changes to the database and close cursor and connection
    db.commit()
    cur.close()
    db.close()

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


app = Flask(__name__)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/test')
def test():
    db = get_db()
    db.row_factory = make_dicts
    users = query_db('SELECT * FROM User WHERE username=?')
    db.close()

    return str(users)


@app.route('/') ## <- by default, 'GET'
def home():
    
    # if the key "username" is NOT YET in the session Dictionary
    # the user has not logged in :)
    if 'username' not in session:
        return redirect('/login')

    return render_template('index.html', username=session['username'], admin=session['admin'])


@app.route('/marks')
def marks():

    if 'username' not in session:
        return redirect('/login')

    db = get_db()
    db.row_factory = make_dicts

    if session['admin']:
        marks = query_db('SELECT * FROM Mark')
    else:
        marks = query_db('SELECT * FROM Mark WHERE username=?', [session['username']])

    db.close()

    return render_template('marks.html', username=session['username'], marks=marks, admin=session['admin'])



@app.route('/remark')
def remark():

    if 'username' not in session:
        return redirect('/login')

    if not request.args:
        return redirect('/marks')

    mark_id = request.args['mark_id']
    reason = request.args['reason']

    try:
        insert_db('INSERT INTO Remark VALUES(?, ?)', (mark_id, reason))
    except:
        return redirect('/marks')

    return redirect('/success')

@app.route('/success')
def success():

    if 'username' not in session:
        return redirect('/login')


    return render_template('success.html')


@app.route('/feedback')
def feedback():

    if 'username' not in session:
        return redirect('/login')
    
    # instructor shouldnt access this link
    if session['admin']:
        return redirect('/')

    # GET
    if not request.args:
    
        db = get_db()
        db.row_factory = make_dicts
        instructors = query_db('SELECT username FROM User WHERE admin = 1')
        db.close()
        return render_template('feedback.html', instructors = instructors)
    
    # POST
    else:

        instructor = request.args['username']
        question1 = request.args['question1']        
        question2 = request.args['question2']
        question3 = request.args['question3']
        question4 = request.args['question4']


        insert_db(
            'INSERT INTO Feedback VALUES (?, ?, ?, ?, ?)', 
            (instructor, question1, question2, question3, question4))

        return redirect('/success')

@app.route('/feedbacks')
def feedbacks():

    if 'username' not in session:
        return redirect('/login')
    
    # student shouldnt access this link
    if not session['admin']:
        return redirect('/')
    
    db = get_db()
    db.row_factory = make_dicts
    feedbacks = query_db('SELECT * FROM Feedback WHERE instructor=?', [session['username']])
    db.close()

    return render_template('feedbacks.html', feedbacks=feedbacks)


@app.route('/remarks')
def remarks():

    if 'username' not in session:
        return redirect('/login')
    
    # student shouldnt access this link
    if not session['admin']:
        return redirect('/')
    
    db = get_db()
    db.row_factory = make_dicts
    remarks = query_db(
        'SELECT * FROM Remark, Mark WHERE Remark.mark_id = Mark.mark_id')
    db.close()

    return render_template('remarks.html', remarks=remarks)


@app.route('/mark')
def mark():

    if 'username' not in session:
        return redirect('/login')
    
    # student shouldnt access this link
    if not session['admin']:
        return redirect('/')
    
    # GET
    if not request.args:
        
        # get a list of student username for a drop down menu
        db = get_db()
        db.row_factory = make_dicts
        students = query_db('SELECT DISTINCT username FROM User WHERE admin = 0')
        db.close()

        return render_template('mark.html', students=students)

    
    # POST
    else:

        name = request.args['name']
        grade = float(request.args['grade'])
        username = request.args['username']


        insert_db(
            'INSERT INTO Mark (name, grade, username) VALUES (?, ?, ?)',
            (name, grade, username))


        return redirect('/mark') # or redirect('/success')




# @app.route('/login', methods=['GET', 'POST'])
@app.route('/login')
def login():

    # if request.method == 'GET':
    #     return render_template('login.html')

    if not request.args:  # len(request.args) == 0:
        return render_template('login.html')

    # username = request.form['username']
    # password = request.form['password']

    username = request.args['username']
    password = request.args['password']


    db = get_db()
    db.row_factory = make_dicts
    user = query_db('SELECT * FROM User WHERE username=? AND password=?',
                    [username, password], one=True)
    db.close()

    # success

    if user:
        session['username'] = user['username']
        session['admin'] = True if user['admin'] == 1 else False
        return redirect('/')
    else:
        return render_template('login.html', error=True)


@app.route('/signup')
def signup():

    if not request.args:
        return render_template('signup.html')


    username = request.args['username']
    password = request.args['password']

    is_admin = 1 if 'admin' in request.args else 0

    db = get_db()
    db.row_factory = make_dicts
    user = query_db('SELECT * FROM User WHERE username=?',
                    [username], one=True)
    db.close()

    
    if user:
        return redirect('/signup')
    else:
        insert_db('INSERT INTO User VALUES(?, ?, ?)', (username, password, is_admin))
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/login')


@app.route('/calendar')
def calendar():
    return render_template('calendar.html')



if __name__ == "__main__":
    app.secret_key = "I fucking hate cscb20 :)"
    app.run(debug=True)

