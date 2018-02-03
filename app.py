################ Imports ################
from flask import Flask, Response, render_template, redirect, flash, url_for, send_from_directory, jsonify, request, session, g
from flask_debugtoolbar import DebugToolbarExtension
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
import calendar
from datetime import datetime, date, time, timedelta
from forms import TestForm
import bcrypt
from waitress import serve
from flask_restful import Resource, Api
import sys

## Local Imports ##
from init_period import *
## Local Imports ##
################ Imports ################


################ MongoDB Connection ################
app = Flask(__name__)
api = Api(app)
client = MongoClient()
db = client.amlis
################ MongoDB Connection ################

################ App Settings ################
# the toolbar is only enabled in debug mode:
app.debug = False
# WTF-FORMS have CSRF enabled by default. We disable it here for now
# If we keep the default (enabled), then we need to make sure
#+ the SECRET_KEY is set
app.config['WTF_CSRF_ENABLED'] = False
# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'AFGC123123456789'

toolbar = DebugToolbarExtension(app)
################## App Settings ################

################## Favicon ##################
@app.route("/favicon.ico")
def favicon():
    return(url_for('static', filename='favicon.ico'))
################## Favicon ##################

#################### Period Function ####################
def choose_period():
    collection = db.period
    all_period_df = pd.DataFrame(list(collection.find({})))
    all_period = all_period_df.to_dict(orient="records")
    return all_period

def period(team, year_period, month_period):
    collection = db.period
    period_df = pd.DataFrame(list(collection.find({'team': team, 'year': year_period, 'month': month_period})))
    if period_df.empty:
        print("Attempting to run uninitialized period.")
        term = {
            "team": team,
            "year": str(year_period),
            "month": str(month_period)
            }
        insert_row = collection.insert_one(term)
        print("Insert_row: ", insert_row)
        if insert_row.inserted_id:
            print(insert_row.inserted_id)
            print("===================")
            print("From Period POST Id:", insert_row.inserted_id)
            print("===================")
            print("Period created!")
            init_days(team, year_period, month_period)
            init_s(team, year_period, month_period)
            init_q(team, year_period, month_period)
            init_d(team, year_period, month_period)
            init_i(team, year_period, month_period)
            init_p(team, year_period, month_period)
            return term
        else:
            print("There was error #1 in your insert!")
            print(insert_row.raw_result)
            return []
    else:
        #print("Period found")
        term = period_df.to_dict(orient="records")[0]
    return term
#################### Period Function ####################


#################### Dash ToDos Function ####################
def todos(group, year, month, rowlimit = 10, collimit = 60):
    more = False
    collection = db.todos
    dash_todo_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month}, {"_id":1, "DESCRIPTION":1, "DISPLAYNAME":1, "COMPLETIONDATE":1, "STATUS":1, "TOPIC":1})))
    if dash_todo_df.empty:
        dash_todo_list = {}
    else:
        # dash_todo_df = dash_todo_df.groupby(['DESCRIPTION', 'DISPLAYNAME', 'COMPLETIONDATE', 'STATUS'])
        # dash_todo_df = dash_todo_df.reset_index()
        # dash_todo_df.columns = ['DESCRIPTION', 'DISPLAYNAME', 'COMPLETIONDATE', 'STATUS']
        # dash_todo_df['ROWNO'] = dash_todo_df.index + 1
        # dash_todo_df['COMPLETIONDATE'] = pd.to_datetime(dash_todo_df['COMPLETIONDATE']).dt.date
        if (dash_todo_df._id.count() > rowlimit):
            dash_todo_df = dash_todo_df.head(rowlimit)
            more = True
        dash_todo_list = dash_todo_df.to_dict(orient='records')
    return dash_todo_list, more
#################### ToDos Function ####################

#################### Topic ToDos Function ####################
def column_todo(team, year, month, topic):
    collection = db.todos
    dash_todo_df = pd.DataFrame(list(collection.find({"TEAM":team, "YEAR": year, "MONTH": month, "TOPIC": topic},
    {"_id":1, "STARTDATE":1, "DESCRIPTION":1, "TASKNAME":1, "DISPLAYNAME":1, "COMPLETIONDATE":1, "STATUS":1, "TOPIC":1})))
    if dash_todo_df.empty:
        dash_todo_list = {}
        #print("VACIO")
    else:
        # dash_todo_df['COMPLETIONDATE'] = pd.to_datetime(dash_todo_df['COMPLETIONDATE']).dt.date
        dash_todo_list = dash_todo_df.to_dict(orient='records')
    return dash_todo_list
#################### ToDos Function ####################

#################### Weekly Summaries Function ####################
def weeklysum(group, year, month):
    collection = db.weeklysum
    dash_week_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month})))
    if dash_week_df.empty:
        dash_week_list = {}
    else:
        dash_week_list = dash_week_df.to_dict(orient='records')
    return dash_week_list
#################### Weekly Summaries Function ####################

#################### Dash Manual Function ####################
def manual_incNearMiss(group, year, month):
    collection = db.manual
    dash_manual_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month, "TABLE":"incNearMiss"} )))
    if dash_manual_df.empty:
        dash_manual_list = {}
    else:
        # dash_manual_df['DATE'] = pd.to_datetime(dash_manual_df['DATE']).dt.date
        dash_manual_list = dash_manual_df.to_dict(orient='records')
    return dash_manual_list

def manual_incFromSite(group, year, month):
    collection = db.manual
    dash_manual_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month, "TABLE": "incFromSite"})))
    if dash_manual_df.empty:
        dash_manual_list = {}
    else:
        #dash_manual_df['VALUE'] = dash_manual_df['VALUE'].astype(int)
        dash_manual_list = dash_manual_df.to_dict(orient='records')
    return dash_manual_list

