from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
import cgi
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:password@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True


db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(255))
    blog_post = db.Column(db.String(99999))
    owner_id = db.Column(db.Integer, db.ForeignKey("User.id"))

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

    def __repr__(self):
        return str(self.username)

@app.route("/")
def index():
    return redirect("/blog")

@app.route("/login", methods=["POST", "GET"])
def login():
    username = ""
    username_error = ""
    password_error = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        returning_user = User.query.filter_by(username=username).first()

        if username != returning_user:
            username_error = "Invalid Username."

        else:
            if password == "":
                password_error = "Please enter your password."
            elif re_user.password != password:
                password_error = "Invalid Password"
    
    return render_template("login.html", title="Login", username=username, username_error=username_error, password_error=password_error)



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