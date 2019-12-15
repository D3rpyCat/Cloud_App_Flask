from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, current_user, logout_user, LoginManager, login_required
from flask_login.mixins import UserMixin
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from bson.json_util import dumps
from bson.code import Code
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'NAM4BwQqes3vc84tThTk'

# LoginManager pour la gestion des connexions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Différentes connexions MongoDB utilisées
mongo_admin_cloud_app = PyMongo(
    app, uri="mongodb://admin:admin@devincimdb1027.westeurope.cloudapp.azure.com:30000/cloud_app")
mongo_admin_admin = PyMongo(
    app, uri="mongodb://admin:admin@devincimdb1027.westeurope.cloudapp.azure.com:30000/admin")

mongo_analyst_cloud_app = PyMongo(
    app, uri="mongodb://analyst:analyst@devincimdb1027.westeurope.cloudapp.azure.com:30000/cloud_app")

mongo_user_cloud_app = PyMongo(
    app, uri="mongodb://user:user@devincimdb1027.westeurope.cloudapp.azure.com:30000/cloud_app")

# On ne définit que la collection users comme étant un accès en tant qu'admin
# Les 2 autres collections dépendent de l'utilisateur qui se connecte
# Ex : si c'est user (standard), on prendra mongo_user_cloud_app, car il n'a que le rôle readWrite
users = mongo_admin_cloud_app.db.users
employees = None
departments = None

# Classe User utilisée par flask-login pour le système d'authentification
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

# Vérifie l'intégrité des formulaires de login
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
            # Si l'utilisateur à créer n'existe pas dans la collection users
            if existing_user is None:
                # On hash son mot de passe en sha256
                hashpass = generate_password_hash(
                    form.password.data, method='sha256')
                # On l'ajoute à la collection
                users.insert_one(
                    {"pseudo": form.pseudo.data, "password": hashpass})
                # On le log in directement et on le redirige sur l'accueil /home/
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
            # Si l'utilisateur qui souhaite se logger est bien présent dans la collection users
            if check_user:
                #On compare le sha256 du mot de passe entré dans le formulaire avec celui présent dans la collection
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
    # Comme la page d'accueil est la première vue auquel on accède, 
    # on se permet de modifier dans cette fonction les variables globales departments et employees
    # en fonction du pseudo de l'utilisateur courant
    # (Il aurait été mieux de le faire avec des rôles définis pour chaque utilisateur, plus sécurisé)
    
    global departments
    global employees
    if current_user.pseudo == 'user':
        departments = mongo_user_cloud_app.db.departments
        employees = mongo_user_cloud_app.db.employees

        # Liste des dept_no et des titres à afficher dans les select de home.html (ils seront affichés par le moteur de template Jinja2)
        dept_no_list = departments.find({}, {"dept_no": 1})
        title_list = employees.find().distinct("all_titles.title")
        return render_template('home.html', name=current_user.pseudo, dept_no_list=list(dept_no_list), title_list=list(title_list))
    if current_user.pseudo == 'admin':
        departments = mongo_admin_cloud_app.db.departments
        employees = mongo_admin_cloud_app.db.employees_names
        return render_template('home.html', name=current_user.pseudo)
    if current_user.pseudo == 'analyst':
        departments = mongo_analyst_cloud_app.db.departments
        employees = mongo_analyst_cloud_app.db.employees
        return render_template('home.html', name=current_user.pseudo)


# ROUTES POUR LE TABLEAU DE BORD D'UN UTILISATEUR STANDARD

@app.route('/all_managers/')
def all_managers():
    # Tous les managers d'un département

    # On récupère le paramètre de la requête GET
    if request.method == 'GET' and request.args.get('dept_no') != None:
        dept_no = request.args.get('dept_no')
    else:
        # Sinon par défaut on prend le premier dept_no existant dans la collection departments
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

    # On renvoit le json avec les données de retour, un status code 200 et un ContentType à la requête Ajax   
    return dumps({'success': True, "employees_names": list(employees_names)}), 200, {'ContentType': 'application/json'}


