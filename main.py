from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Bobemma503@"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)


class User(db.Model):
    _id = db.Column("id",db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __str__(self):
        return self.name
        


@app.route("/home")
@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]
        if password == password2:
            # just reversing password for now
            password_hash = password[::-1]

            # check if user exists
            username_exists = User.query.filter_by(name=name).first()
            email_exists = User.query.filter_by(email=email).first()
            if username_exists:
                flash("Username already exists", "info")
                return redirect(url_for("signup_page"))
            if email_exists:
                flash("Email already used", "info")
                return redirect(url_for("signup_page"))

            # Creating users
            user = User(name, email, password_hash)
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully", "info")
            return redirect(url_for("login_page"))
        else:
            flash("Passwords do not match", "info")
            return redirect(url_for("signup_page"))
    else:
        if "user" in session:
            flash("You are still logged in", "info")
            return redirect(url_for("user_page"))
        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        session.permanent = True
        name = request.form["name"]
        password = request.form["password"]
        password_hash = password[::-1]

        # Reading users info
        user_exists = User.query.filter_by(name=name).first()

        if user_exists:
            if user_exists.password == password_hash:
                session["user"] = name
                flash(f"You logged in successfully, {name}", "info")
                return redirect(url_for("user_page"))
            else:
                flash(f"Incorrect password", "info")
                return redirect(url_for("login_page"))
        else:
            flash(f"User does not exist", "info")
            return redirect(url_for("login_page"))
    else:
        if "user" in session:
            flash("You are still logged in", "info")
            return redirect(url_for("user_page"))
        else:
            return render_template("login.html")


@app.route("/view")
def view_page():
    users = User.query.all()
    return render_template("view.html", users=users)


@app.route("/user", methods=["GET", "POST"])
def user_page():
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = session["email"] = request.form["email"]
            flash("Email added successfully!", "info")
            return render_template("user.html", user=user, email=email)
        if "email" in session:
            email = session["email"]
            return render_template("user.html", user=user, email=email)
        return render_template("user.html", user=user)
    else:
        flash("Please Login", "info")
        return redirect(url_for("login_page"))

# DELETE HAS ISSUES; ISSUE FIXED hehe :)
@app.route("/delete/<name>", methods=["GET", "POST"])
def delete_page(name):
    if request.method == "POST":
        user = User.query.filter_by(name=name).first() # added .first() coz it gives an iterable initially
        # delete user
        if user:
            db.session.delete(user)
            db.session.commit()
            flash(f"{name} deleted successfully", "info")
        else:
            flash(f"User \"{name}\" does not exist", "info")
        
        return redirect(url_for("signup_page"))
    return render_template("delete.html")

@app.route("/logout")
def logout_page():
    if "user" in session:
        user = session["user"]
        flash(f"You logged out successfully, {user}", "info")
        session.pop("user", None)
        session.pop("email", None)
    return redirect(url_for("login_page"))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)