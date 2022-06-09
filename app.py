import datetime
import json
import os
import pickle
import random
import uuid

import nltk
import numpy as np
from flask import Flask, make_response, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from keras.models import load_model
from nltk.stem import WordNetLemmatizer

# nltk.download('popular')
lemmatizer = WordNetLemmatizer()

model = load_model('model.h5')
intents = json.loads(open('data.json').read())
words = pickle.load(open('texts.pkl', 'rb'))
classes = pickle.load(open('labels.pkl', 'rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return(np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res, ints


app = Flask(__name__)
app.static_folder = 'static'
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
# os.environ['URI']
app.config['SECRET_KEY'] = "1b308e20a6f3193e43c021bb1412808f"
# os.environ['SECRET']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class chat(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    message = db.Column(db.Text)
    user = db.Column(db.String(200), db.ForeignKey("user_db.id"))
    response = db.Column(db.Text)
    time_asked = db.Column(db.DateTime)

    def __repr__(self):
        return f'User ID: {self.user}\nmessage: {self.message}\nresponse: {self.response}'

    def __init__(self, id, message, user, asked_on, response):
        self.id = id
        self.message = message
        self.response = response
        self.user = user
        self.time_asked = asked_on


class user_db(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    admin = db.Column(db.Boolean)
    name = db.Column(db.String(200))
    email = db.Column(db.String(100))
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))

    def __repr__(self):
        return f'User Name: {self.username}\nEmail: {self.email}\
            \nAdmin: {bool(self.admin)}'

    def __init__(self, id, name, email, username, password, admin=False):
        self.username = username
        self.email = email
        self.name = name
        self.password = password
        self.id = id
        self.admin = admin


db.create_all()


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route("/api/send", methods=['POST'])
def get_bot_response():
    data = request.get_json()
    resposne, class_of_resp = chatbot_response(data['body'])
    print(f"\nUser: {data['body']}\n\
        Bot:{resposne}\nClass: {class_of_resp}\n")
    '''words = clean_up_sentence(data['body'])
    print(words)'''
    return make_response({
        'results': resposne,
        'class': class_of_resp
    })


if __name__ == "__main__":
    app.run(debug=True)
