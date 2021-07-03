import requests
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

def predict(marks):
    predicted_marks = requests.post('http://localhost:6000/predict', marks).json()
    return predicted_marks

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

@app.route('/dashboard/', methods=['POST', 'GET'])
def dashboard():
    if "user" in session:
        if request.method == "POST":

            name = request.form["name"]
            usn = request.form["usn"]
            sub1 = request.form["sub1"]
            sub2 = request.form["sub2"]
            sub3 = request.form["sub3"]
            sub4 = request.form["sub4"]
            sub5 = request.form["sub5"]
            sub6 = request.form["sub6"]
            sub7 = request.form["sub7"]
            sub8 = request.form["sub8"]
            
            if sub1.isdigit() and sub1.isdigit() and sub1.isdigit() and sub1.isdigit() and sub1.isdigit() and sub1.isdigit() and sub1.isdigit() and sub1.isdigit(): 
                sub1 = int(request.form["sub1"])
                sub2 = int(request.form["sub2"])
                sub3 = int(request.form["sub3"])
                sub4 = int(request.form["sub4"])
                sub5 = int(request.form["sub5"])
                sub6 = int(request.form["sub6"])
                sub7 = int(request.form["sub7"])
                sub8 = int(request.form["sub8"])
        
                if sub1 > 100 or sub2 > 100 or sub3 > 100 or sub4 > 100 or sub5 > 100 or sub6 > 100 or sub7 > 100:

                    flash("Marks cannot be more that 100")
                    return render_template('dashboard.html')
                
                else: 
                    marks = {
                        "Calculus And Linear Algebra": sub1,
                        "Engineering Physics": sub2,
                        "Basic Electrical Engineering": sub3,
                        "Elements of Civil Engineering And Mechanics": sub4,
                        "Engineering Graphics": sub5,
                        "Engineering Physics Laboratory": sub6,
                        "Basic Electrical Engineering Laboratory": sub7,
                        "Technical English 1": sub8
                    }
                    predicted_marks = predict(marks) 
                    print(predicted_marks)    
                    return render_template('predictions.html', predicted_marks=predicted_marks, name=name, usn=usn)
            else:
                flash("Marks must be in digits")
                return render_template('dashboard.html')
                
        else:
            return render_template('dashboard.html')

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