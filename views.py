from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, current_user,logout_user, LoginManager, login_required
from flask_login.mixins import UserMixin
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'NAM4BwQqes3vc84tThTk'

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mongo_admin = PyMongo(
    app, uri="mongodb://admin:admin@devincimdb1027.westeurope.cloudapp.azure.com:30000/cloud_app")
mongo_analyst = PyMongo(
    app, uri="mongodb://analyst:analyst@devincimdb1027.westeurope.cloudapp.azure.com:30000/cloud_app")
mongo_user = PyMongo(
    app, uri="mongodb://user:user@devincimdb1027.westeurope.cloudapp.azure.com:30000/cloud_app")

departments = mongo_admin.db.departments
employees = mongo_admin.db.employees
users = mongo_admin.db.users

class User():
    def __init__(self, pseudo, password):
        self.pseudo = pseudo
        self.password = password

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.pseudo

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

@login_manager.user_loader
def load_user(user_id):
    user_db = users.find_one({'pseudo':user_id})
    return User(user_db['pseudo'],user_db['password'])

class RegForm(FlaskForm):
    pseudo = StringField('pseudo',  validators=[InputRequired(), Length(max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=20)])

@app.route('/')
def default():
    return redirect(url_for('home'))

@app.route('/home/')
@login_required
def home():
    return render_template('home.html', name=current_user.pseudo)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            existing_user = users.find_one({"pseudo":form.pseudo.data})
            if existing_user is None:
                hashpass = generate_password_hash(form.password.data, method='sha256')
                users.insert_one({"pseudo":form.pseudo.data,"password":hashpass})
                login_user(User(form.pseudo.data,hashpass))
                return redirect(url_for('home'))
        else:
            Flask.flash("Pseudo ou mot de passe invalide")
    return render_template('register.html', form=form)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('home'))
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            check_user = users.find_one({"pseudo":form.pseudo.data})
            if check_user:
                if check_password_hash(check_user['password'], form.password.data):
                    login_user(User(form.pseudo.data,form.password.data))
                    return redirect(url_for('home'))
        else:
            Flask.flash("Pseudo ou mot de passe invalide")
    return render_template('login.html', form=form)

@app.route('/logout/', methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user/')
def user():
    dept_no_list = departments.find({}, {"dept_no": 1})
    return render_template("user.html", dept_no_list=dept_no_list)


@app.route('/user/result/all_managers/')
def user_result_all_managers():
    dept_no = request.args.get('dept_no')
    if dept_no != None:
        departments_list = departments.aggregate(
            [{	"$match": {"dept_no": str(dept_no)}},
             {
                "$unwind": {
                    "path": "$all_managers"
                }}
             ])
        employees_names = []
        for department in departments_list:
            results = employees.aggregate(
                [{
                    "$match": {
                        "emp_no": department['all_managers']['emp_no']
                    }
                },
                    {
                        "$project": {
                            "last_name": 1,
                            "first_name": 1
                        }
                }
                ])
            for result in results:
                employees_names.append(result)
        return render_template("user_result_all_managers.html", employees_names=employees_names)


@app.route('/user/result/salary/')
def user_result_salary():
    salaries_list = employees.aggregate(
        [{	"$match": {"first_name": "Sachin", "last_name": "Tsukuda"}},
         {	"$unwind": {"path": "$all_salaries"}},
            {	"$match": {"all_salaries.from_date": "1999/09/03",
                         "all_salaries.to_date": "2006/09/02"}},
            {"$project": {"all_salaries.salary": 1.0}}])
    return render_template("user_result_salary.html", salaries_list=salaries_list)


@app.route('/admin/')
def admin():
    return "Admin view"


@app.route('/analyst/')
def analyst():
    return "Analyst view"


if __name__ == "__main__":
    app.run(debug=True)