def manual_training(group, year, month):
    collection = db.manual
    dash_manual_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month, "TABLE": "training"})))
    if dash_manual_df.empty:
        dash_manual_list = {}
        #print("esta vacio")
    else:
        #dash_manual_df['VALUE'] = dash_manual_df['VALUE'].astype(int)
        dash_manual_list = dash_manual_df.to_dict(orient='records')
        #print("hay data")
    return dash_manual_list

def manual_periodic(group, year, month):
    collection = db.manual
    dash_manual_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month, "TABLE": "periodic"})))
    if dash_manual_df.empty:
        dash_manual_list = {}
        #print("esta vacio")
    else:
        #dash_manual_df['VALUE'] = dash_manual_df['VALUE'].astype(int)
        dash_manual_list = dash_manual_df.to_dict(orient='records')
        #print("hay data")
    return dash_manual_list

def manual_taskIncidents(group, year, month):
    collection = db.manual
    dash_manual_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month, "TABLE": "taskIncidents"})))
    if dash_manual_df.empty:
        dash_manual_list = {}
    else:
        #dash_manual_df['VALUE'] = dash_manual_df['VALUE'].astype(int)
        dash_manual_list = dash_manual_df.to_dict(orient='records')
    return dash_manual_list

def manual_ismStatus(group, year, month):
    collection = db.manual
    dash_manual_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month, "TABLE": "ismStatus"})))
    if dash_manual_df.empty:
        dash_manual_list = {}
    else:
        #dash_manual_df['VALUE'] = dash_manual_df['VALUE'].astype(int)
        dash_manual_list = dash_manual_df.to_dict(orient='records')
    return dash_manual_list

def manual_systemAvailability(group, year, month):
    collection = db.manual
    dash_manual_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month, "TABLE": "systemAvailability"})))
    if dash_manual_df.empty:
        dash_manual_list = {}
    else:
        #dash_manual_df['VALUE'] = dash_manual_df['VALUE'].astype(int)
        dash_manual_list = dash_manual_df.to_dict(orient='records')
    return dash_manual_list

def manual_tracking(group, year, month):
    collection = db.manual
    dash_manual_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month, "TABLE": "tracking"})))
    if dash_manual_df.empty:
        dash_manual_list = {}
    else:
        #dash_manual_df['VALUE'] = dash_manual_df['VALUE'].astype(int)
        dash_manual_list = dash_manual_df.to_dict(orient='records')
    return dash_manual_list

def manual_taskIncWos(group, year, month):
    collection = db.manual
    dash_manual_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month, "TABLE": "taskIncWos"})))
    if dash_manual_df.empty:
        dash_manual_list = {}
    else:
        #dash_manual_df['VALUE'] = dash_manual_df['VALUE'].astype(int)
        dash_manual_list = dash_manual_df.to_dict(orient='records')
    return dash_manual_list

def manual_bundle(group, year, month):
    incNearMiss = manual_incNearMiss(group, year, month)
    incFromSite = manual_incFromSite(group, year, month)
    training = manual_training(group, year, month)
    periodic = manual_periodic(group, year, month)
    taskIncidents = manual_taskIncidents(group, year, month)
    ismStatus = manual_ismStatus(group, year, month)
    systemAvailability = manual_systemAvailability(group, year, month)
    tracking = manual_tracking(group, year, month)
    taskIncWos = manual_taskIncWos(group, year, month)
    return {'incNearMiss': incNearMiss, 'incFromSite': incFromSite, 'training': training, 'periodic': periodic, 'taskIncidents': taskIncidents, 'ismStatus': ismStatus, 'systemAvailability': systemAvailability, 'tracking': tracking, 'taskIncWos': taskIncWos}
#################### Dash Manual Function ####################

#################### Topic Manual Function ####################
def manual_safety(group, year, month, topic):
    days = column_days(group, year, month, topic)
    incNearMiss = manual_incNearMiss(group, year, month)
    #print(incNearMiss)
    incFromSite = manual_incFromSite(group, year, month)
    #print(incFromSite)
    weekly = weeklysum(group, year, month)
    #print(weekly)
    return {'incNearMiss': incNearMiss, 'incFromSite': incFromSite, 'weekly': weekly, 'days': days}

def manual_quality(group, year, month, topic):
    days = column_days(group, year, month, topic)
    # nccappa = manual_nccappa()
    training = manual_training(group, year, month)
    #print(training)
    periodic = manual_periodic(group, year, month)
    todo = column_todo(group, year, month, topic)
    #print(todo)
    weekly = weeklysum(group, year, month)
    #print(weekly)
    return {'training': training, 'periodic': periodic, 'todo': todo, 'weekly': weekly, 'days': days}

def manual_delivery(group, year, month, topic):
    days = column_days(group, year, month, topic)
    taskIncidents = manual_taskIncidents(group, year, month)
    #print(taskIncidents)
    ismStatus = manual_ismStatus(group, year, month)
    #print(ismStatus)
    weekly = weeklysum(group, year, month)
    return {'taskIncidents': taskIncidents, 'ismStatus': ismStatus, 'weekly': weekly, 'days': days}

def manual_inventory(group, year, month, topic):
    days = column_days(group, year, month, topic)
    systemAvailability = manual_systemAvailability(group, year, month)
    #print(systemAvailability)
    weekly = weeklysum(group, year, month)
    return {'systemAvailability': systemAvailability, 'weekly': weekly, 'days': days}

def manual_productivity(group, year, month, topic):
    days = column_days(group, year, month, topic)
    tracking = manual_tracking(group, year, month)
    taskIncWos = manual_taskIncWos(group, year, month)
    # maxwo = manual_maxwo()
    #print(maxwo[0])
    weekly = weeklysum(group, year, month)
    return {'tracking': tracking, 'taskIncWos': taskIncWos, 'weekly': weekly, 'days': days}
#################### Topic Manual Function ####################

