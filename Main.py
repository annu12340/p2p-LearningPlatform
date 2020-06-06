from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'the random string'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    score = db.Column(db.Integer, default=200)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(50))
    description = db.Column(db.String(200))
    pay = db.Column(db.Integer)
    askedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    description = db.Column(db.String(200))
    pay = db.Column(db.Integer)
    questionID = db.Column(db.Integer, db.ForeignKey('question.id'))


################################  REGISTER  LOGIN  LOGOUT ROUTES ###################################


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = hash(request.form['password'])
        data = User.query.filter_by(username=username,
                                    password=password).first()

        if data is not None:
            session['user'] = data.id
            print session['user']
            return redirect(url_for('index'))

        return render_template('incorrectLogin.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'],
                        password=hash(request.form['password']))

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
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


@app.route('/showResponse')
def showResponse():
    showResponse = Response.query.all()
    return render_template('showResponse.html', showResponse=showResponse)


####################################  OTHER ROUTES  #########################################

@app.route('/', methods=['GET', 'POST'])
@app.route('/landingPage')
def landingPage():
    return render_template('landingPage.html')


@app.route('/index')
def index():
    username = User.query.get(session['user']).username
    print(username)
    flash("welcome {}".format(username))
    showQuestion = Question.query.order_by(desc(Question.id))
    return render_template('index.html', showQuestion=showQuestion)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        user_id = session['user']
        print(user_id)
        new_question = Question(question=request.form['question'],
                                description=request.form['description'],
                                pay=request.form['pay'], askedby_id=user_id)
        flash("New question has been succesfully added")
        db.session.add(new_question)

        db.session.commit()

        return redirect(url_for('index'))
    else:

        return render_template('AddQuestion.html')


@app.route('/ParticularQuestion', methods=['GET', 'POST'])
def ParticularQuestion():
    if request.method == 'POST':
        id = request.args
        print((id))
        new_response = Response(username=request.form['username'],
                                description=request.form['description'],
                                pay=request.form['pay'], questionID=request.form['id'])
        db.session.add(new_response)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        id = request.args
        print(id)
        q = Question.query.get(id)
        user = q.askedby_id
        username = User.query.get(user).username

        response = Response.query.filter_by(questionID=q.id).all()
        print("response is", response)
        return render_template('ParticularQuestion.html', question=q, username=username, response=response)


@app.route('/myQuestion')
def myQuestion():
    user_id = session['user']
    myQuestion = Question.query.filter_by(askedby_id=user_id).all()
    print(myQuestion)
    return render_template('myQuestion.html', myQuestion=myQuestion)


@app.route('/DoubtSolved')
def DoubtSolved():
    id = request.args
    print(id)
    q = Question.query.get(id)
    return render_template('DoubtSolved.html', q=q)


@app.route('/Delete')
def Delete():
    id = int(request.args['id'])
    print('to be deleted ', id)
    obj = Question.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()
    return render_template('index.html')



@app.route('/payment')
def payment():
    details = request.args
    print(details)
    mentor = str(details['doubt'])
    print('m is', mentor)
    amt = details['amount']
    user_id = session['user']
    u = User.query.get(user_id)
    mentor = User.query.filter_by(username=mentor).first()
    topay = User.query.get(mentor.id)
    print('mentor is  ', topay)
    if u.score > 0:
        flash("Payment successully made")
        print(u.score)
        u.score = u.score - int(amt)
        topay.score += int(amt)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('4o4.html', display_content="Transcation unsuccessul due to lack of credits")


@app.route('/scoreBoard')
def scoreBoard():
    rank_user = User.query.order_by(desc(User.score))
    return render_template('scoreBoard.html', rank_user=rank_user)


######################################### MAIN ####################################


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
