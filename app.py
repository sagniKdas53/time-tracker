import datetime
import json
import os
import pickle
import random
import re
import uuid

import jwt
import nltk
import numpy as np
from flask import Flask, make_response, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
from werkzeug.security import check_password_hash, generate_password_hash

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


class conversation(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    message = db.Column(db.Text)
    user = db.Column(db.String(200), db.ForeignKey("user_db.id"))
    response = db.Column(db.Text)
    probabilities = db.Column(db.Text)
    time = db.Column(db.DateTime)

    def __repr__(self):
        return f'User ID: {self.user}\nmessage: {self.message}\nresponse: {self.response}'

    def __init__(self, id, message, user, time, response, probability):
        self.id = id
        self.message = message
        self.response = response
        self.user = user
        self.time = time
        self.probabilities = probability


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


@app.route("/api/register", methods=['POST'])
def bot_register():
    data = request.get_json()
    print(data)
    # resposne, class_of_resp = chatbot_response(data['body'])
    if data['action'] == 'register' and data['password'] and data['email'] and data['name']:
        hashed_password = generate_password_hash(
            data['password'], method='sha256')
        email = user_db.query.filter_by(email=data['email']).first()
        if email:
            return make_response({
                'name': data['name'],
                'email': data['email'],
                'status': "the email has been already registered"
            })
        else:
            try:
                new_user = user_db(id=str(uuid.uuid4()), name=data['name'], email=data['email'],
                                   password=hashed_password, admin=False, username=data['name'])
                db.session.add(new_user)
                db.session.commit()
                return make_response({
                    'name': data['name'],
                    'email': data['email'],
                    'status': 'done'
                })
            except Exception as e:
                return make_response({
                    'name': data['name'],
                    'email': data['email'],
                    'status': e
                })
    else:
        return make_response({
            'status': 'fail'
        })


@app.route("/api/login", methods=['POST'])
def bot_login():
    data = request.get_json()
    if not data or not data['email'] or not data['password'] or data['action'] != 'login':
        return make_response('could not verify', 401, {'status': 'login info required"'})
    else:
        user_ent = user_db.query.filter_by(email=data['email']).first()
        # print(f'user_ent.id={user_ent.id}')
        if check_password_hash(user_ent.password, data['password']):
            token = jwt.encode({'id': str(user_ent.id), 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(days=7)}, app.config['SECRET_KEY'], "HS256")
            print(token)
            return make_response({'email': str(user_ent.email), 'token': token, 'status': 'done'})
        else:
            return make_response({'email': str(user_ent.email), 'status': "Incorrect password"})


@app.route("/api/chat", methods=['POST'])
def get_bot_response():
    data = request.get_json()
    resposne, class_of_resp = chatbot_response(data['body'])
    print(f"\nUser: {data['body']}")
    print(f"Bot:{resposne}\nClass: {class_of_resp}\n")
    try:
        token = jwt.decode(data['token'], app.config['SECRET_KEY'], "HS256")
        usr = token['id']
        expiry = token['exp']
        if round(datetime.datetime.now().timestamp()) > expiry:
            resposne = 'please re login'
    except jwt.exceptions.DecodeError as e:
        usr = 'anonymous'
        print(e)
    if class_of_resp[0]['intent'] == "give_leave_many_reason" or class_of_resp[0]['intent'] == "give_OOD_many_reason":
        reason_pattern = r'''['"]([0-9]*)["'] days [a-zA-Z ]* ['"]([a-zA-Z ]*)["']$'''
        result = re.search(reason_pattern, data['body'])
        print(result.group(1), result.group(2))
    conv = conversation(id=str(uuid.uuid4()), message=data['body'], response=resposne,
                        user=usr, time=datetime.datetime.now(), probability=json.dumps(class_of_resp))
    db.session.add(conv)
    db.session.commit()
    return make_response({
        'results': resposne,
        'class': class_of_resp,
    })


if __name__ == "__main__":
    app.run(debug=True)
