from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, current_user, logout_user, LoginManager, login_required
from flask_login.mixins import UserMixin
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from bson.json_util import dumps


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
            [{	"$match": {"emp_no": int(emp_emp_no)}},
             {	"$unwind": {"path": "$all_salaries"}},
                {"$project": {"all_salaries": 1.0}}])
        labels = []
        values = []
        for s in salaries_list:
            labels.append("["+str(s['all_salaries']['from_date']) +
                          " - "+str(s['all_salaries']['to_date'])+"]")
            values.append(s['all_salaries']['salary'])
        if values != []:
            max_value = max(values)+100
        else:
            max_value = 100000

        # all_employees
        title_list = employees.find().distinct("all_titles.title")

        if request.method == 'GET' and request.args.get('dept_no2') != None and request.args.get('title') != None:
            dept_no2 = request.args.get('dept_no2')
            title = request.args.get('title')
        else:
            dept_no2 = departments.find_one({}, {"dept_no": 1})['dept_no']
            title = title_list[0]

        dept_employees_names = []
        dept_employees = employees.aggregate(
            [{"$match": {"all_dept.dept_no": str(dept_no2)}},
             {"$unwind": {"path": "$all_titles"}},
                {"$match": {"all_titles.title": str(title)}},
                {"$project": {"first_name": 1.0, "last_name": 1.0}}])
        for emp in dept_employees:
            dept_employees_names.append(emp)

        # dept_titles_date
        if request.method == 'GET' and request.args.get('dept_no3') != None and request.args.get('from_date_year') != None and request.args.get('from_date_month') != None:
            dept_no3 = request.args.get('dept_no3')
            from_date_year = request.args.get('from_date_year')
            from_date_month = request.args.get('from_date_month')
            if len(from_date_month)==1:
                from_date_month = "0"+from_date_month
        else:
            dept_no3 = departments.find_one({}, {"dept_no": 1})['dept_no']
            list_dates = employees.find().distinct("all_dept.from_date")[0]
            from_date_year = list_dates[:4]
            from_date_month = list_dates[5:7]

        dept_titles_per_date = employees.aggregate(
            [{	"$unwind": {"path": "$all_titles"}},
             {	"$unwind": {"path": "$all_dept"}},
                {	"$match": {"all_dept.dept_no": str(dept_no3), "all_dept.from_date": {
                    "$regex": str(from_date_year)+"/"+str(from_date_month)}}},
             {"$group": {"_id": {"from_date": "$all_dept.from_date",
                                 "title": "$all_titles.title"}, "titleCount": {"$sum": 1}}},
                {"$group": {
                    "_id": "$_id.from_date",
                    "titles": {"$push": {
                        "title": "$_id.title", "count": "$titleCount"}},
                    "count": {"$sum": "$titleCount"}}},
                {"$sort": {"_id": 1}},
                {"$project": {"titles": 1}}
             ])
        stacked_bar_labels = []
        stacked_bar_values = {}
        dept_titles_datasets = []
        for x in dept_titles_per_date:
            stacked_bar_labels.append(x["_id"])
            stacked_bar_values[x["_id"]] = x["titles"]
            for title in x["titles"]:
                if title['title'] not in dept_titles_datasets:
                    dept_titles_datasets.append(title['title'])
        

        return render_template('home.html', name=current_user.pseudo, dept_no_list=list(dept_no_list), employees_names=employees_names, dept_no_chosen=dept_no, emp_emp_no=emp_emp_no, bar_labels=labels, bar_values=values, max=max_value, dept_no_chosen2=dept_no2, title_chosen=title, title_list=list(title_list), dept_employees_names=dept_employees_names, dept_no_chosen3=dept_no3, from_date_year=from_date_year,from_date_month=from_date_month,stacked_bar_labels=stacked_bar_labels, dept_titles_datasets=dept_titles_datasets,stacked_bar_values=stacked_bar_values)
    if current_user.pseudo == 'admin':
        return render_template('home.html', name=current_user.pseudo)
    if current_user.pseudo == 'analyst':
        return render_template('home.html', name=current_user.pseudo)

@app.route('/admin/')
def admin():
    return "Admin view"


@app.route('/analyst/')
def analyst():
    return "Analyst view"

@app.route('/test/')
def test():
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
    return dumps({'success':True,"employees_names":list(employees_names)}), 200, {'ContentType':'application/json'} 

if __name__ == "__main__":
    app.run(debug=True)
