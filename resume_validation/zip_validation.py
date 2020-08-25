from werkzeug.utils import secure_filename
import shutil
import pickle
import spacy
import textract
import os
import re
import random
import zipfile
import rarfile
import json
import wikipedia
import pandas as pd 
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from mail_sending import mail_class
from datetime import datetime
nlp = spacy.load("en_core_web_sm")
class zip_class():
    def zip_method(self, ext, baz, email):
        d=os.getcwd()
        global rang
        path = os.path.join(d, "3k_spacy_updated_model/")
        nlp2 = spacy.load(path)
        print("model loaded")
        if ext.endswith('.rar'):
            print("file is zip file")
            print('Extracting ZIP.')
            archive = rarfile.RarFile(baz, 'r')
            archive.extractall('.')
            print('ZIP Extracted.')
            archive.close()
        else:
            archive = zipfile.ZipFile(baz, 'r')
            archive.extractall('.')
            print('ZIP Extracted.')
            archive.close()
        PATH=os.path.abspath(os.path.dirname(__file__))
        print(PATH)
        head, tail = os.path.split(baz)
        file_path=os.path.join(PATH,secure_filename(tail))
        print(file_path)
        base_ = os.path.splitext(file_path)[0]
        print("head: ", head)
        print("base_: ", base_)
        head, tail = os.path.split(base_)
        print(tail)
        rang = 0
        print('//////////////////')
        base_ = base_+"/"
        nlp2 = spacy.load(path)
        if not os.path.exists('zip_Working'):
            os.makedirs('zip_Working')
        if not os.path.exists('zip_Notworking'):
            os.makedirs('zip_Notworking')
        ####### function for file_existed or not ########
        def file_existed(baz):
            bazz = baz
            head, tail = os.path.split(baz)
            ext0 = os.path.splitext(tail)[0]
            ext = os.path.splitext(tail)[1]
            rand = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ready = ext0 + '(' + rand + ')' + ext
            baz = head + "/" + ready
            head, tail = os.path.split(baz)
            base = os.path.splitext(tail)[0]
            os.rename(bazz, baz)
            return baz, base
        ################################################
        files = os.listdir(base_)
        for i in range(len(files)):
            try:
                files_moving = []
                req = os.path.splitext(files[i])[0]
                path_ = os.path.join(base_, files[i])
                examples = textract.process(path_,encoding = "utf-8")
                examples = examples.decode()
                doc = nlp2(examples)
                entities = dict([(str(x.label_), x.text) for x in doc.ents])
                head, tail = os.path.split(files[i])
                base = os.path.splitext(tail)[0]
                ###### function calling for renaming a file####
                file_exist1 = os.getcwd() + "/" + 'zip_Working' + "/" + tail
                file_exist2 = os.getcwd() + "/" + 'zip_Notworking' + "/" + tail
                if os.path.isfile(file_exist1) or os.path.isfile(file_exist2):
                    path_, base = file_existed(path_)
                #############################################
                completeName_val = (base + "_validations.txt")
                baz = path_
                print('baz',baz)
                count = 0
                head, tail = os.path.split(completeName_val)
                base = os.path.splitext(tail)[0]
                json_file = (base + ".json")
                with open(json_file, "w") as myfile:
                    json.dump(entities, myfile)
                if rang < 3:
                    first = mail_class()
                    first.mail_method(email, json_file, 'Json_file')
                    rang = rang + 1
                unpredicted_entities = ["FirstName", "LastName", "email-id", "mobile-number"]
                for i in unpredicted_entities:
                    with open(completeName_val, "a+") as myfile:
                        if i in entities:
                            count = count + 1
                            myfile.write("predicted %s is available"%i+"\n")
                        else:
                            myfile.write("predicted %s is not available"%i+"\n")
                files_moving.append(baz)
                files_moving.append(completeName_val)
                files_moving.append(json_file)
                if count >= 4:
                    destination = (os.getcwd() + "/" + 'zip_Working')
                    for i in files_moving:
                        shutil.move(i, destination)
                else:
                    with open(completeName_val, "a+") as myfile:
                        myfile.write("The predcicted Values are: %d"%count+"\n")
                    destination = (os.getcwd() + "/" + 'zip_Notworking')
                    for i in files_moving:
                        shutil.move(i,destination)
            except:
                pass
        shutil.rmtree(base_)