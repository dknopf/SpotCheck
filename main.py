from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
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


@app.route('/', methods=['POST', 'GET'])
def index():
    print('got into index!')
    return render_template('index.html')
    #if request.method == 'POST':

    #    StartFunction(datastore_client)
    #    return redirect('/')
    #else:
    #    return render_template('index.html')

@app.route('/schedule')
def scheduled_processes():
    StartFunction(datastore_client)
    return 'Hopefully this never appears'



@app.route('/subscribe', methods=['POST', 'GET'])
def SubscribeToCourses():

    email = request.form['email']
    courses = request.form['courses']
    courses = re.findall('[^,]+', courses)
    print('courses is: ', courses)
    confirmed_courses = []
    for course in courses:
        course = course.strip()
        query = datastore_client.query(kind='course')
        query.key_filter((datastore_client.key('course', course)), '=')
        print('made it past query key filter in subscribe. Key is: ', (datastore_client.key('course', course)))
        results = list(query.fetch())
        if len(results) > 1:
            print('RETURNED MORE THAN ONE RESULT IN SUBSCRIBE QUERY')
        elif len(results) ==1:
            print('successfuly found one result')
            confirmed_courses.append(course)
            if email not in results[0]['emails']:
                results[0]['emails'].append(email)
            datastore_client.put(results[0])
        elif len(results) == 0:
            #PUT IN A 'DID YOU MEAN THIS' FILTER
            print('no result found')

        print('made it past fetching query. Len query is: ', len(results))
    user_query = datastore_client.query(kind='user')
    user_query.key_filter((datastore_client.key('user', email)), '=')
    user_results = list(user_query.fetch())
    print('len user results is', len(user_results))
    if len(user_results) == 0:
        user_entity = datastore.Entity(key=datastore_client.key('user', email))
        user_entity.update({
            'courses' : [course for course in confirmed_courses]
            })
        datastore_client.put(user_entity)
    elif len(user_results) == 1:

        print('confirmed courses is: ', confirmed_courses)
        user_results[0]['courses'] += confirmed_courses
        print(user_results[0])

        datastore_client.put(user_results[0])
    elif len(user_results) > 1:
        print('THERE ARE MORE THAN ONE USERS RETURNED FOR USER SEARCH')
    #msg = EmailMessage()
    #msg.set_content('Hello, World')
    #msg['Subject'] = "THIS IS  A TEST EMAIL"
    #msg['From'] = 'dknopf@wesleyan.edu'
    #msg['To'] = 'dknopf@wesleyan.edu'
    #s = smtplib.SMTP('smtp.gmail.com')
    #s.send_message(msg)
    #s.quit()
    ##os.system("curl https://intoli.com/install-google-chrome.sh | bash")
    if request.form['page'] == 'index':
        return redirect('/')
    elif request.form['page'] == 'courselist':
        if len(user_results) == 1:
            return render_template('courselist.html', courses=user_results[0]['courses'], user=email)
        else:
            return render_template('courselist.html', courses=user_entity['courses'], user=email)




@app.route('/show_subscribed_courses', methods = ['POST', 'GET'])
def ShowSubscribedCourses():
    user = request.form['email']
    query = datastore_client.query(kind='user')
    query.key_filter((datastore_client.key('user', user)), '=')
    results = list(query.fetch())
    if len(results) == 1:
        return render_template('courselist.html', courses=results[0]['courses'], user=user)
    else:
        return render_template('courselist.html', courses=['ARABIC', 'english'], user='dknopf@wesleyan.edu')


@app.route('/unsubscribe', methods=['POST'])
def Unsubscribe():
    if request.method == 'POST':
        user = request.form['user']
        course = request.form['course']
        user_entity = datastore_client.get(datastore_client.key('user', user))
        user_entity['courses'].remove(course)
        datastore_client.put(user_entity)
        course_entity = datastore_client.get(datastore_client.key('course', course))
        course_entity['emails'].remove(user)
        datastore_client.put(course_entity)
        return render_template('courselist.html', courses = user_entity['courses'], user=user)


if __name__ == '__main__':
    app.run(debug=True)