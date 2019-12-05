
# ************************************************************************
#                               FLASK 
# Flask handles web server requests for your app 
#  Framework  that automatically executes the routine code 
# ************************************************************************
# -------------- PYTHON SCRIPT -------------- 
# Handles communication between web server & browser
# ------------------------------------------- 
# -------------- HTML-----------------------
# Responsible for structure of page content (SKELETON!)
# - stored in 'templates' folder
# ------------------------------------------- 
# -------------- CSS-----------------------
# Responsible for styling & formatting on HTML (FLESH!)
# - stored in 'static' folder
# ------------------------------------------- 
# -------------- SQLite -----------------------
# Our database system
# ------------------------------------------- 
# -------------- SQLAlchemy ------------------
# Database of info for the web app(BRAIN!)
# - Can create classes that model the DB itself
# - ORM - object relational mapping
# ------------------------------------------- 
# -------------- JINJA2 --------------------
# Templating language
# - Finds '{{}}' and fills in with var name values
# ------------------------------------------- 
# Resource:
# http://jonathansoma.com/tutorials/flask-sqlalchemy-mapbox/putting-data-on-the-page.html#hello-jinja2
# https://www.codementor.io/garethdwyer/building-a-crud-application-with-flask-and-sqlalchemy-dm3wv7yu2


# # Python library that allows us to access paths on our file system in proj dir
import os
import Tkinter
import tkMessageBox
import getpass
import re


# Import flask library (make framework avail in our program to use its features) 
from flask import Flask, render_template, abort, request, redirect, flash, url_for, g, session
#  Import Flask SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required


# Create instance of Flask class
# '__name__' is a variable that gets string '__main__' when executing script
app = Flask(__name__)
bcrypt = Bcrypt(app)
# Needed in order to access the session dictionary (encryption required - session obj)
app.secret_key="abc"
# ***************************** ADDING OUR DATA MODEL *****************************
# Tell our web app where to find our DB and initialize SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///dogs.sqlite3'
mainUser=None
userName=None
loggedin=False
#Initialize connection to DB and keep this in db var (will be used to interact with our db)
db = SQLAlchemy(app) 

# Dear SQLAch, please teach yourself the DB lol - dont need to specify type of each row - for every model just look at columns that already exist in table
db.Model.metadata.reflect(db.engine)

# Make a regular expression 
# for validating an Email 
#"\. - a period"
#[^a] - one character that is not @
regex = '[^@]+@[^@]+\.[^@]+'

# Define a function for 
# for validating an Email 
def check(email):  
    # pass the regualar expression 
    # and the string in search() method 
    if(re.search(regex,email)):  
        return True   
    else:  
        return False

# Ready to use LoginManager - will handle sessions
# Initialize the app instance
login_manager = LoginManager(app)
login_manager.init_app(app)
#login_manager.login_view = "users.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get('rowid')


# MAKE THE MODEL - specify four things..
# 1) Name
# 2) Table Name - where to find data & learn columns from 
# 3) Says "we're going to change something about the table"
# 4) SQLAch needs unqiue col to be able to keep each row seperate - LOC_CODE column is also the 'primary key'
class Dog(db.Model):
	"""
	Create the Dog class
    """
	__tablename__ = 'dogs'
	__table_args__ = { 'extend_existing': True}
	rowid = db.Column(db.Integer, primary_key=True)
	NAME = db.Column(db.String(32), index=True)
	CHARACTER = db.Column(db.String(32), index=True)
	ABOUT = db.Column(db.String(32), index=True)
	BREED = db.Column(db.String(32), index=True)
	PICTURELINK = db.Column(db.String(32), index=True)
	# Add foreign key column - column that refers to primary key of User table
	OWNER_ID = db.Column(db.Integer, db.ForeignKey('users.rowid'), nullable=False, index=True)


class User(db.Model, UserMixin):
	"""
	Create the Dog class
    """
	__tablename__ = 'users'
	__table_args__ = { 'extend_existing': True}
	rowid = db.Column(db.Integer, primary_key=True, unique=True)
	NAME = db.Column(db.String(32), index=True)
	EMAIL = db.Column(db.String(32), index=True)
	PASSWORD = db.Column(db.String(128))
	


