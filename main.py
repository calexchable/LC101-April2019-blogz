from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
import cgi
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True


db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(255))
    blog_post = db.Column(db.String(99999))

    def __init__(self, blog_title, blog_post):
        self.blog_title = blog_title
        self.blog_post = blog_post

@app.route("/", methods=["POST", "GET"])
def index():
    all_posts = Blog.query.all()
    
    return render_template("blog.html", all_posts=all_posts)

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
        error_title = ""
        error_post = ""        

        if blog_title.strip(" ") == "":
            error_title = "Blog Title cannot be left blank."
        if blog_post.strip(" ") == "":
            error_post = "Please add you post."

        new_post = Blog(blog_title, blog_post)

        if error_title == "" and error_post == "":
            db.session.add(new_post)
            db.session.commit()
            link = "/blog?id=" + str(new_post.id)
            return redirect(link)

        else:
            return render_template("new_post.html", blog_title=blog_title, blog_post=blog_post, error_post=error_post, error_title=error_title)

    else:
        return render_template('new_post.html')
        
if __name__ == '__main__':
    app.run()