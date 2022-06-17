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
import plotly.graph_objects as go
from flask import Flask, make_response, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
from plotly.subplots import make_subplots
from werkzeug.security import check_password_hash, generate_password_hash

try:
    if os.environ['deployment']:
        if nltk.data.find('corpora/omw-1.4'):
            print('Data is moslty downloaded')
        nltk.download('punkt')
except (KeyError, LookupError):
    print('NLTK data corpus has problems in initilizing')

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
try:
    if os.environ['deployment']:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['URI']
        app.config['SECRET_KEY'] = os.environ['SECRET']
except KeyError:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hyoryknfluddky:722bb2161259ab8ac73dada6e70875f8258909296dd481e62d2655ffa5326a81@ec2-52-44-13-158.compute-1.amazonaws.com:5432/d10rp0bt5d4qbc'
    app.config['SECRET_KEY'] = "1b308e20a6f3193e43c021bb1412808f"
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
            \nID: {self.id}'

    def __init__(self, id, name, email, username, password, admin=False):
        self.username = username
        self.email = email
        self.name = name
        self.password = password
        self.id = id
        self.admin = admin


class attendance_sheet(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    date = db.Column(db.DateTime)
    status = db.Column(db.String(20))
    hours = db.Column(db.Float)
    reason = db.Column(db.Text)
    user = db.Column(db.String(200))

    def __repr__(self):
        return f'User Name: {self.user}\nStatus: {self.status}\
            \nDate: {self.date}'

    def __init__(self, id, date, status, hours, reason, user):
        self.id = id
        self.date = date
        self.status = status
        self.hours = hours
        self.reason = reason
        self.user = user


db.create_all()

# making the default anon user
try:
    anon = user_db.query.filter(user_db.name == 'anonymous').first().id
    print(f'Anon id is: {anon}')
except AttributeError:
    anon = str(uuid.uuid4())
    print(f'Anon id is: {anon}')
    anon_usr = user_db(id=anon, name='anonymous', username='anonymous', password=anon,
                       email='anonymous@anonymous.anon', admin=False)
    db.session.add(anon_usr)
    db.session.commit()


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
    # response, class_of_resp = chatbot_response(data['body'])
    if data['action'] == 'register' and data['password'] and data['email'] and data['name']:
        hashed_password = generate_password_hash(
            data['password'], method='sha256')
        email = user_db.query.filter_by(email=data['email']).first()
        if email:
            return make_response({

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

                    'email': data['email'],
                    'status': 'successfully registered'
                })
            except Exception as e:
                return make_response({

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
    if not data or not data['email'] or not data['password']:
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


@app.route("/api/OODL", methods=['POST'])
def OODForm_processor():
    data = request.get_json()
    print(data)
    if not data or not data['reason'] or not data['start'] or\
            not data['end'] or not data['token'] or not data['cause'] or not data['hours']:
        return make_response('could not process request', 401, {'status': 'more info required"'})
    else:
        token = jwt.decode(data['token'], app.config['SECRET_KEY'], "HS256")
        start_time_obj = datetime.datetime.strptime(data['start'], '%Y-%m-%d')
        end_time_obj = datetime.datetime.strptime(data['end'], '%Y-%m-%d')
        while start_time_obj <= end_time_obj:
            print(start_time_obj)
            cmd = attendance_sheet(id=str(uuid.uuid4()), date=start_time_obj,
                                   status=data['reason'], hours=data['hours'], reason=data['cause'], user=token['id'])
            db.session.add(cmd)
            start_time_obj += datetime.timedelta(days=1)
        db.session.commit()
        return make_response({
            'status': 'Successfully applied for '+data['reason'],
        })


@app.route("/api/timedelta", methods=['POST'])
def timedelta():
    data = request.get_json()
    print(data)
    if not data or not data['delta']:
        return make_response('could not process request', 401, {'status': 'more info required'})
    else:
        called_on = datetime.datetime.now()
        if data['delta'] == '0':
            delta = datetime.timedelta(hours=0)
        else:
            try:
                pattern = "'([0-9.-]*)'"
                result = re.search(
                    pattern, data['delta'].replace('"', "'").strip())
                delta = datetime.timedelta(hours=float(result.group(1)))
            except AttributeError:
                return make_response('could not process request', 401, {'status': 'could not parse input'})
        return make_response({
            'status': 'success',
            'results': str((called_on+delta).strftime("%m/%d/%Y, %H:%M:%S"))
        })


@app.route("/api/graph", methods=['POST'])
def attendance_graph():
    data = request.get_json()
    print(data)
    if not data or not data['token']:
        return make_response('could not process request', 401, {'status': 'more info required'})
    else:
        token = jwt.decode(data['token'], app.config['SECRET_KEY'], "HS256")
        user = token['id']
        now = datetime.datetime.now()
        monday = now - datetime.timedelta(days=(now.weekday()+1))
        friday = monday + datetime.timedelta(days=5)
        attendance = attendance_sheet.query.filter(attendance_sheet.user == user).filter(attendance_sheet.date >= monday)\
            .filter(attendance_sheet.date <= friday).order_by(attendance_sheet.date).all()
        output = []
        attendance_data = {
            'work': 0, 'leave': 0, 'overtime': 0, 'ood': 0
        }
        effort_data = {
            'effort': 0, 'extra_effort': 0
        }
        for day in attendance:
            output.append((day.date, day.status, day.hours, '<br>'))
            if day.status == 'attendance' or day.status == 'OOD':
                effort_data['effort'] += day.hours
                attendance_data['work'] += 1
            elif day.status == 'leave':
                attendance_data['leave'] += 1
            elif day.status == 'overtime':
                effort_data['extra_effort'] += day.hours
                attendance_data['overtime'] += 1
        plot_dict = {'Type': list(attendance_data.keys()),
                     'Days': list(attendance_data.values())}
        fig = make_subplots(rows=2, cols=1, specs=[
                            [{"type": "bar"}], [{"type": "pie"}]])
        fig.append_trace(go.Bar(y=list(plot_dict.values())[1], x=list(plot_dict.values())[0], name='days', marker=dict(
            color='LightSkyBlue')),
            row=1, col=1)
        total = 42.5
        values = []
        for val in effort_data.values():
            values.append(val)
            total -= val
        if total < 0:
            values.append(0)
        else:
            values.append(total)
        # print(values)
        labels = list(effort_data.keys())
        labels.append('unutilized time')
        # print(labels)
        fig.append_trace(go.Pie(values=values, labels=labels),
                         row=2, col=1)
        fig.update_layout(width=900, title_text="Performance plots")
        fig.show()
        '''payload = f"static/temp/{str(uuid.uuid4()).split('-')[-1]}.html"
        fig.write_html(payload)'''
        return make_response({
            'status': 'success',
            'payload': 'See the new tab for the graphs'
        })


@app.route("/api/chat", methods=['POST'])
def get_bot_response():
    called_on = datetime.datetime.now()
    data = request.get_json()
    response, class_of_resp = chatbot_response(data['body'])
    sanitized = data['body'].replace('"', "'").strip()
    try:
        token = jwt.decode(data['token'], app.config['SECRET_KEY'], "HS256")
        usr = token['id']
        expiry = token['exp']
        if round(datetime.datetime.now().timestamp()) > expiry:
            response = 'please re login'
    except jwt.exceptions.DecodeError as e:
        usr = anon
        print(e)
    print(f"\nUser ID: {usr}\nMessage: {data['body']}")
    print(f"Bot:{response}\nClass: {class_of_resp}\n")
    if class_of_resp[0]['intent'] == "give_leave_many_reason" or class_of_resp[0]['intent'] == "give_OOD_many_reason":
        if class_of_resp[0]['intent'] == "give_leave_many_reason":
            stat = "leave"
        if class_of_resp[0]['intent'] == "give_OOD_many_reason":
            stat = "OOD"
        try:
            reason_pattern = r'''[ ']([0-9]*)['" ][a-zA-Z ]*[ ']([a-zA-Z ]*)['.]$'''
            result = re.search(reason_pattern, sanitized)
            days, reason = int(result.group(1)), result.group(2)
            print(days, reason)
            for i in range(days):
                cmd = attendance_sheet(id=str(uuid.uuid4()), date=(called_on+datetime.timedelta(days=i)),
                                       status=stat, hours=24, reason=reason, user=usr)
                print(cmd)
                db.session.add(cmd)
        except AttributeError as e:
            response = "Input improperly formatted or incomplete. The '' are necessary."
    if class_of_resp[0]['intent'] == "give_attendance_today":
        try:
            reason_pattern = r"'([0-9.]*)'"
            result = re.search(reason_pattern, sanitized)
            hours = float(result.group(1))
            print(hours)
            cmd = attendance_sheet(id=str(uuid.uuid4()), date=called_on,
                                   status='attendance', hours=hours, reason='no reason', user=usr)
            print(cmd)
            db.session.add(cmd)
        except AttributeError as e:
            response = "Input improperly formatted or incomplete. The '' are necessary."
    conv = conversation(id=str(uuid.uuid4()), message=data['body'], response=response,
                        user=usr, time=called_on, probability=json.dumps(class_of_resp))
    db.session.add(conv)
    db.session.commit()
    return make_response({
        'results': response,
        'class': class_of_resp,
    })


if __name__ == "__main__":
    app.run(debug=True)