# ***************************** ROUTE METHODS *****************************
@app.route('/') 
def home_main():
	""" Direct to main home page 
	Args:
	None

	Returns:
	pixarpup home login/registration template 

	"""
	loggedin= session['loggedin']
	print("Login: ", current_user.is_authenticated)
	# Pass HTML file to the method - reads HTML template and returns to webpage
	return render_template('pixarpups.html',loggedin=loggedin)


@app.route('/logout')
def logout():
	""" 
	Logout User back to home page

	Args:
	None

	Returns:
	Back to Main PixarPups page

	"""
	logout_user()
	session['loggedin'] = False
	print("Login: ", current_user.is_authenticated)
	return render_template('pixarpups.html')


@app.route('/signup', methods=["GET", "POST"])
def register():
	""" 
	Registers new user to database

	Args:
	None

	Returns:
	Form page for uploading new char 

	"""
	error = ""
	error_email = ""
	error_password= ""
	success=""
	password_valid = False
	email_valid = False
	loggedin=session['loggedin']
	if request.form:
		# Email verification
		email = request.form.get("email")
		email_valid = check(email)
		if not email_valid:
			error_email="Not valid email format"
		# Password verification
		password = request.form.get("password")
		hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
		if re.search(r'\d', password) and re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and len(password)>=8:
			password_valid = True
		else :
			error_password="Password must contain each of the criteria: a number, uppercase letter, lowercase letter at least 8 characters"
		# Verify Registration
		user=User(NAME=request.form.get("name"),
					EMAIL= request.form.get("email"),
					PASSWORD = hashed_password)
		if email_valid and password_valid:
			db.session.add(user)
			db.session.commit()
			success="Registration Successful!"
		else:
			error= error_email + " -- " + error_password
	return render_template("register.html", error=error, success=success, loggedin=loggedin)


@app.route('/login', methods=["GET", "POST"])
def login():
	""" Direct to login page for credentials
	Args:
	None

	Returns:
	Error or home page on success
	 """
	loggedin = session['loggedin']
	if loggedin is False:
		error=""
		if request.form:
			password = request.form.get("password")
			email = request.form.get("email")
			# Check DB to see if correct credentials
			user = User.query.filter_by(EMAIL=email).first()
			# If user exists in DB and password correct
			if user and bcrypt.check_password_hash(user.PASSWORD, password):
				login_user(user)

				session['mainUser']=user.rowid
				session['userName']=user.NAME
				session['loggedin'] = True
				print("Login: ", current_user.is_authenticated)
				return redirect(url_for('home'))
			else:
				error="Credentials Incorrect"
				return render_template("login.html", error=error)
		return render_template("login.html", error=error, loggedin=loggedin)
	else:
		return redirect(url_for('home'))


@app.route('/home')
def home():
	""" Direct to  dog page after login
	Args:
	None

	Returns:
	Form page for uploading new char template

	 """
	loggedin = session['loggedin']
	if loggedin is True:
	# Get all rows in the table
		dogs = Dog.query.all()
		count = Dog.query.count()
		user_id = session.get('mainUser', None)
		user_name = session.get('userName', None)
		# Pass HTML file to the method - reads HTML template and returns to webpage
		return render_template('home.html', dogs=dogs, count=count, user_id=user_id, user_name=user_name, loggedin=loggedin)
	else:
		return render_template('pixarpups.html')


@app.route('/about/')
def about():
	""" Direct to 'about' page 
	Args:
	None

	Returns:
	About page template 
	"""
	loggedin = session['loggedin']
	return render_template('about.html', loggedin=loggedin)


