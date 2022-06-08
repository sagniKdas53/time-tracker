"""
GROUP - 10
Project - Internship Forum
Mentor - Sunil Kumar Aralimara Channappa 
Team members:
Siva A - Team leader                         
Prabu K      
Joshva A                                             
Sree Bhavana Kasturi
Sagnik Das
Shiva Ganesh M
Tirupathi Reddy Devagiri
Neetha Jyothi Simhadri
Ashwin Mahendra Gawande
Shruti Govindalwar

"""

import datetime
import os
import uuid
from functools import wraps

import jwt
from flask import Flask, make_response, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

popularity_lim = 1
# change this to change filtering on popularity
# the flask app is initialized here as the configurations are set
app = Flask(__name__, static_folder='build')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['URI']
app.config['SECRET_KEY'] = os.environ['SECRET']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# the database table are represented as classes here


class user_db(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    admin = db.Column(db.Boolean)
    name = db.Column(db.String(200))
    email = db.Column(db.String(100))
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    credit = db.Column(db.Integer)

    def __repr__(self):
        return f'User Name: {self.username}\nEmail: {self.email}\
            \nAdmin: {bool(self.admin)}\nCredit: {self.credit}'

    def __init__(self, id, name, email, username, password, credit=0, admin=False):
        self.username = username
        self.email = email
        self.name = name
        self.password = password
        self.id = id
        self.admin = admin
        self.credit = credit


class questions_db(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    question = db.Column(db.Text)
    author = db.Column(db.String(200), db.ForeignKey("user_db.id"))
    likes = db.Column(db.Integer)
    time_asked = db.Column(db.DateTime)

    def __repr__(self):
        return f'User ID: {self.author}\nQuestion: {self.question}\nPopularity: {self.likes}'

    def __init__(self, id, question, author, asked_on, likes=0):
        self.id = id
        self.question = question
        self.likes = likes
        self.author = author
        self.time_asked = asked_on


class answers_db(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    answers = db.Column(db.Text)
    author = db.Column(db.String(200), db.ForeignKey('user_db.id'))
    question = db.Column(db.String(200), db.ForeignKey('questions_db.id'))
    time_answered = db.Column(db.DateTime)

    def __repr__(self):
        return f'Question ID: {self.question}\nAnswer: {self.answers}'

    def __init__(self, id, answer, author, time_answer, question):
        self.id = id
        self.answers = answer
        self.author = author
        self.question = question
        self.time_answered = time_answer

# this is the question likes and dislikes table schema,
# the frontned sends 1 or 0 as the response which is then
# interpreter as like and dislike respectively


class question_responses(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    time = db.Column(db.DateTime)
    question_id = db.Column(db.String(200), db.ForeignKey('questions_db.id'))
    user_id = db.Column(db.String(200), db.ForeignKey('user_db.id'))
    response = db.Column(db.Boolean)

    def __repr__(self):
        if self.response == True:
            resp = 'Liked'
        elif self.response == False:
            resp = 'Disliked'
        else:
            resp = 'Unknown'
        return f'Question ID: {self.question_id} \
                is {resp} by {self.user_id} at {self.time}'

    def __init__(self, id, response, user, question, time):
        self.id = id
        self.time = time
        self.response = response
        self.user_id = user
        self.question_id = question


db.create_all()


# this is the JWT checker, this token is used to make the user stay signed in
# in the front end, the token has the user id and the expiry embedded into it.

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return make_response({'message': 'token is missing'})
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = user_db.query.filter_by(id=data['id']).first()
        except:
            return make_response({'message': 'token is invalid'})
        return f(current_user, *args, **kwargs)
    return decorator

# main serving route


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# admin routes, mostly signup login and monitoring


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        is_admin = bool(data['admin'])
    except:
        is_admin = False
    if data['password'] and data['email'] and data['username']:
        hashed_password = generate_password_hash(
            data['password'], method='sha256')
        email = user_db.query.filter_by(email=data['email']).first()
        if email:
            return make_response({"email": "the email has been already registered"})
        else:
            new_user = user_db(id=str(uuid.uuid4()), name=data['name'], email=data['email'],
                               password=hashed_password, admin=is_admin, username=data['username'])

            db.session.add(new_user)
            db.session.commit()
            return make_response({'username': data['username'],
                                  'email': data['email'],
                                  'status': 'registered'})

# this is a login route which return jwt and creds about the user
# route type  : public


@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or not data['email'] or not data['password']:
        return make_response('could not verify', 401, {'Authentication': 'login required"'})
    user_ent = user_db.query.filter_by(email=data['email']).first()
    # print(f'user_ent.id={user_ent.id}')
    if check_password_hash(user_ent.password, data['password']):
        token = jwt.encode({'id': str(user_ent.id), 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=1440)}, app.config['SECRET_KEY'], "HS256")
        print(token)
        return make_response({'username': str(user_ent.username),
                              'email': str(user_ent.email), 'token': token, 'credit': int(user_ent.credit)})
    else:
        return make_response({'errmsg': "Incorrect password"})


@app.route('/api/admin/users', methods=['GET'])
@token_required
def show_users(current_user):
    if current_user.admin:
        users = user_db.query.all()
        output = []
        for usr in users:
            output.append({
                'id': usr.id,
                'name': usr.name,
                'email': usr.email
            })
        return make_response({'users': output})
    else:
        return make_response('could not verify admin',  401, {'Authentication': '"login required"'})

# this send the all the question available in the database
# route type : private


@app.route('/api/questions/all', methods=['GET'])
@token_required
def show_questions(current_user):
    if current_user:
        questions = questions_db.query.all()
        if questions:
            output = []
            for question in questions:
                output.append({
                    'id': question.id,
                    'question': question.question,
                    'author': question.author,
                    'likes': question.likes,
                })
            return make_response({'questions': output})
        else:
            return make_response({'questions': "no questions"})
    else:
        return make_response('could not verify admin',  401, {'Authentication': '"login required"'})

# The question routes


# this route is used for adding the question
#  route type : private

@app.route('/api/question/add', methods=['POST'])
@token_required
def addQuestion(current_user):

    data = request.get_json()
    print(data['question'])
    if len(data['question']) > 5:
        new_quest = questions_db(id=str(uuid.uuid4()), question=data['question'],
                                 likes=0, asked_on=datetime.datetime.now(),
                                 author=current_user.id)
        db.session.add(new_quest)
        current_user.credit += 1
        db.session.commit()
        return make_response({"question": data['question'], "questionid": new_quest.id})
    else:
        return make_response({"errmsg": "question should atleast have 6 character"})

# this  route is used to delete the question only by the authour
# route type : private


@app.route('/api/question/delete', methods=['POST'])
@token_required
def DeleteQuestion(current_user):
    data = request.get_json()
    if data['questionid']:
        question = questions_db.query.filter_by(id=data['questionid']).first()
        if question:
            if question.author == current_user.id:
                db.session.delete(question)
                db.session.commit()
                return make_response({'result': 'successfully deleted'})
            else:
                return make_response({'errmsg': 'you are not an author of this question'})
        else:
            return make_response({'errmsg': 'question is not in exisistance'})

    else:
        return make_response({'errmsg': 'invalid request'})


#  this route will return the based on the  likes
#  route type : private


@app.route('/api/question/fquest', methods=['GET'])
def PopularQuestion():
    questions = questions_db.query.filter(questions_db.likes >= popularity_lim).order_by(
        db.desc(questions_db.likes)).limit(10)
    output = []
    for quest in questions:
        output.append({
            'id': quest.id,
            'question': quest.question,
            'likes': quest.likes,
            'author': quest.author
        })
    return make_response({'popular_questions': output})

# this route  is used to serch for the substring of the question
# route type : private


@app.route('/api/questions/search', methods=['POST'])
def FindQuestion():
    data = request.get_json()
    questions = questions_db.query.filter(questions_db.question.contains(data['query'])).order_by(
        db.desc(questions_db.time_asked)).limit(10)
    output = []
    for quest in questions:
        output.append({
            'id': quest.id,
            'question': quest.question,
            'likes': quest.likes,
            'author': quest.author
        })
    return make_response({'results': output})


# this route is used to find the most recently posted questions
# and return a list of ten found questions
# route type : private

@app.route('/api/question/new', methods=['POST'])
def recentQuestion():
    questions = questions_db.query.order_by(
        db.desc(questions_db.time_asked)).limit(10)
    output = []
    for quest in questions:
        output.append({
            'id': quest.id,
            'question': quest.question,
            'likes': quest.likes,
            'author': quest.author
        })
    return make_response({'results': output})

# this  route will return the question created by the current user
#  route type : private


@app.route('/api/question/myquest', methods=['POST'])
@token_required
def userQuestions(current_user):
    questions = questions_db.query.filter_by(
        author=current_user.id).order_by(questions_db.likes).limit(10)
    output = []
    for quest in questions:
        output.append({
            'id': quest.id,
            'question': quest.question,
            'likes': quest.likes,
            'author': quest.author
        })
    return make_response({'results': output})


# the answers routes


# the answers routes
# this route is used to add an answer as the logged in user to the selected question

@app.route('/api/answers/addanswer', methods=['POST'])
@token_required
def addAnswer(current_user):
    data = request.get_json()
    if len(data['answer']) > 4:
        ans_id = str(uuid.uuid4())
        new_ans = answers_db(id=ans_id, question=data['question'], answer=data['answer'],
                             author=current_user.id, time_answer=datetime.datetime.now())
        db.session.add(new_ans)
        current_user.credit += 5
        db.session.commit()
        return make_response({"answer_id": str(ans_id)})
    else:
        return make_response({"errmsg": "answer should atleast have 5 character"})

# this route is used to get the answers for a given question using the question id
# route type : private


@app.route('/api/answers/getanswers', methods=['POST'])
def getAnswer():
    data = request.get_json()
    answers = answers_db.query.filter_by(question=data['question'])
    output = []
    for ans in answers:
        user = user_db.query.filter_by(id=ans.author).first()
        output.append({
            'id': ans.id,
            'answer': ans.answers,
            'username': user.username,
            'credits': user.credit
        })
    return make_response({'results': output})

# likes routes


# likes and dislikes routes
# this routes processes the like and dislike event generated form the frontend
# if a question is liked or disliked for the first time by a user then it adds
# in a new record to the question_response table, from the second time onwards
# the value of the response is updated but new records are not made, decords are not deleted
# if the user has not interacted with a question then both liked and disliked are unset
# as such are countted as zero, after thefirst interaction they are tacked.

# route type : private

@app.route('/api/question/res', methods=['POST'])
@token_required
def questionResponse(current_user):
    data = request.get_json()
    question = questions_db.query.filter_by(id=data['question_id']).first()
    if question:
        resp = question_responses.query.filter(question_responses.question_id == data['question_id'],
                                               question_responses.user_id == current_user.id).first()
        if not resp:
            # liking or disliking for the first time
            newResp = question_responses(time=datetime.datetime.now(), id=str(uuid.uuid4()),
                                         user=current_user.id, question=data['question_id'],
                                         response=bool(data['response']))
            if bool(data['response']):
                question.likes += 1
                res = 'liked successfully'
            else:
                question.likes -= 1
                res = 'disliked successfully'
            db.session.add(newResp)
        else:
            # liking or disliking if there is already a response
            if resp.response == bool(data['response']):
                res = 'already done'
            else:
                if bool(data['response']):
                    question.likes += 2  # removing the dislike and adding a like
                    res = 'liked successfully'
                    resp.response = bool(data['response'])
                else:
                    question.likes -= 2  # removing the like and adding a dislike
                    res = 'disliked successfully'
                    resp.response = bool(data['response'])
    else:
        res = 'question not found'
    db.session.commit()
    return make_response({'result': res})


if __name__ == '__main__':
    app.run(debug=True)
