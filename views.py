from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo_admin = PyMongo(
    app, uri="mongodb://admin:admin@devincimdb1027.westeurope.cloudapp.azure.com:30000/cloud_app")
mongo_analyst = PyMongo(
    app, uri="mongodb://analyst:analyst@devincimdb1027.westeurope.cloudapp.azure.com:30000/cloud_app")
mongo_user = PyMongo(
    app, uri="mongodb://user:user@devincimdb1027.westeurope.cloudapp.azure.com:30000/cloud_app")

departments = mongo_admin.db.departments
employees = mongo_admin.db.employees


@app.route('/')
def home():
    return "Hello world !"


@app.route('/user/')
def user():
    departments_list = departments.aggregate(
        [{	"$match": {"dept_no": "d005"}},
         {
            "$unwind": {
                "path": "$all_managers"
            }}
         ])
    employees_names = []
    for department in departments_list:
        print(department)
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

    print(employees_names)
    return render_template("index.html",
                           employees_names=employees_names)

@app.route('/admin/')
def admin():
    return "Admin view"

@app.route('/analyst/')
def analyst():
    return "Analyst view"

if __name__ == "__main__":
    app.run(debug=True)