@app.route('/dogs/<slug>')
def detail(slug):
	""" 
	Return detail page for item 'slug'
	
	Args:
	slug (int): name of item

	"""
	loggedin = session['loggedin']
	if loggedin is True:
		# 'first' gives us the row and we can now access values from the data
		# Raise 404 errors instead of returning NONE - return error for missing entries
		dog=Dog.query.filter_by(rowid=slug).first_or_404(description='There is no data with {}'.format(slug))
		# Render the detail template
		return render_template("detail.html", dog=dog, loggedin=loggedin)
	else:
		return render_template('pixarpups.html')

	
@app.route('/upload', methods=["GET", "POST"])
def upload():
	""" 
	Uploads new entry to webpage and database

	Args:
	None

	Returns:
	Form page for uploading new char 

	"""
	loggedin = session['loggedin']
	if loggedin is True:
		user_id = session.get('mainUser', None)
		message=""
		# Accept POST requests and receive input from our form
		if request.form:
			# Create Dog obj and store it in our database
			dog = Dog(NAME=request.form.get("dog_name"), 
							CHARACTER=request.form.get("dog_character"),
							ABOUT=request.form.get("dog_about"),
							BREED=request.form.get("dog_icon"),
							PICTURELINK=request.form.get("dog_photo"),
							OWNER_ID=user_id)

			# Add dog to our DB and commit our changes

			message="Entry Uploaded!"
			#request.form.get("GFG").reset() 
			db.session.add(dog)
			db.session.commit()
			return redirect(url_for('home'))
		return render_template('upload_form.html', message=message, loggedin=loggedin)
	else:
		return render_template('pixarpups.html')


@app.route('/update/<slug>', methods=["GET","POST"])
def update(slug):
	""" 
	Updates entry on webpage and database
	
	Args:
	slug (int): name of item

	Returns:
	Form page to update item 'slug'

	"""
	loggedin = session['loggedin']
	if loggedin is True:
		dog_ref = Dog.query.filter_by(rowid=slug).first_or_404(description='There is no data with {}'.format(slug))
		user_id = session.get('mainUser', None)
		if request.form:
			# Get old/new name
			dog_name_old = request.form.get("dog_name_old")
			dog_name_new = request.form.get("dog_name_new")
			# Get old/new character
			dog_character_old = request.form.get("dog_character_old")
			dog_character_new = request.form.get("dog_character_new")
			# Get old/new about
			dog_about_old = request.form.get("dog_about_old")
			dog_about_new = request.form.get("dog_about_new")
			# Get old/new icon
			dog_icon_old = request.form.get("dog_icon_old")
			dog_icon_new = request.form.get("dog_icon_new")
			# Get old/new photo
			dog_photo_old = request.form.get("dog_photo_old")
			dog_photo_new = request.form.get("dog_photo_new")
			# Fetches dog with old data from db
			dog = Dog.query.filter_by(NAME=dog_name_old,
										CHARACTER = dog_character_old,
										ABOUT = dog_about_old,
										BREED = dog_icon_old,
										PICTURELINK = dog_photo_old).first()
										
			dog.NAME = dog_name_new
			dog.CHARACTER = dog_character_new
			dog.ABOUT = dog_about_new
			dog.BREED = dog_icon_new
			dog.PICTURELINK = dog_photo_new

			# Saves the dog to database
			db.session.commit()
			return redirect("/dogs/{}".format(slug))
		return render_template("update_form.html", dog=dog_ref, slug=slug, loggedin=loggedin)
	else:
		return render_template('pixarpups.html')


@app.route('/dogs/delete', methods=["POST"])
def delete():
	""" 
	Deletes selected item on webpage and database 
	
	Args:
	slug (int): name of item

	Returns:
	Updated homage page
	"""
	loggedin = session['loggedin']
	if loggedin is True:
		dog_id = request.form.get("dog_id")
		dog = Dog.query.filter_by(rowid = dog_id).first()
		db.session.delete(dog)
		db.session.commit()
		# Pop Up Confirmation - ADD
		return redirect("/home")
	else:
		return render_template('pixarpups.html')


# Python assigns '__main__' to script when executed
if __name__ == '__main__':
	# Run the app and print out Python errors on page if any
    app.run(debug=True)




