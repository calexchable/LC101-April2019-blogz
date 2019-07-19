from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import pymysql
import cgi
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:password@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
app.secret_key = "y2k+9-11g0vp10y"

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(255))
    blog_post = db.Column(db.String(99999))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, blog_title, blog_post, owner):
        self.blog_title = blog_title
        self.blog_post = blog_post
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    blogs = db.relationship("Blog", backref = "owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return str(self.username)

@app.before_request
def require_login():
    allowed_routes = ["login", "register", "index"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")


@app.route("/", methods=["POST", "GET"])
def index():
    users = User.query.all()
    return render_template("index.html", users=users)

@app.route("/login", methods=["POST", "GET"])
def login():
    username = ""
    username_error = ""
    password_error = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        existing_user = User.query.filter_by(username=username).first()

        if username != existing_user:
            username_error = "Invalid Username."

        else:
            if password == "":
                password_error = "Please enter your password."
            elif existing_user.password != password:
                password_error = "Invalid Password"
    
    return render_template("login.html", title="Login",username=username, username_error=username_error, password_error=password_error)

@app.route("/register", methods=["POST", "GET"])
def register():
    username = ""
    username_error = ""
    password_error = ""
    verify_error = ""

    if request.method == "POST":
        username = request.form["username"]
        username_error = ""

        exisiting_user = User.query.filter_by(username=username).first()

        if username == "":
            username_error = "Please enter a username."
        elif len(username) < 3 or len(username) > 20:
            username = ""
            username_error = "Username must contain between 3 and 20 characters."
        elif " " in username:
            username = ""
            username_error = "Username cannot contain any spaces."
        elif username == exisiting_user:
            username = ""
            username_error = "Username already exisits. Please select another username."

        password = request.form["password"]
        password_error = ""

        if password == "":
            password_error = "Please enter a valid Password."
        elif len(password) < 3 or len(password) > 20:
            password = ""
            password_error = "Password must contain between 3 and 20 characters."
        elif " " in password:
            password = ""
            password_error = "Password must not contain any spaces."
        
        verify = request.form["verify"]
        verify_error = ""

        if verify == "":
            verify_error = "Please validate your password."
        elif verify != password:
            verify = ""
            verify_error = "Passwords do not match. Please re-enter your password."
        
        if username_error == "" and password_error == "" and verify_error == "":
            if not exisiting_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session["user"] = new_user.username
                return redirect("/new_post")

            else:
                username_error = "Username in use, select another."

    return render_template("register.html", username=username, username_error=username_error, password_error=password_error, verify_error=verify_error)

@app.route("/blog")
def blog_list():
    title = "Blogzzz"

    if session:
        owner = User.query.filter_by(username = session["username"]).first()

    if "id" in request.args:
        post_id = request.args.get("id")
        blog = Blog.query.filter_by(id = post_id).all()

        return render_template("blog.html", title=title, blog=blog, post_id = post_id)
    
    elif "user" in request.args:
        user_id = request.args.get("user")
        blog = Blog.query.filter_by(owner_id = user_id).all()

        return render_template("blog.html", title=title, blog=blog)

    else:
        blog = Blog.query.all()

        return render_template("blog.html", title=title, blog=blog)

@app.route("/newpost", methods=["POST", "GET"])
def new_post():

    blog_title = ""
    blog_post = ""
    
    error_title = ""
    error_post = ""  
        
    owner = User.query.filter_by(username = session["username"]).first()

    if request.method == "POST":

        blog_title = request.form["blog_title"]
        blog_post = request.form["blog_post"]

        if blog_title.strip(" ") == "":
            error_title = "Blog Title cannot be left blank."

        if blog_post.strip(" ") == "":
            error_post = "Please add you post."

        if error_title == "" and error_post == "":

            new_post = Blog(blog_title, blog_post, owner)
            db.session.add(new_post)
            db.session.commit()
            blog_id = Blog.query.order_by(Blog.id.desc()).first()
            user = owner

            return redirect("/blog?id={}&user={}".format(blog_id.id, user.username))

        return render_template("new_post.html", blog_title=blog_title, blog_post=blog_post, error_post=error_post, error_title=error_title)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/blog")

if __name__ == '__main__':
    app.run()