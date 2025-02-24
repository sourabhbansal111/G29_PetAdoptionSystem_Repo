from flask import Flask , render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager ,login_user, login_required , logout_user ,UserMixin , current_user
from functools import wraps 
from werkzeug.utils import secure_filename
import os


app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db?check_same_thread=False"
app.config['UPLOAD_FOLDER'] = 'static/images/uploads/'
db=SQLAlchemy(app)



app.config["SECRET_KEY"]="welcome"

@app.route("/")
def home():
    return render_template("home.html")

class User(db.Model,UserMixin):
    __tablename__="user"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100))
    email=db.Column(db.String(100))
    password_hash=db.Column(db.String(200))
    profile_pic = db.Column(db.String(255))
    role=db.Column(db.String,default="user")

    def generate_password(self,simple_password):
        #this function is for generating hash password
        self.password_hash=generate_password_hash(simple_password)

    def check_password(self,simple_password):
        #this function is for check hash password
        return check_password_hash(self.password_hash,simple_password)
    

class Contact(db.Model):
    __tablename__ = "Contact"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    number = db.Column(db.String(100) )
    email = db.Column(db.String(100))
    location = db.Column(db.String(200))
    message = db.Column(db.String(5000))
    petname = db.Column(db.String(100))
    petid = db.Column(db.String(100))

class Letter(db.Model):
    __tablename__ = "letterpage"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    number = db.Column(db.String(100))
    location = db.Column(db.String(200))
    message = db.Column(db.String(5000))

    

@app.route("/register",methods=["GET","POST"])
def registerFunction():
    if request.method=="POST":
        username=request.form.get("username")
        email=request.form.get("email")
        password=request.form.get("password")
        role="user"
        if User.query.filter_by(email=email,role="user").first():
            flash("user already exist")
            return redirect(url_for("registerFunction"))
        user_object=User(username=username,email=email,role=role)
        user_object.generate_password(password)
        db.session.add(user_object)
        db.session.commit()
        flash("user registgered successfuly")
        return render_template("login.html")
    return render_template("login.html")



@app.route("/adminregister",methods=["GET","POST"])
def adminregisterFunction():
    if request.method=="POST":
        username=request.form.get("username")
        email1=request.form.get("email")
        password=request.form.get("password")
        role="admin"
        if User.query.filter_by(email=email1,role="admin").first():
            flash("user already exist")
            return redirect(url_for("admin"))
        user_object=User(username=username,email=email1,role=role)
        user_object.generate_password(password)
        db.session.add(user_object)
        db.session.commit()
        flash("admin registgered successfuly")
        return redirect("superadmin")
    return render_template("login.html")



@app.route("/login",methods=["GET","POST"])
def loginFunction():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        role=request.form.get("role")
        user_object=User.query.filter_by(email=email,role=role).first()
        if user_object and user_object.check_password(password): #this will check hash password with original password
            login_user(user_object)# we are storing user in session here 
            flash("User Logged in Successfuly")
            return  redirect(url_for("home"))
        else:
            flash("invalid user")
    return render_template("login.html")



def role_required(role1):
    def decorator(func):
        @wraps(func) 
        def wrapper(*args,**kwargs):
            if current_user.role!=role1:
                flash("unauthorize access")
                return redirect (url_for("loginFunction"))
            return func(*args,**kwargs)
        return wrapper
    return decorator




login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="loginFunction"  

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))



@app.route("/admin")
@login_required
@role_required("admin")
def admin():
    users=User.query.filter_by(role="user").all()
    admins=User.query.filter_by(role="admin").all()
    contacts = Contact.query.all()
    letters = Letter.query.all()
    return render_template("admin.html" ,admins=admins, users=users , contacts=contacts ,letters=letters)




@app.route("/superadmin")
@login_required
@role_required("superadmin")
def superadmin():
    users=User.query.filter_by(role="user").all()
    admins=User.query.filter_by(role="admin").all()
    contacts = Contact.query.all()
    letters = Letter.query.all()
    return render_template("superadmin.html",users=users,admins=admins , contacts=contacts ,letters=letters)




@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")



@app.route("/update/<int:id>",methods=["POST","GET"])
def updatefun(id):
    #we will require user first
    if request.method=="POST":
        current_user.username=request.form.get("username")
        current_user.email=request.form.get("email")

        db.session.commit()

        return redirect(url_for("profile"))
    return redirect(url_for("profile"))    
    

