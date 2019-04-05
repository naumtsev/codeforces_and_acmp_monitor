#!/usr/bin/python
# -*- coding: utf-8 -*-
from requests import get
from flask import Flask, render_template, request, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectField, FileField
from wtforms.widgets import TextArea, TextInput
from wtforms.validators import DataRequired, Email
import time
from get_attempts import get_attempts_from_acmp, get_attempts_from_codeforces

TIME_UPDATE = time.time()

DEBUG = True
STATUS_EMPTY = 'EM'
CODEFORCES_STRING = 'cf'
ACMP_STRING = 'acmp'



def load_groupsofproblems():
    file = open('static/groupsofproblems.txt', 'r', encoding='utf-8')
    data = file.readlines()
    buffer = []
    sz = len(data)

    if(len(data) % 2 != 0):
        sz -= 1
    for i in range(0, sz, 2):
        title = data[i].strip()
        problems = data[i + 1].split()
        buffer.append((title, problems))
    file.close()
    return buffer



ADMINS = dict()
users = dict()

groupsofproblems = []
tables = []


def update_users():
    global users
    users.clear()
    file = open('static/users.txt', 'r', encoding='utf-8')
    b_users = file.readlines()
    file.close()
    for i in range(len(b_users)):
        cf_handle, acmp_id = map(str, b_users[i].split())
        users[cf_handle] = {CODEFORCES_STRING: cf_handle}

        if(acmp_id == STATUS_EMPTY):
            users[cf_handle][ACMP_STRING] = None
        else:
            users[cf_handle][ACMP_STRING] = acmp_id


def update_problems():
    global groupsofproblems, tables
    tables.clear()
    groupsofproblems = load_groupsofproblems()
    groupsofproblems.reverse()
    for title, problems in groupsofproblems:
        problems_buffer = []
        cnt = 0
        for p in problems:

            site, name_problem = map(str, p.split('_'))
            if(site == CODEFORCES_STRING):
                i = name_problem
                name = ''
                number = ''
                for j in i:
                    if j.isdigit():
                        number += j
                    else:
                        name += j
                problems_buffer.append((chr(cnt + ord('A')), number, name, CODEFORCES_STRING))
            elif site == ACMP_STRING:
                name = name_problem
                problems_buffer.append((chr(cnt + ord('A')), name, name, ACMP_STRING))
            cnt += 1

        tables.append((title, problems_buffer, []))

        for user in users:
            solved_codeforces = get_attempts_from_codeforces(users[user][CODEFORCES_STRING])
            solved_acmp = []
            if users[user][ACMP_STRING]:
                solved_acmp = get_attempts_from_acmp(users[user][ACMP_STRING])
            statusofproblems = []
            cnt_solved = 0
            for problem in problems:
                solved = False
                site, name_problem = map(str, problem.split('_'))
                if(site == ACMP_STRING):
                    if name_problem in solved_acmp:
                        solved = True
                elif(site == CODEFORCES_STRING):
                    if name_problem in solved_codeforces:
                        solved = True

                if solved:
                    statusofproblems.append('+')
                    cnt_solved += 1
                else:
                    statusofproblems.append('-')

            tables[-1][2].append((user, statusofproblems, cnt_solved))
        tables[-1][2].sort(key=lambda x: -x[2])


    global TIME_UPDATE
    TIME_UPDATE = time.time()


def load_admins():
    file = open('static/admins.txt', 'r', encoding='utf-8')
    data = file.readlines()

    for i in data:
        buffer = i.split()
        log, pas = buffer[0], buffer[1]
        ADMINS[log] = pas

    file.close()


load_admins()
update_users()
update_problems()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'e70lIUUoXRKlXc5VUBmiJ9Hdi'


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    global TIME_UPDATE
    NOW_TIME = time.time()
    if(NOW_TIME - TIME_UPDATE >= 60):
        TIME_UPDATE = NOW_TIME
        update_problems()
    return render_template('index.html', TABLE=tables, session=session, last_update=int(NOW_TIME - TIME_UPDATE), CODEFORCES_STRING=CODEFORCES_STRING, ACMP_STRING=ACMP_STRING)


