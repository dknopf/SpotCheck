from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility
from datetime import datetime
from google.cloud import datastore
from WesmapsWebscraperBS import StartFunction
import os
from email.message import EmailMessage
import smtplib
import ssl
import yagmail
import re
from twilio.rest import Client as Twilio_Client

from Refresh import Refresh
import config as cf

datastore_client = datastore.Client()
twilio_client = Twilio_Client(
    os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_ACCOUNT_SECRET"))

app = Flask(__name__)
Mobility(app)

# @app.route('/CreateME')
# def RetrieveMasterEntity():
#    query = datastore_client.query(kind='masterEntity')
#    print('made it past query')
#    results = list(query.fetch())
#    return ','.join(results[0]['courseList'])


# @app.route('/', methods=['POST', 'GET'])
# def index():
#    return render_template('testAutocomplete.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    print('got into top of autocmpletes')
    search = request.args.get('q')
    course_query = datastore_client.query(kind='course')
    course_query.key_filter((datastore_client.key('course', search)), '=')
    course_results = list(course_query.fetch())
    print(len(course_results))
    print('got here')
    return jsonify(matching_results=course_results)


@app.route('/', methods=['POST', 'GET'])
def index():
    status = request.args.get('status', None)
    print('got into index!')
    return render_template('index.html', status=status)
    # if request.method == 'POST':

    #    StartFunction(datastore_client)
    #    return redirect('/')
    # else:
    #    return render_template('index.html')


def GetCourseList():
    UpdateDate()
    query = datastore_client.query(kind='masterEntity')
    results = list(query.fetch())
    global course_list
    course_list = results[0][cf.dateObj.courseList]


@app.route('/schedule')
def scheduled_processes():
    StartFunction(datastore_client)
    return 'Hopefully this never returns'


@app.route('/subscribe', methods=['POST', 'GET'])
def SubscribeToCourses():
    user = CleanUser(request.form['email'].strip().lower())
    if not ValidateUser(user):
        return redirect(url_for('index', status='badUsername'))
    courses = request.form['courses'].strip()
    if not (user == '' or courses == ''):
        user_query = datastore_client.query(kind='user')
        user_query.key_filter((datastore_client.key('user', user)), '=')
        user_results = list(user_query.fetch())
        print('len user results is', len(user_results))
        if len(user_results) == 0:
            user_entity = datastore.Entity(
                key=datastore_client.key('user', user))
            user_entity.update({
                'courses': [],
                'username': user
            })
            datastore_client.put(user_entity)
        elif len(user_results) == 1:
            user_entity = user_results[0]
        print('courses string before findall is is:', courses)
        courses = re.findall('[^,]+', courses)
        print('courses is: ', courses)
        confirmed_courses = []
        courses_added = {}

        for course in courses:
            course = re.sub('  ', ', ', course)
            course = course.strip()

            if re.search('^[A-Z&]{3,4}$', course):  # Department
                print('GOT INTO DEPARTMENT SECTION')
                courses_to_add = []
                for i in range(8):
                    query = datastore_client.query(kind='course')
                    query.add_filter('dept' + str(i), '=', course)
                    courses_to_add += list(query.fetch())
                for course_to_add in courses_to_add:
                    if course_to_add.key.name not in user_entity['courses']:
                        user_entity['courses'].append(course_to_add.key.name)
                        courses_added[course_to_add.key.name] = ''
                    if user not in course_to_add['emails']:
                        course_to_add['emails'].append(user)
                        courses_added[course_to_add.key.name] = ''

                    # if email not in course_to_add['emails'] and course_to_add.key.name not in courses_added:
                    #    course_to_add['emails'].append(email)
                    #    courses_added[course_to_add.key.name] = '' #SHOULD PROBABLY TURN CONFIRMED COURSES INTO A DICT
                    #    confirmed_courses.append(course_to_add.key.name)
                    # else:
                    #    print('email: ', email, 'is in emails list of: ', course_to_add.key.name)
                    #    print('courses_added is: ', courses_added)
                # datastore_client.put_multi(courses_to_add)
                    # MAKE THIS INTO PUT MULTI
                    datastore_client.put(course_to_add)

            else:  # Individual course
                query = datastore_client.query(kind='course')
                query.key_filter((datastore_client.key('course', course)), '=')
                print('made it past query key filter in subscribe. Key is: ',
                      (datastore_client.key('course', course)))
                results = list(query.fetch())
                if len(results) > 1:
                    print('RETURNED MORE THAN ONE RESULT IN SUBSCRIBE QUERY')
                elif len(results) == 1:
                    print('successfuly found one result')
                    if user not in results[0]['emails']:
                        results[0]['emails'].append(user)
                        courses_added[course] = ''
                        # confirmed_courses.append(course)
                    if course not in user_entity['courses']:
                        user_entity['courses'].append(course)
                        courses_added[course] = ''

                    datastore_client.put(results[0])
                elif len(results) == 0:
                    # PUT IN A 'DID YOU MEAN THIS' FILTER
                    print('no result found')

                print('made it past fetching query. Len query is: ', len(results))

        datastore_client.put(user_entity)
        if len(courses_added) > 0:
            print('got into confirmed courses greater than 1')
            return redirect(url_for('index', status='success'))
        else:
            return redirect(url_for('index', status='failure'))
    else:
        if request.form['page'] == 'index':
            return redirect(url_for('index', status='noEntry'))


def CleanUser(user):
    if not re.search('@', user):
        if user[:2] == "+1":
            user = user[2:]
        user = re.sub("[\(\)\-\+\s]", "", user)

    print("user:", user)
    return user


def ValidateUser(user):
    if not re.search('@', user):
        if not re.search("^\d{10}$", user):
            return False
        try:
            phone_number = twilio_client.lookups \
                .phone_numbers(user) \
                .fetch(country_code='US')
        except:
            return False
    return True


@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html', tryAgain=False)


@app.route('/show_subscribed_courses', methods=['POST', 'GET'])
def ShowSubscribedCourses():
    user = CleanUser(request.form['email'].strip().lower())
    if user == '':
        # Add feedback here
        return render_template('login.html', tryAgain=True)
    query = datastore_client.query(kind='user')
    query.key_filter((datastore_client.key('user', user)), '=')
    results = list(query.fetch())
    if len(results) == 1:
        return render_template('courselist.html', courses=results[0]['courses'], user=user)
    else:
        return render_template('login.html', tryAgain=True)
        # return render_template('courselist.html', courses=['ARABIC', 'english'], user='dknopf@wesleyan.edu')


@app.route('/unsubscribe', methods=['POST', 'GET'])
def unsubscribe():
    user = request.args.get('user', None)
    course = request.args.get('course', None)
    user_entity = datastore_client.get(datastore_client.key('user', user))
    try:
        if user_entity['courses'].count(course) > 1:
            print('THERE IS MORE THAN ONE OCCURENCE BEFORE REMOVING OF COURSE: ',
                  course, 'IN USER: ', user)
            print(user_entity['courses'])
        user_entity['courses'].remove(course)
        if (course in user_entity['courses']):
            print('COURSE: ', course, 'STILL IN USER_ENTITY COURSES')
        #print('got past user_entity removing course')
        datastore_client.put(user_entity)

        course_entity = datastore_client.get(
            datastore_client.key('course', course))
        #print('got past querying course entity')
        try:
            course_entity['emails'].remove(user)
            #print('got past removing email from course')
        except Exception as inst:
            print('Error: ', str(inst), 'when removing course: ',
                  course, 'for user: ', user)
        datastore_client.put(course_entity)
        #datastore_client.put_multi([user_entity, course_entity])
        #print('got past updating client')
    except Exception as inst:
        print('got into exception: ', str(inst),
              'for unsubscribing on course: ', course, "and user: ", user)
    return '', 204
    # return render_template('courselist.html', courses = user_entity['courses'], user=user)


@app.route('/update_semester', methods=['GET'])
def UpdateSemester():
    UpdateDate()
    Refresh(datastore_client)
    return '', 204


@app.route('/get_courses', methods=['GET'])
def GetCourses():
    GetCourseList()
    return({"courses": course_list})


def UpdateDate():
    cf.dateObj.GetCurrDate()


if __name__ == '__main__':
    app.run(debug=True)
