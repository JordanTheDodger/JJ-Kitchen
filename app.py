from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
from data import Dishes
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SECRET_KEY'] = "Don't tell anyone"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1033@localhost/learning'
db = SQLAlchemy(app)

Dishes = Dishes()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/dishes')
def dishes():
    return render_template('dishes.html', Dishes=Dishes)


@app.route('/dish/<string:id>')
def dish(id):
    return render_template('dish.html', id=id)


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    # Using WtForms for registration
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create db, execute query
        db.create_all()
        usr = Flask_Users(None, name, email, username, password)
        db.session.add(usr)

        # Commit and close connection
        db.session.commit()

        flash('You are now registered', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route('/login', methods=['GET,''POST'])
def login():
    if request.method == 'POST':
        # get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # getting user
        login_user = Flask_Users.query.all(username=username.first())

        if login_user:
            # Get stored hash
            password = login_user.password
            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                app.logger.info('PASSWORD MATCHED')
            else:
                app.logger.info('PASSWORD MATCHED')

        else:
            app.logger.info('NO USER FOUND')

    return render_template('login.html')


# Calling the database
class Flask_Users(db.Model):
    __tablename__ = "flask_users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, id, name, email, username, password):
        self.id = id
        self.name = name
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return f'Username:- {self.username}\n Email:- {self.email}\n Password:- {self.password}'

if __name__ == '__main__':
    app.run(port=4995, debug=True)
