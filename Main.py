from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'the random string'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    score = db.Column(db.Integer, default=200)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(50))
    description = db.Column(db.String(200))
    pay = db.Column(db.Integer)
    askedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))



################################  REGISTER  LOGIN  LOGOUT ROUTES ###################################


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        data = User.query.filter_by(email=email,
                                    password=password).first()

        if data is not None:
            session['user'] = data.id
            print session['user']
            return redirect(url_for('index'))
        return render_template('incorrectLogin.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(email=request.form['email'],
                        password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


####################################  ROUTES TO DISPLAY #########################################

@app.route('/show')
def show():
    show_user = User.query.all()
    return render_template('show.html', show_user=show_user)


@app.route('/showQuestion')
def showQuestion():
    showQuestion = Question.query.order_by(desc(Question.id))
    return render_template('showQuestion.html', showQuestion=showQuestion)



####################################  OTHER ROUTES  #########################################


@app.route('/index')
def index():
    showQuestion = Question.query.all()
    return render_template('index.html', showQuestion=showQuestion)


@app.route('/', methods=['GET', 'POST'])
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        user_id = session['user']
        print(user_id)
        new_question = Question(question = request.form['question'],
                        description=request.form['description'],
                            pay=request.form['pay'],askedby_id= user_id )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('showQuestion'))
    else:

        return render_template('AddQuestion.html')



@app.route('/ParticularQuestion')
def ParticularQuestion():
    id=request.args
    print(id)
    q = Question.query.get(id)
    user=q.askedby_id
    email=User.query.get(user).email
    return render_template('ParticularQuestion.html',question=q,email=email)

@app.route('/history')
def history():
    return 'History'


######################################### MAIN ####################################


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
