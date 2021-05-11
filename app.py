from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
import bcrypt

app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:brb@localhost:5432/stdpred'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        user = request.form['email']
        password = request.form['password']
        found_user = Users.query.filter_by(email=user).first()
        password = bytes(password, 'utf-8')
        if found_user:
            passwd = found_user.password
            passwd = bytes(passwd, 'utf-8')
            check_pass = bcrypt.checkpw(password, passwd)
            if check_pass:
                session["user"] = found_user.name
                return redirect(url_for('dashboard'))
            else:
                flash("Password is incorrect")
                return render_template('login.html')
        else:
            flash("Email address not found")
            return render_template('login.html')
            
    else:
        if "user" in session:
            return redirect(url_for("dashboard"))
        else:
            return render_template('login.html')

@app.route('/dashboard/')
def dashboard():
    if "user" in session:
        user = session["user"]
        return render_template("dashboard.html", user=user)
    else:
        return redirect(url_for("home"))
         

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        user_exists = Users.query.filter_by(email=email).first()
        if not user_exists:
            password = bytes(password, 'utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            hashed_password = hashed_password.decode('utf-8')
            new_user = Users(name, email, hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        else:
            flash("Email address already exists")
            return render_template("register.html")
    else:
        return render_template("register.html")

@app.route('/logout')
def logout():
    if not "user" in session:
        return redirect(url_for("home"))
        
    del session["user"]
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)