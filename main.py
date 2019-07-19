from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
import cgi
import os
import User
import Blog


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:password@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True


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

    def __init__(self, username, password, blogs):
        self.username = username
        self.password = password
        self.blogs = blogs

    def __repr__(self):
        return str(self.username)

@app.route("/", methods=["POST", "GET"])
def index():
    users = User.query.all()
    return render_template("index.html", users=users

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
        
        if username == "":
            username_error = "Please enter a username."
        elif len(username) < 3 or len(username) > 20:
            username = ""
            username_error = "Username must contain between 3 and 20 characters."
        elif " " in username:
            username = ""
            username = error = "Username cannot contain any spaces."

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
        
        exisiting_user = User.query.filter_by(username=username).first
        if username == exisiting_user:
            username_error = "Username already exists. Please re-enter a new username."
            username = ""

        if username_error == "" and password_error == "" and verify_error == "":
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session["user"] = new_user.username
            return redirect("/blog")

    return render_template("register.html", username=username, username_error=username_error, password_error=password_error, verify_error=verify_error)

@app.route("/blog")
def single_blog():
    post_id = request.args.get("id")

    if post_id:
        single_post = Blog.query.get(post_id)
        return render_template("single_post.html", single_post=single_post)

    else:
        all_posts = Blog.query.all()

        return render_template("blog.html", all_posts=all_posts)

@app.route("/newpost", methods=["POST", "GET"])
def new_post():
    if request.method == "POST":
        blog_title = request.form["blog_title"]
        blog_post = request.form["blog_post"]
        owner_id = request.form["owner_id"]

        error_title = ""
        error_post = ""        

        if blog_title.strip(" ") == "":
            error_title = "Blog Title cannot be left blank."
        if blog_post.strip(" ") == "":
            error_post = "Please add you post."

        new_post = Blog(blog_title, blog_post, owner_id)

        if error_title == "" and error_post == "":
            db.session.add(new_post)
            db.session.commit()
            link = "/blog?id=" + str(new_post.id)
            return redirect(link)

        else:
            return render_template("new_post.html", blog_title=blog_title, blog_post=blog_post, owner_id=owner_id, error_post=error_post, error_title=error_title)

    else:
        return render_template('new_post.html')
        
if __name__ == '__main__':
    app.run()