#! /usr/bin/env python
import os
import re
from flask import Flask, session
# from flask.ext.session import Session
from flask import request, render_template, flash, redirect, url_for
from wtforms import Form, Field, BooleanField, StringField, DateTimeField, TextAreaField, IntegerField, PasswordField, validators

app = Flask(__name__)
# sess = Session()

class Scoresheet(Form):
    username = StringField('Referee', [validators.Length(min=3, max=25)])
    team_name = StringField('Team name', [validators.Length(min=3, max=25)])
    date = DateTimeField("Date")
    attempt = IntegerField("Attempt")

@app.route('/help_me_carry', methods=['GET', 'POST'])
def help_me_carry():
    class TestSheet(Scoresheet):
        pass

    sheet_path = "/home/loy/Dropbox/RoboCupTC/RuleBook/scoresheets/HelpMeCarry.tex"
    sheet_file = open(sheet_path)
    sheet_lines = sheet_file.readlines()

    def generate_field(line):
        """Example line:
            \scoreitem{10}{Follow operator outside the arena}"""
        content = line.strip()  # Remove whitespace
        if line.startswith("\scoreitem") or True:
            elements = re.findall('\{(.*?)\}', line)
            max_score = elements[0]
            achievement_desc = elements[1]
            field_key = achievement_desc.replace(" ", "_")
            achievement_desc += "({score})".format(score=max_score)
            return field_key, IntegerField(description=achievement_desc, validators=[validators.NumberRange(min=0, max=max_score)])

    for line in sheet_lines:
        if "\scoreitem" in line:
            name, field = generate_field(line)
            if field:
                # name = field.description.replace(" ", "_")
                setattr(TestSheet, name, field)

    form = TestSheet(request.form)
    
    if request.method == 'POST' and form.validate():
        for k,v in form.__dict__.items():
            print k, v
        flash('Thanks for registering')
        # return redirect(url_for('login'))
    return render_template('register.html', form=form)

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        print(form.username.data, form.email.data, form.password.data)
        # db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)

    app.debug = True
    app.run()