#################### Dash Days Function ####################
def days(group, year, month):
    collection = db.days
    dash_days_df = pd.DataFrame(list(collection.find({"TEAM":group, "YEAR": year, "MONTH": month})))
    if dash_days_df.empty:
        dash_days_list = {}
    else:
        dash_days_list = dash_days_df.to_dict(orient='records')
    return dash_days_list
#################### Dash Days Function ####################

#################### Topic Days Function ####################
def column_days(team, year, month, topic):
    collection = db.days
    dash_days_df = pd.DataFrame(list(collection.find({"TEAM":team, "YEAR": year, "MONTH": month, "TOPIC": topic})))
    if dash_days_df.empty:
        dash_days_list = {}
    else:
        dash_days_list = dash_days_df.to_dict(orient='records')
    return dash_days_list
#################### Topic Days Function ####################

#################### Dash Attendance Function ####################
def attendance(team, year_period, month_period):
    collection = db.attendance
    dash_attend_df = pd.DataFrame(list(collection.find({"TEAM":team, "YEAR": year_period, "MONTH": month_period})))
    if dash_attend_df.empty:
        dash_attend_list = {}
    else:
        dash_attend_list = dash_attend_df.to_dict(orient='records')
    return dash_attend_list
#################### Dash Attendance Function ####################

#################### Attendance Route ####################
@app.route("/dash/attendance/<team>/<year_period>/<month_period>")
def attend(team, year_period, month_period):
    collection = db.attendance
    term = period(team, year_period, month_period)
    dash_attend_df = pd.DataFrame(list(collection.find({"TEAM":team, "YEAR": year_period, "MONTH": month_period})))
    if dash_attend_df.empty:
        dash_attend_list = {}
    else:
        dash_attend_list = dash_attend_df.to_dict(orient='records')
    return render_template('amlis/edit_attendance.html', term=[term], attendata=dash_attend_list, team=team, year=year_period, month=month_period)
#################### Attendance Route ####################

#################### Topic Route ####################
@app.route("/dash/<team>/<year_period>/<month_period>/<topic>")
def main_bundle(team, year_period, month_period, topic):
    #The following block pulls data from MongoDB for sections that are common across all topics
    todo_data = column_todo(team, year_period, month_period, topic)
    term = period(team, year_period, month_period)
    #weekly_data = column_weekly(team, year_period, month_period)
    #days_data = column_days(team, year_period, month_period, topic)
    #metrics_data = column_metrics(team, year_period, month_period, topic)
    #The following block pull data that is specific to topic, and calls the appropriate template.
    if topic == 's':
        safety = manual_safety(team, year_period, month_period, topic)
        return render_template('amlis/s/s_override.html', safety_data=safety, tododata=todo_data, term=[term], team=team, year=year_period, month=month_period, topic=topic)
    elif topic == 'q':
        quality = manual_quality(team, year_period, month_period, topic)
        return render_template('amlis/q/q_override.html', quality_data=quality, tododata=todo_data, term=[term], team=team, year=year_period, month=month_period, topic=topic)
    elif topic == 'd':
        delivery = manual_delivery(team, year_period, month_period, topic)
        return render_template('amlis/d/d_override.html', delivery_data=delivery, term=[term], team=team, year=year_period, month=month_period, topic=topic)
    elif topic == 'i':
        inventory = manual_inventory(team, year_period, month_period, topic)
        return render_template('amlis/i/i_override.html', inventory_data=inventory, term=[term], team=team, year=year_period, month=month_period, topic=topic)
    elif topic == 'p':
        productivity = manual_productivity(team, year_period, month_period, topic)
        return render_template('amlis/p/p_override.html', productivity_data=productivity, term=[term], team=team, year=year_period, month=month_period, topic=topic)
#################### Topic Route ####################

#################### Dash Route without Period ####################
@app.route("/dash/<team>")
def team_noperiod(team):
    year_period = datetime.now().year
    month_period= datetime.now().month
    return redirect("/dash/" + team + "/" + str(year_period) + "/" + str(month_period))
#################### Dash Route without Period ####################

#################### Dash Route ####################
@app.route("/dash/<team>/<year_period>/<month_period>")
def team_period(team, year_period, month_period):
    all_periods = choose_period()
    # returns a json as a service representing the entire dataset
    term = period(team, year_period, month_period)
    #print("Term: ", term)
    if len(term)==0:
        print("Period not found!!!")
    else:
        # nc_data, nc_more = nccapa()
        # wo_data, wo_more = maxwo(5)
        todo_s = column_todo(term['team'], term['year'], term['month'], topic="s")
        todo_q = column_todo(term['team'], term['year'], term['month'], topic="q")
        todo_d = column_todo(term['team'], term['year'], term['month'], topic="d")
        todo_i = column_todo(term['team'], term['year'], term['month'], topic="i")
        todo_p = column_todo(term['team'], term['year'], term['month'], topic="p")
        week_data = weeklysum(term['team'], term['year'], term['month'])
        attend_data = attendance(term['team'], term['year'], term['month'])
        # print("Attendance data:", attend_data)
        # week_data = weeklysum(team, year_period, month_period)
        # print("Week Data: ", week_data)
        day_data = days(term['team'], term['year'], term['month'])
        manual_data = manual_bundle(term['team'], term['year'], term['month'])
        #print(test_data)
        #return render_template('todos.html', data=term)
        return render_template('amlis/dash.html', term=[term], team=team, todos=todo_s, todoq=todo_q, todod=todo_d, todoi=todo_i, todop=todo_p, weekdata=week_data, daydata=day_data, manualdata = manual_data, attendata=attend_data)#, coltododata=col_todo_data, referrer = referrer_url, periods = all_periods)