@app.route('/all_employees/')
def all_employees():
    # Tous les collaborateurs d'un département avec un certain titre

    title_list = employees.find().distinct("all_titles.title")
    # On récupère les paramètres de la requête GET
    if request.method == 'GET' and request.args.get('dept_no2') != None and request.args.get('title') != None:
        dept_no2 = request.args.get('dept_no2')
        title = request.args.get('title')
    else:
        # Sinon par défaut on prend le premier dept_no existant dans la collection departments
        # Idem pour le titre
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

    # On renvoit le json avec les données de retour, un status code 200 et un ContentType à la requête Ajax   
    return dumps({'success': True, "dept_employees_names": list(dept_employees_names)}), 200, {'ContentType': 'application/json'}


@app.route('/all_salaries/')
def all_salaries():
    # Tous les salaires d'un employé (selon son emp_no)

    emp_emp_no = 0
    # On récupère le paramètre de la requête GET
    if request.method == 'GET' and request.args.get('emp_emp_no') != None:
        emp_emp_no = request.args.get('emp_emp_no')

    salaries_list = employees.aggregate(
        [{	"$match": {"emp_no": int(emp_emp_no)}},
            {	"$unwind": {"path": "$all_salaries"}},
            {"$project": {"all_salaries": 1.0}}])

    # On renvoit labels et values qui vont servir pour le graphique Chart.js (cf. home.js)       
    labels = []
    values = []
    for s in salaries_list:
        from_date = str(s['all_salaries']['from_date'])[:4]
        to_date = str(s['all_salaries']['to_date'])[:4]
        if to_date == "9999":
            to_date = "Aujourd'hui"
        labels.append("["+from_date + " - "+to_date+"]")
        values.append(s['all_salaries']['salary'])

    # On renvoit le json avec les données de retour, un status code 200 et un ContentType à la requête Ajax   
    return dumps({'success': True, "labels": labels, "values": values}), 200, {'ContentType': 'application/json'}


@app.route('/dept_titles_date/')
def dept_titles_date():
    # Nombre d'employés ayant rejoint le département choisi par date et par titre, sur une période d'un mois dans une année

    # On récupère les paramètres de la requête GET
    if request.method == 'GET' and request.args.get('dept_no3') != None and request.args.get('from_date_year') != None and request.args.get('from_date_month') != None:
        dept_no3 = request.args.get('dept_no3')
        from_date_year = request.args.get('from_date_year')
        from_date_month = request.args.get('from_date_month')
        if len(from_date_month) == 1:
            from_date_month = "0"+from_date_month
    else:
        dept_no3 = departments.find_one({}, {"dept_no": 1})['dept_no']
        first_from_date = employees.find().distinct("all_dept.from_date")[0]
        from_date_year = first_from_date[:4]
        from_date_month = first_from_date[5:7]

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

    # On renvoit labels, values et datasets qui vont servir pour le graphique Chart.js (cf. home.js)         
    labels = []
    values = {}
    datasets = []
    for x in dept_titles_per_date:
        labels.append(x["_id"])
        values[x["_id"]] = x["titles"]
        for title in x["titles"]:
            if title['title'] not in datasets:
                datasets.append(title['title'])

    # On renvoit le json avec les données de retour, un status code 200 et un ContentType à la requête Ajax    
    return dumps({'success': True, "labels": labels, "values": values, "datasets": datasets}), 200, {'ContentType': 'application/json'}

# ROUTES POUR LE TABLEAU DE BORD D'UN ANALYSTE

@app.route('/moy_salaire/')
def moy_salaire():
    # Moyenne des salaires par genre sur une période spécifiée par l'utilisateur

    # On récupère les paramètres de la requête GET
    if request.method == 'GET' and request.args.get('from_date') != None and request.args.get('to_date') != None:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
    else:
        first_from_date = employees.find().distinct(
            "all_salaries.from_date")[0]
        from_date = first_from_date[0]
        first_to_date = employees.find().distinct("all_salaries.to_date")[0]
        from_date = first_to_date[0]

    map_moy_salary = Code(
        "function() {for (i=0; i < this.all_salaries.length; i++){ var from=new Date(this.all_salaries[i].from_date); var to=new Date(this.all_salaries[i].to_date); if (from >= new Date(\""+str(from_date)+"\") && to <= new Date(\""+str(to_date)+"\")){emit(this.gender, this.all_salaries[i].salary);}}}")
    reduce_moy_salary = Code(
        "function (key, values) {return Array.avg(values);}")

    result = employees.map_reduce(
        map_moy_salary, reduce_moy_salary, out="result").find()

    # On renvoit labels et values qui vont servir pour le graphique Chart.js (cf. home.js)   
    labels = ['M', 'F']
    values = []
    for res in result:
        values.append(res['value'])

    # On renvoit le json avec les données de retour, un status code 200 et un ContentType à la requête Ajax   
    return dumps({'success': True, "labels": labels, "values": values}), 200, {'ContentType': 'application/json'}


