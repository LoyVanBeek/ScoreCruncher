#! /usr/bin/env python
import os
import sys
import re
from flask import Flask, session
# from flask.ext.session import Session
from flask import request, render_template, flash, redirect, url_for
from wtforms import Form, Field, BooleanField, StringField, DateTimeField, TextAreaField, IntegerField, PasswordField, validators
from challenge import Challenge

app = Flask(__name__)
# sess = Session()

scoresheets_dir = "~/Dropbox/RoboCupTC/RuleBook/scoresheets/"

class Scoresheet(Form):
    username = StringField('Referee', [validators.Length(min=3, max=25)])
    team_name = StringField('Team name', [validators.Length(min=3, max=25)])
    # date = DateTimeField("Date")
    attempt = IntegerField("Attempt")

def generate_field_for_achievement(achievement):
    field_key = achievement.description.replace(" ", "_")
    field_desc = achievement.description + " [{occ}x{score}]".format(occ=achievement.occurrences, score=achievement.score_per_occurence)
    return field_key, IntegerField(description=field_desc,
                                   validators=[validators.NumberRange(min=0, max=achievement.max_total)])

def generate_form_for_challenge(challenge):
    class TestSheet(Scoresheet):
        pass

    for achievement in challenge:
        name, field = generate_field_for_achievement(achievement)
        setattr(TestSheet, name, field)

    return TestSheet()

@app.route('/scoresheet/<string:testname>', methods=['GET', 'POST'])
def scoresheet(testname):
    sheet_path = os.path.expanduser(os.path.join(scoresheets_dir, testname+".tex"))
    chall = Challenge.from_scoresheet(open(sheet_path))
    form = generate_form_for_challenge(chall)
    
    if request.method == 'POST' and form.validate():
        # TODO: save scores
        flash('Thanks for the scores')
        return redirect(url_for("scoresheet/{testname}".format(testname=testname)))
    return render_template('scoresheet.html', form=form)

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.config['SESSION_TYPE'] = 'filesystem'

    try:
        scoresheets_dir = sys.argv[1]
    except IndexError:
        app.logger.warning("Please supply a path to the scoresheets directory of the Rulebook. Now using default")

    app.debug = True
    app.run()