#################### Initializers Functions ####################
def init_days(team, year_period, month_period):
    collection = db.days
    weekday, number_of_days = monthrange(int(year_period), int(month_period))
    for eachday in range(1, number_of_days + 1):
        for eachtopic in ['s', 'q', 'd', 'i', 'p']:
            update_result = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":eachtopic, "DAY":eachday},
                        {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":eachtopic, "DAY":eachday, "VALUE": "white"},
                        upsert=True)
            if not update_result.acknowledged:
                print("Error upserting:", eachday, eachtopic)

def init_s(team, year_period, month_period):
    collection = db.manual
    topic = 's'
    update_incNearMiss = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'incNearMiss'},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "DATE": " ", "DESCRIPTION": " ", "OWNER": " ", "TABLE": 'incNearMiss'},
                    upsert=True)
    if not update_incNearMiss.acknowledged:
        print("Error upserting incNearMiss:", topic)
    update_incFromSite = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'incFromSite'},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "Safety Info. Cascade", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'incFromSite'},
                    upsert=True)
    if not update_incFromSite.acknowledged:
        print("Error upserting incFromSite:", topic)

def init_q(team, year_period, month_period):
    collection = db.manual
    topic = 'q'
    update_training = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'training', "METRIC": "Training"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "Training", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'training'},
                    upsert=True)
    if not update_training.acknowledged:
        print("Error upserting training:", topic)
    update_pdtraining = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'training', "METRIC": "Past Due Trainings"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "Past Due Trainings", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'training'},
                    upsert=True)
    if not update_pdtraining.acknowledged:
        print("Error upserting pdtraining:", topic)
    update_periodic = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'periodic'},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "SYSTEMITEM": " ", "GMPREVIEW": " ", "NONPRIVILEGED": " ", "PRIVILEGED": " ",
                     "SERVICEACCOUNT": " ", "DUE": datetime(2099, 1, 1, 0, 0, 0), "STATUS": " ", "TABLE": 'periodic'},
                    upsert=True)
    if not update_periodic.acknowledged:
        print("Error upserting pdtraining:", topic)

def init_d(team, year_period, month_period):
    collection = db.manual
    topic = 'd'
    update_taskIncidents_taskWA = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncidents', "METRIC": "TASK - WEEK AHEAD"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "TASK - WEEK AHEAD", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncidents'},
                    upsert=True)
    if not update_taskIncidents_taskWA.acknowledged:
        print("Error upserting taskIncidents Task Week Ahead:", topic)
    update_taskIncidents_taskPD = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncidents', "METRIC": "TASK - PAST DUE"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "TASK - PAST DUE", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncidents'},
                    upsert=True)
    if not update_taskIncidents_taskPD.acknowledged:
        print("Error upserting taskIncidents Task Past Due:", topic)
    update_taskIncidents_incWA = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncidents', "METRIC": "INCIDENTS - WEEK AHEAD"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "INCIDENTS - WEEK AHEAD", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncidents'},
                    upsert=True)
    if not update_taskIncidents_incWA.acknowledged:
        print("Error upserting taskIncidents Incidents Week Ahead:", topic)
    update_taskIncidents_incPD = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncidents', "METRIC": "INCIDENTS - PAST DUE"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "INCIDENTS - PAST DUE", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncidents'},
                    upsert=True)
    if not update_taskIncidents_incPD.acknowledged:
        print("Error upserting taskIncidents Incidents Past Due:", topic)
    update_taskIncidents_incWAIT = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncidents', "METRIC": "INCIDENTS - WAITING"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "INCIDENTS - WAITING", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncidents'},
                    upsert=True)
    if not update_taskIncidents_incWAIT.acknowledged:
        print("Error upserting taskIncidents Incidents Waiting:", topic)
    update_taskIncidents_woOpen = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncidents', "METRIC": "WORK ORDERS - OPEN"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "WORK ORDERS - OPEN", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncidents'},
                    upsert=True)
    if not update_taskIncidents_woOpen.acknowledged:
        print("Error upserting taskIncidents Work Orders Open:", topic)
    update_taskIncidents_woPD = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncidents', "METRIC": "WORK ORDERS - PAST DUE"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "WORK ORDERS - PAST DUE", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncidents'},
                    upsert=True)
    if not update_taskIncidents_woOpen.acknowledged:
        print("Error upserting taskIncidents Work Orders Past Due:", topic)
    update_ismStatus_impPD = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'ismStatus'},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "ISM - IMP. PAST DUE", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'ismStatus'},
                    upsert=True)
    if not update_ismStatus_impPD.acknowledged:
        print("Error upserting ismStatus Imp. Past Due :", topic)
    update_ismStatus_impWA = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'ismStatus', "METRIC": "ISM - IMP. WEEK AHEAD"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "ISM - IMP. WEEK AHEAD", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'ismStatus'},
                    upsert=True)
    if not update_ismStatus_impWA.acknowledged:
        print("Error upserting ismStatus Imp. Week Ahead :", topic)
    update_ismStatus_DR = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'ismStatus', "METRIC": "ISM - DEPTMT. REVIEW"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "ISM - DEPTMT. REVIEW", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'ismStatus'},
                    upsert=True)
    if not update_ismStatus_DR.acknowledged:
        print("Error upserting ismStatus DEPTMT. REVIEW :", topic)
    update_ismStatus_CPD = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'ismStatus', "METRIC": "ISM - CLOSURE PAST DUE"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "METRIC": "ISM - CLOSURE PAST DUE", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'ismStatus'},
                    upsert=True)
    if not update_ismStatus_CPD.acknowledged:
        print("Error upserting ismStatus Closure Past Due :", topic)

