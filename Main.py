from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

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


@app.route('/', methods=['GET', 'POST'])
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
            return redirect(url_for('home'))
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


#############################################################################

@app.route('/home')
def home():
    return 'home'


@app.route('/show')
def show():
    show_user = User.query.all()
    return render_template('show.html', show_user=show_user)

@app.route('/add')
def add():
    return 'add'


#############################################################################

@app.route('/history')
def history():
    return 'History'


#############################################################################


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