@app.route('/update/1', methods=['GET', 'POST'])
def now_update_problems():
    update_problems()
    return redirect('/')


@app.route('/update/2', methods=['GET', 'POST'])
def now_update_users():
    update_users()
    update_problems()
    return redirect('/')


@app.errorhandler(404)
def not_found_error(error):
    return redirect('/')


class LoginForm(FlaskForm):
    username = StringField('Login:', validators=[DataRequired()], widget=TextInput())
    password = StringField('Password:', validators=[DataRequired()], widget=TextInput())
    submit = SubmitField('Отправить')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'login' in session:
        return redirect('/')
    form = LoginForm()

    if form.validate_on_submit():
        login = form.username.data
        password = form.password.data
        if login in ADMINS:
            if(ADMINS[login] == password):
                session['login'] = login
                return redirect('/')
            else:
                return render_template('login.html', form = form, status=1)
        else:
            return render_template('login.html', form=form, status=1)
    return render_template('login.html', form = form)


@app.route('/logout')
def logout():
    session.pop('login',0)
    return redirect('/')


@app.route('/edittasks', methods=['GET', 'POST'])
def edittasks():
    if 'login' not in session:
        return redirect('/')

    NOW_TIME = time.time()
    if request.method == 'GET':
        file = open('static/groupsofproblems.txt', 'r', encoding='utf-8')
        data = file.read()
        file.close()
        return render_template('editfile.html',session=session, nowtitle='Edit Tasks',
                               defaulttext=data, last_update= max(0, int(NOW_TIME - TIME_UPDATE)))
    if request.method == 'POST':
        text = request.form['textfield']
        file = open('static/groupsofproblems.txt', 'w', encoding='utf-8')
        data = file.writelines(text.split('\n'))
        file.close()
        return redirect('/update/1')


@app.route('/editusers', methods=['GET', 'POST'])
def editusers():
    if 'login' not in session:
        return redirect('/')

    NOW_TIME = time.time()
    if request.method == 'GET':
        file = open('static/users.txt', 'r', encoding='utf-8')
        data = file.read()
        file.close()
        return render_template('editfile.html',session=session, nowtitle='Edit users',
                               defaulttext=data, last_update=max(0, int(NOW_TIME - TIME_UPDATE)))
    if request.method == 'POST':
        text = request.form['textfield'].split('\n')
        file = open('static/users.txt', 'w', encoding='utf-8')
        file.writelines(text)
        file.close()
        return redirect('/update/2')


@app.route('/editadmins', methods=['GET', 'POST'])
def editadmins():
    if 'login' not in session:
        return redirect('/')

    NOW_TIME = time.time()
    if request.method == 'GET':
        file = open('static/admins.txt', 'r', encoding='utf-8')
        data = file.read()
        file.close()
        return render_template('editfile.html',session=session, nowtitle='Edit admins',
                               defaulttext=data, last_update=max(0, int(NOW_TIME - TIME_UPDATE)))

    if request.method == 'POST':
        text = request.form['textfield'].split('\n')
        file = open('static/admins.txt', 'w', encoding='utf-8')
        file.writelines(text)
        file.close()
        load_admins()
        return redirect('/')

@app.route('/notebook', methods=['GET', 'POST'])
def editnotebook():
    if 'login' not in session:
        return redirect('/')

    NOW_TIME = time.time()
    if request.method == 'GET':
        file = open('static/notebook.txt', 'r', encoding='utf-8')
        data = file.read()
        file.close()
        return render_template('editfile.html',session=session, nowtitle='Edit notebook',
                               defaulttext=data, last_update=max(0, int(NOW_TIME - TIME_UPDATE)))

    if request.method == 'POST':
        text = request.form['textfield'].split('\n')
        file = open('static/notebook.txt', 'w', encoding='utf-8')
        file.writelines(text)
        file.close()
        return redirect('/')


if DEBUG:
    app.run(port=8080, host='127.0.0.1')
