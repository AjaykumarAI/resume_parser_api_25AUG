from flask import Flask, render_template, request, redirect, flash, jsonify
from werkzeug.utils import secure_filename
from flask import *
from werkzeug.utils import secure_filename
import shutil
import pickle
import spacy
import textract
import os
import re
import json
import wikipedia
import pandas as pd
import dns.resolver
from spacy.gold import GoldParse
from spacy.scorer import Scorer
import logging
import logging.handlers
from datetime import datetime
from mail_sending import mail_class
from validation import validation_class
from zip_validation import zip_class


app = Flask(__name__)
handler = logging.handlers.RotatingFileHandler('log.txt',maxBytes = 1024 * 1024)
logging.getLogger('werkzeug').setLevel(logging.DEBUG)
logging.getLogger('werkzeug').addHandler(handler)
app.logger.setLevel(logging.WARNING)
app.logger.addHandler(handler)
app.config['PROPAGATE_EXCEPTIONS'] = True

nlp = spacy.load("en_core_web_sm")

app.secret_key = 'random string'
email = None

@app.route('/login/<name>')
@app.route('/login')
def login(name = None):
    session.pop("email", None)
    return render_template('login.html')

@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    global email
    error = None
    if request.method == 'POST':
        email = request.form['mail']    ### getting the email from the user
        session["email"] = email
        error = 'Invalid email address. Please try again!'
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)  ### checking the email is valid or not
        #### Log-file ######
        with open('log.txt','a') as f:
            f.write(email + '\n')
        ###################
        if match == None:
            return redirect(url_for('login',name = error))
        else:
            return render_template('upload.html')
    return redirect(url_for('login'))


@app.route('/results', methods = ['GET','POST'])
def results():
    if "email" in session:
        email = session["email"]

        if request.method == 'POST':
            f = request.files['file']
            filename, file_extension = os.path.splitext(f.filename)
            PATH = os.path.abspath(os.path.dirname(__file__))
            f.save(os.path.join(PATH, secure_filename(f.filename)))
            file_path=os.path.join(PATH,secure_filename(f.filename))
        
            d = os.getcwd()
            path = os.path.join(d, "3k_spacy_updated_model/")

            nlp2 = spacy.load(path)
            baz = file_path           ### Getting the uploaded file from the user
            head, tail = os.path.split(baz)    ##### Head is for file path and Tail is for file name
            ext0 = os.path.splitext(tail)[0] 
            ext = os.path.splitext(tail)[1]     #### file extension from the user file

            
            if not os.path.exists('Working'):
                os.makedirs('Working')
            if not os.path.exists('Not_working'):
                os.makedirs('Not_working')
            if not os.path.exists('Invalid_files'):
                os.makedirs('Invalid_files')
            
            def file_existed(baz):
                bazz = baz
                head, tail = os.path.split(bazz)
                ext0 = os.path.splitext(tail)[0]
                ext = os.path.splitext(tail)[1]
                rand = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ready = ext0 + '(' + rand + ')' + ext
                baz = head + "/" + ready
                os.rename(bazz, baz)
                return baz

            ##### calling zip_validation file ######
            if ext.endswith('.zip') or ext.endswith('.rar'):
                zipper = zip_class()
                zipper.zip_method(ext, baz, email)
            ########################################
            else:
                error = 'Please Upload a valid file'
                file_ext = ['.doc', '.docx', '.jpeg', '.jpg', '.png', '.pdf', '.txt', '.rtf','.Doc','.Docx','.Pdf', '.JPEG', '.JPG', '.PNG', '.TXT', '.Txt']
                if ext in file_ext:
                    examples = textract.process(baz, encoding = "utf-8")
                    examples = examples.decode()
                    doc = nlp2(examples)
                    entities = dict([(str(x.label_), x.text) for x in doc.ents])
                    entities = json.dumps(entities)
                    error = str(entities)
                    baz = file_existed(baz)
                    head, tail = os.path.split(baz)
                    base = os.path.splitext(tail)[0]   #### filename without file extension
                    completeName = os.path.join(base+".json")     #### merging the filename with .json format
                    ###### Json #########
                    with open(completeName, 'w') as f:
                        com =  json.dump(entities, f)
                    #####################
                    results_json_path = os.path.abspath(completeName)
                    results_json_path = str(results_json_path)
                    completeName_val = os.path.join(base+"_validations.txt")    ##### merging the filename with _validation.txt format
                    #### validation calling ####
                    first = validation_class()
                    retu = first.validation_method(entities, completeName_val, baz, completeName)
                    print("Validation is done.")
                    #########################
                    #### Email-sending #######
                    print("Mail is started sending.")
                    first = mail_class()
                    if retu >= 4:
                        json_file = (os.getcwd() + "/" + "Working" + "/" + completeName)
                        first.mail_method(email, json_file, 'Json_file')
                        first.mail_method('resumevalidation@screativesoft.com', json_file, 'Json_file')
                        print("Mail has sent successfully!")
                        print("Working File")
                    else:
                        first.mail2_method(email, "Your Resume was different our back end team is working on it, Thank you.")
                        print("Mail has sent successfully!")
                        print("Not_Working File")
                    ###########################
                    #entities_list = ["FirstName", "LastName", "Address", "City", "State", "Country", "email-id", "mobile-number", "land-line-number", "Objective", "Summary", "Bachelors", "Bachelors-university-name", "Bachelors-degree-college-name", "Bachelors-city", "Bachelors-state", "Bachelors-country", "Bachelors-percentage", "Bachelors-Start-date", "Bachelors-end-date", "Masters", "Masters-university-name", "Masters-college-name", "Masters-city", "Masters-state", "Masters-country", "Masters-percentageMasters-start-date", "Masters-end-date", "other-certifications", "Total-years-of-experience", "Skills-summary", "project1-client", "project1-tittle", "project1-city", "project1-state", "project1-start-date", "project1-end-date", "project1-responsibilities", "project1-environment", "project2-client", "project2-tittle", "project2-city", "project2-state", "project2-start-date", "project2-end-date", "project2-responsibilities", "project2- environment", "project3-client", "project3-tittle", "project3-city", "project3-state", "project3-start-date", "project3-end-date", "project3-responsibilities", "project3- environment", "project4-client", "project4-tittle", "project4-city", "project4-state", "project4-start-date", "project4-end-date","project4-responsibilities", "project4- environment", "project5-client", "project5-tittle", "project5-city", "project5-state", "project5-start-date", "project5-end-date","project5-responsibilities", "project5- environment", "project6-client", "project6-tittle", "project6-city", "project6-state", "project6-start-date", "project6-end-date", "project6-responsibilities", "project6- environment", "Other-projects",]
                    return render_template('upload.html', error = error)
                error = "please upload a valid a file"
                baz = file_existed(baz)
                shutil.move(baz, os.path.join(os.getcwd(), 'Invalid_files'))
                return render_template('upload.html', error = error)
            error = 'Done Sucessfully.'
            return render_template('upload.html', error = error)
    return redirect(url_for("login"))
if __name__ == '__main__':
    app.run("0.0.0.0",port = 5000,debug = True)
