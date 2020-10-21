from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mobility import Mobility
from datetime import datetime
from google.cloud import datastore
from WesmapsWebscraperBS import StartFunction
import os
from email.message import EmailMessage
import smtplib, ssl
import yagmail
import re

datastore_client = datastore.Client()


app = Flask(__name__)
Mobility(app)

#@app.route('/CreateME')
#def RetrieveMasterEntity():
#    query = datastore_client.query(kind='masterEntity')
#    print('made it past query')
#    results = list(query.fetch())
#    return ','.join(results[0]['courseList'])


#@app.route('/', methods=['POST', 'GET'])
#def index():
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
    GetCourseList()
    return render_template('index.html', course_list=course_list, status=status)
    #if request.method == 'POST':

    #    StartFunction(datastore_client)
    #    return redirect('/')
    #else:
    #    return render_template('index.html')

def GetCourseList():
    query = datastore_client.query(kind='masterEntity')
    results = list(query.fetch())
    global course_list
    course_list = results[0]['courseList']

@app.route('/schedule')
def scheduled_processes():
    StartFunction(datastore_client)
    return 'Hopefully this never appears'



@app.route('/subscribe', methods=['POST', 'GET'])
def SubscribeToCourses():

    email = request.form['email'].strip().lower()
    courses = request.form['courses'].strip()
    if not (email == '' or courses == ''):
        user_query = datastore_client.query(kind='user')
        user_query.key_filter((datastore_client.key('user', email)), '=')
        user_results = list(user_query.fetch())
        print('len user results is', len(user_results))
        if len(user_results) == 0:
            user_entity = datastore.Entity(key=datastore_client.key('user', email))
            user_entity.update({
                'courses' : []
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
            course=re.sub('  ', ', ', course)
            course = course.strip()

            if re.search('^[A-Z&]{3,4}$', course): #Department
                print('GOT INTO DEPARTMENT SECTION')
                courses_to_add = []
                for i in range(8):
                    query = datastore_client.query(kind='course')
                    query.add_filter('dept' + str(i), '=', course)
                    courses_to_add+=list(query.fetch())
                for course_to_add in courses_to_add:
                    if course_to_add.key.name not in user_entity['courses']:
                        user_entity['courses'].append(course_to_add.key.name)
                        courses_added[course_to_add.key.name] = ''
                    if email not in course_to_add['emails']:
                        course_to_add['emails'].append(email)
                        courses_added[course_to_add.key.name] = ''


                    #if email not in course_to_add['emails'] and course_to_add.key.name not in courses_added:
                    #    course_to_add['emails'].append(email)
                    #    courses_added[course_to_add.key.name] = '' #SHOULD PROBABLY TURN CONFIRMED COURSES INTO A DICT
                    #    confirmed_courses.append(course_to_add.key.name)
                    #else:
                    #    print('email: ', email, 'is in emails list of: ', course_to_add.key.name)
                    #    print('courses_added is: ', courses_added)
                #datastore_client.put_multi(courses_to_add)
                    datastore_client.put(course_to_add) #MAKE THIS INTO PUT MULTI

            else: #Individual course
                query = datastore_client.query(kind='course')
                query.key_filter((datastore_client.key('course', course)), '=')
                print('made it past query key filter in subscribe. Key is: ', (datastore_client.key('course', course)))
                results = list(query.fetch())
                if len(results) > 1:
                    print('RETURNED MORE THAN ONE RESULT IN SUBSCRIBE QUERY')
                elif len(results) ==1:
                    print('successfuly found one result')
                    if email not in results[0]['emails']:
                        results[0]['emails'].append(email)
                        courses_added[course] = ''
                        #confirmed_courses.append(course)
                    if course not in user_entity['courses']:
                        user_entity['courses'].append(course)
                        courses_added[course] = ''

                    datastore_client.put(results[0])
                elif len(results) == 0:
                    #PUT IN A 'DID YOU MEAN THIS' FILTER
                    print('no result found')

                print('made it past fetching query. Len query is: ', len(results))

        datastore_client.put(user_entity)
        



        #user_query = datastore_client.query(kind='user')
        #user_query.key_filter((datastore_client.key('user', email)), '=')
        #user_results = list(user_query.fetch())
        #print('len user results is', len(user_results))
        #if len(user_results) == 0:
        #    user_entity = datastore.Entity(key=datastore_client.key('user', email))
        #    user_entity.update({
        #        'courses' : [course for course in confirmed_courses]
        #        })
        #    datastore_client.put(user_entity)
        #elif len(user_results) == 1:

        #    print('confirmed courses is: ', confirmed_courses)
        #    user_results[0]['courses'] += confirmed_courses
        #    print(user_results[0])

        #    datastore_client.put(user_results[0])
        #elif len(user_results) > 1:
        #    print('THERE ARE MORE THAN ONE USERS RETURNED FOR USER SEARCH')
        #msg = EmailMessage()
        #msg.set_content('Hello, World')
        #msg['Subject'] = "THIS IS  A TEST EMAIL"
        #msg['From'] = 'dknopf@wesleyan.edu'
        #msg['To'] = 'dknopf@wesleyan.edu'
        #s = smtplib.SMTP('smtp.gmail.com')
        #s.send_message(msg)
        #s.quit()
        ##os.system("curl https://intoli.com/install-google-chrome.sh | bash")
        if len(courses_added) > 0:
            print('got into confirmed courses greater than 1')
            return redirect(url_for('index', status='success'))

            #if request.form['page'] == 'index':
        else:
            return redirect(url_for('index', status='failure'))

        # NOT NECESSARY BC YOU CAN NO LONGER SUBSCRIBE FROM COURSELIST PAGE
        #elif request.form['page'] == 'courselist':
        #    if len(user_results) == 1:
        #        return render_template('courselist.html', courses=user_results[0]['courses'], user=email)
        #    else:
        #        return render_template('courselist.html', courses=user_entity['courses'], user=email)
    else:
        if request.form['page'] == 'index':
            return redirect(url_for('index', status='noEntry'))
        #elif request.form['page'] == 'courselist':
        #    return render_template('courselist.html')



@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html', tryAgain = False)

@app.route('/show_subscribed_courses', methods = ['POST', 'GET'])
def ShowSubscribedCourses():
    user = request.form['email'].strip().lower()
    if user == '':
        return render_template('login.html', tryAgain=True) #Add feedback here
    query = datastore_client.query(kind='user')
    query.key_filter((datastore_client.key('user', user)), '=')
    results = list(query.fetch())
    if len(results) == 1:
        return render_template('courselist.html', courses=results[0]['courses'], user=user)
    else:
        return render_template('login.html', tryAgain = True)
        #return render_template('courselist.html', courses=['ARABIC', 'english'], user='dknopf@wesleyan.edu')


@app.route('/unsubscribe', methods=['POST', 'GET'])
def unsubscribe():
    user = request.args.get('user', None)
    course = request.args.get('course', None)
    user_entity = datastore_client.get(datastore_client.key('user', user))
    try:
        if user_entity['courses'].count(course) > 1:
            print('THERE IS MORE THAN ONE OCCURENCE BEFORE REMOVING OF COURSE: ', course, 'IN USER: ', user)
            print(user_entity['courses'])
        user_entity['courses'].remove(course)
        if (course in user_entity['courses']):
            print('COURSE: ', course, 'STILL IN USER_ENTITY COURSES')
        #print('got past user_entity removing course')
        datastore_client.put(user_entity)


        course_entity = datastore_client.get(datastore_client.key('course', course))
        #print('got past querying course entity')
        try:
            course_entity['emails'].remove(user)
            #print('got past removing email from course')
        except Exception as inst:
            print('Error: ', str(inst), 'when removing course: ', course, 'for user: ', user)
        datastore_client.put(course_entity)
        #datastore_client.put_multi([user_entity, course_entity])
        #print('got past updating client')
    except Exception as inst:
        print('got into exception: ', str(inst), 'for unsubscribing on course: ', course, "and user: ", user)
    return '', 204
    #return render_template('courselist.html', courses = user_entity['courses'], user=user)


@app.route('/test.js', methods=['GET'])
def GetTestJS():
    return render_template('testJS.html')

#@app.route('/unsubscribe', methods=['POST'])
#def Unsubscribe():
#    if request.method == 'POST':
#        user = request.form['user']
#        course = request.form['course']
#        user_entity = datastore_client.get(datastore_client.key('user', user))
#        user_entity['courses'].remove(course)
#        datastore_client.put(user_entity)
#        course_entity = datastore_client.get(datastore_client.key('course', course))
#        course_entity['emails'].remove(user)
#        datastore_client.put(course_entity)
#        return render_template('courselist.html', courses = user_entity['courses'], user=user)


if __name__ == '__main__':
    app.run(debug=True)