def init_i(team, year_period, month_period):
    collection = db.manual
    topic = 'i'
    update_systemAvailability_mesMI = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'systemAvailability', "METRIC": "MES - MAJOR INCIDENTS"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "MES - MAJOR INCIDENTS", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'systemAvailability'},
                    upsert=True)
    if not update_systemAvailability_mesMI.acknowledged:
        print("Error upserting systemAvailability Mes - Major Incidents :", topic)
    update_systemAvailability_mesDown = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'systemAvailability', "METRIC": "MES - DOWNTIME"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "MES - DOWNTIME", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'systemAvailability'},
                    upsert=True)
    if not update_systemAvailability_mesDown.acknowledged:
        print("Error upserting systemAvailability Mes - Downtime :", topic)
    update_systemAvailability_mesTotal = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'systemAvailability', "METRIC": "MES - TOTAL TIME"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "MES - TOTAL TIME", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'systemAvailability'},
                    upsert=True)
    if not update_systemAvailability_mesTotal.acknowledged:
        print("Error upserting systemAvailability Mes - Total Time :", topic)
    update_systemAvailability_mesPer = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'systemAvailability', "METRIC": "MES - %"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "MES - %", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'systemAvailability'},
                    upsert=True)
    if not update_systemAvailability_mesPer.acknowledged:
        print("Error upserting systemAvailability Mes - % :", topic)
    update_systemAvailability_piMI = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'systemAvailability', "METRIC": "PI - MAJOR INCIDENTS"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "PI - MAJOR INCIDENTS", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'systemAvailability'},
                    upsert=True)
    if not update_systemAvailability_piMI.acknowledged:
        print("Error upserting systemAvailability Pi - Major Incidents :", topic)
    update_systemAvailability_piDown = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'systemAvailability', "METRIC": "PI - DOWNTIME"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "PI - DOWNTIME", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'systemAvailability'},
                    upsert=True)
    if not update_systemAvailability_piDown.acknowledged:
        print("Error upserting systemAvailability Pi - Downtime :", topic)
    update_systemAvailability_piTotal = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'systemAvailability', "METRIC": "PI - TOTAL TIME"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "PI - TOTAL TIME", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'systemAvailability'},
                    upsert=True)
    if not update_systemAvailability_piTotal.acknowledged:
        print("Error upserting systemAvailability Pi - Total Time :", topic)
    update_systemAvailability_piPer = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'systemAvailability', "METRIC": "PI - %"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "PI - %", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'systemAvailability'},
                    upsert=True)
    if not update_systemAvailability_piPer.acknowledged:
        print("Error upserting systemAvailability Pi - % :", topic)

