from flask import Flask, render_template, request
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