@app.route('/blog')
def blogFunc():
    return render_template('blog.html')

@app.route('/Cockapoo')
def divOneFunc():
    return render_template('div_1.html')

@app.route('/Maltipoo')
def divTwoFunc():
    return render_template('div_2.html')

@app.route('/Shih_Tzu')
def divThreeFunc():
    return render_template('div_3.html')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
@login_required
def contactPage():
    if request.method == "POST":
        
        firstname = request.form.get("first-name")
        lastname = request.form.get("last-name")
        petname = request.form.get("pet-name")
        petid = request.form.get("pet-id")
        email = request.form.get("email")
        number = request.form.get("phone")
        location = request.form.get("location")
        message = request.form.get("message")

        # Prevent duplicate entries

        Contact_object = Contact(firstname=firstname, lastname=lastname, petname=petname,
                            email=email, number=number, location=location, message=message , petid=petid)
        db.session.add(Contact_object)
        db.session.commit()
        flash("Contact form submitted successfully!", "success")

        return redirect(url_for("contactPage"))

    return render_template("contact.html")



@app.route("/letter", methods=["GET", "POST"])
def letterPage():
    if request.method == "POST":
        
        firstname = request.form.get("first-name")
        lastname = request.form.get("last-name")
        number = request.form.get("phone")
        location = request.form.get("location")
        message = request.form.get("message")

        letter_object = Letter(firstname=firstname, lastname=lastname, number=number,
                                location=location, message=message)
        db.session.add(letter_object)
        db.session.commit()
        flash("Newsletter signup successful!", "success")
        return redirect(url_for("contactPage"))

    return render_template("contact.html")


           



with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(role="superadmin").first():
        superadmin=User(username="superadmin",email="superadmin@gmail.com",role="superadmin")
        superadmin.generate_password("superadmin")
        db.session.add(superadmin)
        db.session.commit()
    if not User.query.filter_by(role="admin").first():
        admin=User(username="admin",email="admin@gmail.com",role="admin")
        admin.generate_password("admin")
        db.session.add(admin)
        db.session.commit()



@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        return "No file part", 400
    
    file = request.files['profile_picture']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    current_user.profile_pic=file_path
    db.session.commit()

    return file_path  # Return the file path to update on frontend



#delete
@app.route("/delete/<int:id>" , methods=["GET","POST"])
def deletefun(id):
    #we will require user first
    if request.method=="POST":
        user=db.session.get(User,id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for("superadmin"))
        else:
            return "no user found"
    return render_template("404.html"), 404
    

@app.route("/deletecont/<int:id>" , methods=["GET","POST"])
def deletecont(id):
    #we will require user first
    if request.method=="POST":
        entry=db.session.get(Contact,id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return redirect(url_for("superadmin"))
        else:
            return "no user found"
    return render_template("404.html"), 404



@app.errorhandler(404)
def error_404(e):
    print(e)
    return render_template("errorPages/404.html"),404



@app.errorhandler(500)
def error_500(e):
    print(e)
    return render_template("errorPages/500.html"),500

    

@app.route("/deleteletter/<int:id>" , methods=["GET","POST"])
def deleteletter(id):
    #we will require user first
    if request.method=="POST":
        entry=db.session.get(Letter,id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return redirect(url_for("superadmin"))
        else:
            return "no user found"
    return render_template("404.html"), 404
    


@app.route("/deletecontbyadmin/<int:id>" , methods=["GET","POST"])
def deletecontbyadmin(id):
    #we will require user first
    if request.method=="POST":
        entry=db.session.get(Contact,id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return redirect(url_for("admin"))
        else:
            return "no user found"
    return render_template("404.html"), 404


    

@app.route("/deleteletterbyadmin/<int:id>" , methods=["GET","POST"])
def deleteletterbyadmin(id):
    #we will require user first
    if request.method=="POST":
        entry=db.session.get(Letter,id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return redirect(url_for("admin"))
        else:
            return "no user found"
    return render_template("404.html"), 404
    



@app.route("/logout")
def logout():
    logout_user()
    return render_template("home.html")




if __name__=="__main__":
    app.run(debug=True)






