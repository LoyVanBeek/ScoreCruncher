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

def generate_form_for_scoresheet(sheet_file):
    class TestSheet(Scoresheet):
        pass

    sheet_lines = sheet_file.readlines()

    for line in sheet_lines:
        if "\scoreitem" in line:
            name, field = generate_field(line)
            if field:
                # name = field.description.replace(" ", "_")
                setattr(TestSheet, name, field)

    form = TestSheet(request.form)
    return form

@app.route('/help_me_carry', methods=['GET', 'POST'])
def help_me_carry():
    form = generate_form_for_scoresheet(open("/home/loy/Dropbox/RoboCupTC/RuleBook/scoresheets/HelpMeCarry.tex"))
    
    if request.method == 'POST' and form.validate():
        for k,v in form.__dict__.items():
            print k, v
        flash('Thanks for the scores')
        return redirect(url_for("help_me_carry"))
    return render_template('scoresheet.html', form=form)

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)

    app.debug = True
    app.run()