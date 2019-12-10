from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, current_user, logout_user, LoginManager, login_required
from flask_login.mixins import UserMixin
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'NAM4BwQqes3vc84tThTk'

login_manager = LoginManager()
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
    user_db = users.find_one({'pseudo': user_id})
    return User(user_db['pseudo'], user_db['password'])


class RegForm(FlaskForm):
    pseudo = StringField('pseudo',  validators=[InputRequired(), Length(
        max=30, message="Veuillez entrer un pseudo de moins de %(max)d caractères.")])
    password = PasswordField('password', validators=[InputRequired(), Length(
        min=4, max=20, message="Veuillez entrer un pseudo de %(min)d à %(max)d caractères.")])


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            existing_user = users.find_one({"pseudo": form.pseudo.data})
            if existing_user is None:
                hashpass = generate_password_hash(
                    form.password.data, method='sha256')
                users.insert_one(
                    {"pseudo": form.pseudo.data, "password": hashpass})
                login_user(User(form.pseudo.data, hashpass))
                return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('home'))
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            check_user = users.find_one({"pseudo": form.pseudo.data})
            if check_user:
                if check_password_hash(check_user['password'], form.password.data):
                    login_user(User(form.pseudo.data, form.password.data))
                    return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/logout/', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def default():
    return redirect(url_for('home'))


@app.route('/home/')
@login_required
def home():
    if current_user.pseudo == 'user':
        # all_managers
        dept_no_list = departments.find({}, {"dept_no": 1})
        if request.method == 'GET' and request.args.get('dept_no') != None:
            dept_no = request.args.get('dept_no')
        else:
            dept_no = departments.find_one({}, {"dept_no": 1})['dept_no']
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

        # all_salaries
        emp_emp_no = 0
        if request.method == 'GET' and request.args.get('emp_emp_no') != None:
            emp_emp_no = request.args.get('emp_emp_no')
        salaries_list = employees.aggregate(
        [{	"$match": {"emp_no":int(emp_emp_no)}},
         {	"$unwind": {"path": "$all_salaries"}},
            {"$project": {"all_salaries": 1.0}}])
        labels = []
        values = []
        for s in salaries_list:
            labels.append("["+str(s['all_salaries']['from_date'])+" - "+str(s['all_salaries']['to_date'])+"]")
            values.append(s['all_salaries']['salary'])
        if values!=[]:
            max_value = max(values)+100
        else:
            max_value = 100000
        return render_template('home.html', name=current_user.pseudo, dept_no_list=dept_no_list, employees_names=employees_names, dept_no_chosen=dept_no, emp_emp_no=emp_emp_no,bar_labels=labels,bar_values=values,max=max_value)
    if current_user.pseudo == 'admin':
        return render_template('home.html', name=current_user.pseudo)
    if current_user.pseudo == 'analyst':
        return render_template('home.html', name=current_user.pseudo)


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