@app.route('/avg_salary_title_hire_date/')
def avg_salary_title_hire_date():
    # Moyennes des salaires par titre et par date d'ancienneté pour une période longue d'un mois dans une année

    # On récupère les paramètres de la requête GET
    if request.method == 'GET' and request.args.get('from_date_year') != None and request.args.get('from_date_month') != None:
        from_date_year = request.args.get('from_date_year')
        from_date_month = request.args.get('from_date_month')
        if len(from_date_month) == 1:
            from_date_month = "0"+from_date_month
    else:
        first_from_date = employees.find().distinct("all_dept.from_date")[0]
        from_date_year = first_from_date[:4]
        from_date_month = first_from_date[5:7]

    map_moy_salary = Code(
        "function () { var date = new Date(this.hire_date); if (date.getFullYear() == "+from_date_year+" && date.getMonth() == "+str(int(from_date_month)-1)+"){ emit({ \"title\": this.all_titles[this.all_titles.length - 1].title,\"hire_date\": date}, this.all_salaries[this.all_salaries.length - 1].salary);}}; ")
    reduce_moy_salary = Code(
        "function (key, values) {return Array.avg(values);}")

    result = employees.map_reduce(
        map_moy_salary, reduce_moy_salary, out="result")
    avg_salaries = result.aggregate([{
        "$group": {
            "_id": {"title": "$_id.title",
                    "hire_date": "$_id.hire_date"},
            "moy": {
                "$avg": "$value"
            }
        }
    }])

    # On renvoit labels,values et datasets qui vont servir pour le graphique Chart.js (cf. home.js)   
    labels = []
    values = []
    datasets = []
    for x in avg_salaries:
        label = str(x['_id']['hire_date'])[:10].replace("-", "/")
        if label not in labels:
            labels.append(label)
        if x['_id']['title'] not in datasets:
            datasets.append(x['_id']['title'])
        values.append({
            "title": x['_id']['title'],
            "hire_date": label,
            "moy": x['moy']
        })

    # On renvoit le json avec les données de retour, un status code 200 et un ContentType à la requête Ajax
    return dumps({'success': True, "labels": labels, "values": values, "datasets": datasets}), 200, {'ContentType': 'application/json'}

# ROUTES POUR LE TABLEAU DE BORD D'UN ADMINISTRATEUR

@app.route('/admin_db_stats/')
def db_stats():
    # Statistiques sur la base de données cloud_app et les collections

    explain_find_employees = mongo_admin_cloud_app.db.command("explain", {
        "find": "employees"})

    explain_find_departments = mongo_admin_cloud_app.db.command("explain", {
        "find": "departments"})

    listShards = mongo_admin_admin.db.command("listShards")

    dbStats = mongo_admin_cloud_app.db.command("dbStats")

    collStats_employees =  mongo_admin_cloud_app.db.command("collStats","employees")

    collStats_departments =  mongo_admin_cloud_app.db.command("collStats","departments")

    # On renvoit le json avec les données de retour, un status code 200 et un ContentType à la requête Ajax
    return dumps({'success': True,
                  "explain_find_employees": explain_find_employees,
                  "explain_find_departments": explain_find_departments,
                  "listShards": listShards,
                  "dbStats":dbStats,
                  "collStats_employees":collStats_employees,
                  "collStats_departments":collStats_departments}), 200, {'ContentType': 'application/json'}

@app.route('/admin_sharding_state/')
def sharding_state():
    # Etat du sharding sur cloud_app

    dbStats = mongo_admin_cloud_app.db.command("dbStats")

    # On renvoit labels et values qui vont servir pour le graphique Chart.js (cf. home.js)   
    labels = []
    values = []
    for shard in dbStats['raw']:
        labels.append(shard[:3])
        values.append(dbStats['raw'][shard]['objects'])

    # On renvoit le json avec les données de retour, un status code 200 et un ContentType à la requête Ajax        
    return dumps({'success': True, "labels": labels, "values": values}), 200, {'ContentType': 'application/json'}

if __name__ == "__main__":
    app.run(debug=True)