def init_p(team, year_period, month_period):
    collection = db.manual
    topic = 'p'
    update_tracking = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'tracking'},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC":topic, "DATEOPEN": " ", "SYSTEM": " ", "PROBLEM": " ", "DUEDATE": " ",
                     "PROBLEMINVESTIGATOR": " ", "STATUS": " ", "TABLE": 'tracking'},
                    upsert=True)
    if not update_tracking.acknowledged:
        print("Error upserting tracking:", topic)


    update_taskIncWos_taskOIP = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncWos', "METRIC": "TASKS - OPEN/INPROG/PENDING"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "TASKS - OPEN/INPROG/PENDING", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncWos'},
                    upsert=True)
    if not update_taskIncWos_taskOIP.acknowledged:
        print("Error upserting taskIncWos Tasks - Open In Progress Pending :", topic)
    update_taskIncWos_taskCC = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncWos', "METRIC": "TASKS - CLOSED/CANCELLED"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "TASKS - CLOSED/CANCELLED", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncWos'},
                    upsert=True)
    if not update_taskIncWos_taskCC.acknowledged:
        print("Error upserting taskIncWos Tasks - Closed Cancelled :", topic)
    update_taskIncWos_incOIP = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncWos', "METRIC": "INCIDENTS - OPEN/INPROG/PENDING"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "INCIDENTS - OPEN/INPROG/PENDING", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncWos'},
                    upsert=True)
    if not update_taskIncWos_incOIP.acknowledged:
        print("Error upserting taskIncWos Incidents - Open In Progress Pending :", topic)
    update_taskIncWos_incCC = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncWos', "METRIC": "INCIDENTS - CLOSED/CANCELLED"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "INCIDENTS - CLOSED/CANCELLED", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncWos'},
                    upsert=True)
    if not update_taskIncWos_incCC.acknowledged:
        print("Error upserting taskIncWos Incidents - Closed Cancelled :", topic)
    update_taskIncWos_woOIP = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncWos', "METRIC": "WORK ORDERS - OPEN/INPROG/PENDING"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "WORK ORDERS - OPEN/INPROG/PENDING", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncWos'},
                    upsert=True)
    if not update_taskIncWos_woOIP.acknowledged:
        print("Error upserting taskIncWos Work Orders - Open In Progress Pending :", topic)
    update_taskIncWos_woCC = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncWos', "METRIC": "WORK ORDERS - CLOSED/CANCELLED"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "WORK ORDERS - CLOSED/CANCELLED", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncWos'},
                    upsert=True)
    if not update_taskIncWos_woCC.acknowledged:
        print("Error upserting taskIncWos Work Orders - Closed Cancelled :", topic)
    update_taskIncWos_ismOIP = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncWos', "METRIC": "ISM CHANGES - OPEN/INPROG/PENDING"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "ISM CHANGES - OPEN/INPROG/PENDING", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncWos'},
                    upsert=True)
    if not update_taskIncWos_ismOIP.acknowledged:
        print("Error upserting taskIncWos ISM Changes - Open In Progress Pending :", topic)
    update_taskIncWos_ismCC = collection.replace_one({"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "TABLE": 'taskIncWos', "METRIC": "ISM CHANGES - CLOSED/CANCELLED"},
                    {"TEAM":team, "YEAR": year_period, "MONTH": month_period, "TOPIC": topic, "METRIC": "ISM CHANGES - CLOSED/CANCELLED", "one": "0", "two": "0", "three": "0",
                     "four": "0", "five": "0", "six": "0", "seven": "0", "eight": "0", "nine": "0", "ten": "0", "TABLE": 'taskIncWos'},
                    upsert=True)
    if not update_taskIncWos_ismCC.acknowledged:
        print("Error upserting taskIncWos ISM Changes - CLOSED/CANCELLED :", topic)
#################### Initializers Functions ####################

####### This section includes the API code for Attendance ###########
class AttendList(Resource):
    def get(self, team, year_period, month_period):
        collection = db.attendance
        form_cursor = collection.find({'TEAM': team, 'YEAR': year_period, 'MONTH': month_period})
        if form_cursor.count() > 0:
            form_data = list(form_cursor)
            # print(form_data)
            for item in form_data:
                for key, value in item.items():
                    if type(value)==date:
                        item[key]=value.strftime("%m/%d/%Y")
                    elif type(value)==ObjectId:
                        item[key]=str(value)
                    elif type(value)==time:
                        item[key]=value.strftime("%H:%M:%S")
                    elif type(value)==datetime:
                        item[key]=value.strftime("%m/%d/%Y")
            return form_data
        else:
            return []

api.add_resource(AttendList, '/api/attend/<string:team>/<string:year_period>/<string:month_period>')

class AttendItem(Resource):
    def put(self, team, year_period, month_period):
        """This function perform an update on an existing record"""
        collection = db.attendance
        form_data = request.form.to_dict()
        if '_id' in form_data:
            id = form_data.pop('_id')
            print("===================")
            print("From Attendance Put Id:",id)
            print("===================")
            print("Row will be updated: ", id)
#            try:
            update_record = {'$set':form_data}
            updated_row = collection.update_one({'_id': ObjectId(id) }, update_record)
            if updated_row.matched_count == 1:
                print("Row updated succesfully!")
            else:
                print("There was error #1 in your update!")
                print(updated_row.raw_result)
#            except:
#                print("There was error #2 in your update!")
        else:
            print("Not ObjectId received!")
        return

    def delete(self, team, year_period, month_period):
        """Delete document"""
        collection = db.attendance
        form_data = request.form.to_dict()
        if '_id' in form_data:
            # try:
            id = form_data.pop('_id')
            print("===================")
            print("From Attendance Delete Id:",id)
            print("===================")
            deleted_row = collection.delete_one({'_id': ObjectId(id)})
            #     if delete_row.delete_count != 1:
            #         print("Warning: Expected to delete 1 row, but deleted these many instead: ", delete_row.delete_count)
            #         print(delete_row.raw_result)
            # except:
            #     print("There was error #1 in your delete!")
            #     print(deleted_row.raw_result)
        else:
            print("Not ObjectId received!")
        return

    def post(self, team, year_period, month_period):
        """Creates a new document"""
        collection = db.attendance
        form_data = request.form.to_dict()
        # print("===========================")
        # print("post: ", form_data)
        # print("===========================")
        form_data['TEAM'] = team
        form_data['YEAR'] = year_period
        form_data['MONTH'] = month_period
        # print("===========================")
        # print("post: ", form_data)
        # print("===========================")
#        try:
        insert_row = collection.insert_one(form_data)
        if insert_row.inserted_id:
            print(insert_row.inserted_id)
            print("===================")
            print("From Attendance Post Id:", insert_row.inserted_id)
            print("===================")
        else:
            print("There was error #1 in your insert!")
            print(insert_row.raw_result)
#        except:
#            print("There was error #2 in your insert!")
        return


api.add_resource(AttendItem, '/api/attend/<string:team>/<string:year_period>/<string:month_period>')

#####################################

####### This section includes the API code for ToDo ###########
class TodoList(Resource):
    def get(self, team, year_period, month_period, topic):
        collection = db.todos
        form_cursor = collection.find({'TEAM': team, 'YEAR': year_period, 'MONTH': month_period, 'TOPIC': topic})
        if form_cursor.count() > 0:
            form_data = list(form_cursor)
            # print(form_data)
            for item in form_data:
                for key, value in item.items():
                    if type(value)==date:
                        item[key]=value.strftime("%m/%d/%Y")
                    elif type(value)==ObjectId:
                        item[key]=str(value)
                    elif type(value)==time:
                        item[key]=value.strftime("%H:%M:%S")
                    elif type(value)==datetime:
                        item[key]=value.strftime("%m/%d/%Y")
            return form_data
        else:
            return []
#            return { data: [], itemsCount: 0 }

api.add_resource(TodoList, '/api/todos/<string:team>/<string:year_period>/<string:month_period>/<string:topic>')

class TodoItem(Resource):
    def put(self, team, year_period, month_period, topic):
        """This function perform an update on an existing record"""
        collection = db.todos
        form_data = request.form.to_dict()
        print("===================")
        print("From Todo put: ", form_data)
        print("===================")
        if '_id' in form_data:
            id = form_data.pop('_id')
            print("===================")
            print("From Todo Put Id:",id)
            print("===================")
            print("Row will be updated: ", id)
#            try:
            update_record = {'$set':form_data}
            updated_row = collection.update_one({'_id': ObjectId(id) }, update_record)
            if updated_row.matched_count == 1:
                print("Row updated succesfully!")
            else:
                print("There was error #1 in your update!")
                print(updated_row.raw_result)
#            except:
#                print("There was error #2 in your update!")
        else:
            print("Not ObjectId received!")
        return

    def delete(self, team, year_period, month_period, topic):
        """Delete document"""
        collection = db.todos
        form_data = request.form.to_dict()
        if '_id' in form_data:
            # try:
            id = form_data.pop('_id')
            print("===================")
            print("From Todo Delete Id:",id)
            print("===================")
            deleted_row = collection.delete_one({'_id': ObjectId(id)})
            #     if delete_row.delete_count != 1:
            #         print("Warning: Expected to delete 1 row, but deleted these many instead: ", delete_row.delete_count)
            #         print(delete_row.raw_result)
            # except:
            #     print("There was error #1 in your delete!")
            #     print(deleted_row.raw_result)
        else:
            print("Not ObjectId received!")
        return

    def post(self, team, year_period, month_period, topic):
        """Creates a new document"""
        collection = db.todos
        form_data = request.form.to_dict()
        # print("===========================")
        # print("post: ", form_data)
        # print("===========================")
        form_data['TEAM'] = team
        form_data['YEAR'] = year_period
        form_data['MONTH'] = month_period
        form_data['TOPIC'] = topic
        # print("===========================")
        # print("post: ", form_data)
        # print("===========================")
#        try:
        insert_row = collection.insert_one(form_data)
        if insert_row.inserted_id:
            print(insert_row.inserted_id)
            print("===================")
            print("From Todo Post Id:", insert_row.inserted_id)
            print("===================")
        else:
            print("There was error #1 in your insert!")
            print(insert_row.raw_result)
#        except:
#            print("There was error #2 in your insert!")
        print("I'm returning")
        return


api.add_resource(TodoItem, '/api/todos/<string:team>/<string:year_period>/<string:month_period>/<string:topic>')

#####################################

####### This section includes the API code for Days ###########

class DaysList(Resource):
    def get(self, team, year_period, month_period, topic):
        collection = db.days
        form_cursor = collection.find({'TEAM': team, 'YEAR': year_period, 'MONTH': month_period, 'TOPIC': topic})
        if form_cursor.count() > 0:
            form_data = list(form_cursor)
            print("GET form data: ", form_data)
            for item in form_data:
                for key, value in item.items():
                    if type(value)==date:
                        item[key]=value.strftime("%m/%d/%Y")
                    elif type(value)==ObjectId:
                        item[key]=str(value)
                    elif type(value)==time:
                        item[key]=value.strftime("%H:%M:%S")
                    elif type(value)==datetime:
                        item[key]=value.strftime("%m/%d/%Y")
            return form_data
        else:
            return []

api.add_resource(DaysList, '/api/days/<string:team>/<string:year_period>/<string:month_period>/<string:topic>')

class DaysItem(Resource):
    def put(self, team, year_period, month_period, topic, day, value):
        """This function perform an update on an existing record"""
        collection = db.days
        form_cursor = collection.find({'TEAM': team, 'YEAR': year_period, 'MONTH': month_period, 'TOPIC': topic, 'DAY': int(day)})
        print("Put form data cursor: ", form_cursor)
        form_data = collection.find_one({'TEAM': team, 'YEAR': year_period, 'MONTH': month_period, 'TOPIC': topic, 'DAY': int(day)})
        print("Put form data: ", form_data)
        # form_data = list(form_cursor)
        # print("Put form data list: ", form_data)
        # form_data = request.form.to_dict()
        # print("Put form data form: ", form_data)
        if '_id' in form_data:
        #if '_id' in form_cursor:
            id = form_data.pop('_id')
            print("Row will be updated: ", id)
            form_data['VALUE'] = value
            update_record = {'$set':form_data}
            updated_row = collection.update_one({'_id': ObjectId(id) }, update_record)
            if updated_row.matched_count == 1:
                print("Row updated succesfully!")
            else:
                print("There was error #1 in your update!")
                print(updated_row.raw_result)
        else:
            print("Not ObjectId received!")
        return

api.add_resource(DaysItem, '/api/days/<string:team>/<string:year_period>/<string:month_period>/<string:topic>/<string:day>/<string:value>')
#####################################

####### This section includes the API code for Manual ###########
class ManualList(Resource):
    def get(self, team, year_period, month_period, topic, table):
        collection = db.manual
        form_cursor = collection.find({'TEAM': team, 'YEAR': year_period, 'MONTH': month_period, 'TOPIC': topic, 'TABLE': table})
        if form_cursor.count() > 0:
            form_data = list(form_cursor)
            # print(form_data)
            for item in form_data:
                for key, value in item.items():
                    if type(value)==date:
                        item[key]=value.strftime("%m/%d/%Y")
                    elif type(value)==ObjectId:
                        item[key]=str(value)
                    elif type(value)==time:
                        item[key]=value.strftime("%H:%M:%S")
                    elif type(value)==datetime:
                        item[key]=value.strftime("%m/%d/%Y")
            return form_data
        else:
            return []

api.add_resource(ManualList, '/api/manual/<string:team>/<string:year_period>/<string:month_period>/<string:topic>/<string:table>')

class ManualItem(Resource):
    def put(self, team, year_period, month_period, topic, table):
        """This function perform an update on an existing record"""
        collection = db.manual
        form_data = request.form.to_dict()
        if '_id' in form_data:
            id = form_data.pop('_id')
            # print("===================")
            # print("From PUT Id:",id)
            # print("===================")
            print("Row will be updated: ", id)
#            try:
            update_record = {'$set':form_data}
            # print("update_record =", update_record)
            updated_row = collection.update_one({'_id': ObjectId(id) }, update_record)
            # print("update_row =", updated_row)
            if updated_row.matched_count == 1:
                print("Row updated succesfully!")
            else:
                print("There was error #1 in your update!")
                print(updated_row.raw_result)
#            except:
#                print("There was error #2 in your update!")
        else:
            print("Not ObjectId received!")
        return

    def delete(self, team, year_period, month_period, topic, table):
        """Delete document"""
        collection = db.manual
        form_data = request.form.to_dict()
        print("===========================")
        print("post-delete: ", form_data)
        print("===========================")
        if '_id' in form_data:
#            try:
            id = form_data.pop('_id')
            print("===================")
            print("From Delete Id:",id)
            print("===================")
            deleted_row = collection.delete_one({'_id': ObjectId(id)})
            if delete_row.delete_count != 1:
                print("Warning: Expected to delete 1 row, but deleted these many instead: ", delete_row.delete_count)
                print(delete_row.raw_result)
            #except:
            print("There was error #1 in your delete!")
            print(deleted_row.raw_result)
        else:
            print("Not ObjectId received!")
        return

    def post(self, team, year_period, month_period, topic, table):
        """Creates a new document"""
        collection = db.manual
        form_data = request.form.to_dict()
        # print("===========================")
        # print("post: ", form_data)
        # print("===========================")
        # list_data = list(form_data)
        form_data['TEAM'] = team
        form_data['YEAR'] = year_period
        form_data['MONTH'] = month_period
        form_data['TOPIC'] = topic
        form_data['TABLE'] = table
        # period = ('TEAM': team , 'YEAR': year_period, 'MONTH': month_period, 'TOPIC': topic, 'TABLE':table )
        # list_data.insert(0, period)
        # form_data.append('TEAM':team, 'YEAR': year_period, 'MONTH': month_period, 'TOPIC':topic, 'TABLE':table)
        # print("===========================")
        # print("Manual post: ", form_data)
        # print("===========================")
        # list_data = list(form_data)
        # print("===========================")
        # print("post: ", list_data)
        # print("===========================")
#        try:
        insert_row = collection.insert_one(form_data)
        if insert_row.inserted_id:
            # print(self.get(insert_row.inserted_id))
            print(insert_row.inserted_id)
            # print("===================")
            # print("From POST Id:", insert_row.inserted_id)
            # print("===================")
        else:
            print("There was error #1 in your insert!")
            print(insert_row.raw_result)
#        except:
#            print("There was error #2 in your insert!")
        return


api.add_resource(ManualItem, '/api/manual/<string:team>/<string:year_period>/<string:month_period>/<string:topic>/<string:table>')

#####################################

####### This section includes the API code for Weekly ###########
class WeekList(Resource):
    def get(self, team, year_period, month_period, week, hi_lo):
        collection = db.weeklysum
        form_cursor = collection.find({'TEAM': team, 'YEAR': year_period, 'MONTH': month_period, "WEEK": week, "HI_LO": hi_lo})
        if form_cursor.count() > 0:
            form_data = list(form_cursor)
            # print("===================")
            # print("From Weekly form_data get data:", form_data)
            # print("===================")
            for item in form_data:
                for key, value in item.items():
                    if type(value)==date:
                        item[key]=value.strftime("%m/%d/%Y")
                    elif type(value)==ObjectId:
                        item[key]=str(value)
                    elif type(value)==time:
                        item[key]=value.strftime("%H:%M:%S")
                    elif type(value)==datetime:
                        item[key]=value.strftime("%m/%d/%Y")
            return form_data
        else:
            return []

api.add_resource(WeekList, '/api/week/<string:team>/<string:year_period>/<string:month_period>/<string:week>/<string:hi_lo>')

class WeekItem(Resource):
    def put(self, team, year_period, month_period, week, hi_lo):
        """This function perform an update on an existing record"""
        collection = db.weeklysum
        form_data = request.form.to_dict()
        if '_id' in form_data:
            id = form_data.pop('_id')
            print("===================")
            print("From Weekly PUT Id:",id)
            print("===================")
            print("Row will be updated: ", id)
#            try:
            update_record = {'$set':form_data}
            # print("update_record =", update_record)
            updated_row = collection.update_one({'_id': ObjectId(id) }, update_record)
            # print("update_row =", updated_row)
            if updated_row.matched_count == 1:
                print("Row updated succesfully!")
            else:
                print("There was error #1 in your update!")
                print(updated_row.raw_result)
#            except:
#                print("There was error #2 in your update!")
        else:
            print("Not ObjectId received!")
        return

    def delete(self, team, year_period, month_period, week, hi_lo):
        """Delete document"""
        collection = db.weeklysum
        form_data = request.form.to_dict()
        print("===========================")
        print("Weekly delete: ", form_data)
        print("===========================")
        if '_id' in form_data:
    #            try:
            id = form_data.pop('_id')
            print("===================")
            print("From Weekly Delete Id:", id)
            print("===================")
            deleted_row = collection.delete_one({'_id': ObjectId(id)})
            # if delete_row.delete_count != 1:
            #     print("Warning: Expected to delete 1 row, but deleted these many instead: ", delete_row.delete_count)
            #     print(delete_row.raw_result)
            # #except:
            # print("There was error #1 in your delete!")
            # print(deleted_row.raw_result)
        else:
            print("Not ObjectId received!")
        return

    def post(self, team, year_period, month_period, week, hi_lo):
        """Creates a new document"""
        collection = db.weeklysum
        form_data = request.form.to_dict()
        print("===========================")
        print("post: ", form_data)
        print("===========================")
        # list_data = list(form_data)
        form_data['TEAM'] = team
        form_data['YEAR'] = year_period
        form_data['MONTH'] = month_period
        form_data['WEEK'] = week
        form_data['HI_LO'] = hi_lo
        print("===========================")
        print("post: ", form_data)
        print("===========================")
        insert_row = collection.insert_one(form_data)
        if insert_row.inserted_id:
            # print(self.get(insert_row.inserted_id))
            print(insert_row.inserted_id)
            print("===================")
            print("From Weekly POST Id:", insert_row.inserted_id)
            print("===================")
        else:
            print("There was error #1 in your insert!")
            print(insert_row.raw_result)
    #        except:
    #            print("There was error #2 in your insert!")
        return

api.add_resource(WeekItem, '/api/week/<string:team>/<string:year_period>/<string:month_period>/<string:week>/<string:hi_lo>')


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.template_filter('shortdate')
def filter_datetime2shortdate(mydate):
#    native = mydate.replace(tzinfo=None)
    format='%m-%d-%y'
    return mydate.strftime(format)


if __name__ == "__main__":
    app.secret_key = 'mysecret'
    #app.run()
    serve(app)
