from flask import Flask, render_template, request, flash, redirect, url_for, session, logging

from data import Dishes
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SubmitField, IntegerField
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'God save you from Forms'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1033@localhost/learning'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_CURSORCLASS'] = 'DictCursor'
db = SQLAlchemy(app)


Dishes = Dishes()


@app.route('/')
@app.route('/home')
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


# Register Form class
class RegisterForm(Form):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.DataRequired(), validators.Length(min=6, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    address = TextAreaField('Address', [validators.DataRequired(), validators.Length(max=1000)])
    contact = IntegerField('Contact')
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
        username = form.username.data
        address = form.address.data
        contact = form.contact.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create db, execute query
        db.create_all()
        usr = Flask_Users(None, name, email, username, address, contact, password)
        db.session.add(usr)

        # Commit and close connection
        db.session.commit()

        flash('You are now registered', 'success')
        return redirect(url_for('home'))

    return render_template("register.html", form=form)


class Flask_Users(db.Model):# Calling  User DB
    __tablename__ = "flask_users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    contact = db.Column(db.Integer, nullable=False,unique=True)
    password = db.Column(db.String, nullable=False)

    def __init__(self,id,name,email,username,address,contact,password):
        self.id = id
        self.name = name
        self.email = email
        self.username = username
        self.address = address
        self.contact = contact
        self.password = password

    def __repr__(self):
        return f'Username:- {self.username}\n Email:- {self.email}\n Password:- {self.password}'
#REGISTRATION PROCESS ENDS DO NOT MOVE ANY CODE FROM ABOVE


# # Login Form class
# class LoginForm(Form):
#     username = StringField('Username', [validators.DataRequired()])
#     password = PasswordField('Password', [validators.DataRequired()])


# User Login
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        # get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # getting user
        login_user = Flask_Users.query.filter_by(username=username).one()

        if login_user is not None:
            # Get stored hash
            password = login_user.password  # is this right way to get one field from login_user??
            # Compare passwords
            password_match = sha256_crypt.verify(password_candidate, password)
            if password_match:
                app.logger.info('PASSWORD MATCHED')

        else:
            app.logger.info('NO user')

    return render_template('login.html')


# class Flask_Dishes(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String,nullable=False)
#     body = db.Column(db.String,nullable=False)
#     price = db.Column(db.Integer,nullable=False)
#
#     def __init__(self, id, title, body, price):
#         self.id = id
#         self.title = title
#         self.body = body
#         self.price = price
#
#     def __repr__(self):
#         return f'Name:- {self.title}\n Price:- {self.price}'
#
#
# class Flask_Orders(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('Flask_Users.id'),nullable=False)
#     dish_id = db.Column(db.Integer, db.ForeignKey('Flask_Dishes.id'), nullable=False)
#     qty = db.Column(db.Integer, nullable=False)
#     qty_price = db.Column(db.Integer)
#     total_price = db.Column(db.Integer, nullable=False)
#
#     def __init__(self, id, user_id, dish_id, qty, total_price):
#         self.id = id
#         self.user_id = user_id
#         self.dish_id = dish_id
#         self.total_price = total_price
#
#     def __repr__(self):
#         return f'Username:- {self.username}\n Email:- {self.email}\n Password:- {self.password}'

if __name__ == '__main__':
    app.run(port=4995, debug=True)
