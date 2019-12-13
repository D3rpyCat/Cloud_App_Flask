# Cloud_App_Flask

MongoDB dashboard for a student project using the "employees" database.

## Packages

* virtualenv (for Linux) or virtualenvwrapper-win (for Windows)
* flask
* flask-login
* Flask-PyMongo
* Flask-WTF
* Werkzeug

## Installing & Running the app

* Install virtualenv/virtualenvwrapper-win

* Creating a virtual environment on **Windows** and activating it:

```bash
mkvirtualenv App
workon App
```

* Creating a virtual environment on **Linux** and activating it:

```bash
virtualenv App
source venv/bin/activate
```

You should see the name of your new environment on the left of your command line.

* Install all the other **required packages** listed above on your environment, using ```pip install```.

* **Launch the app:**

```bash
python views.py
```

* You can view the app at **localhost:5000**

* When you're done and you want to deactivate your environment:

```bash
deactivate
```

## Database source

https://dev.mysql.com/doc/employee/en/
