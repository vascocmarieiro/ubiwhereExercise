from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import datetime
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "ubiwhere": generate_password_hash("ubiwhere"),
    
}


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)



basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), unique=False)
    description = db.Column(db.String(120), unique=False)
    local = db.Column(db.String(120), unique=False)
    category = db.Column(db.String(120), unique=False)
    created= db.Column(db.String(120), unique=False)
    updated= db.Column(db.String(120), unique=False)
    state= db.Column(db.String(120), unique=False)

    def __init__(self, author, description,local,category,created,updated,state):
        self.author = author
        self.description = description
        self.local=local
        self.category=category
        self.created=created
        self.updated=updated
        self.state=state
        


class TaskSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id','author', 'description','local','category','created','updated','state')


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


# endpoint to create new task
@app.route("/tasks", methods=["POST"])
def add_task():
    author = request.json['author']
    description = request.json['description']
    local=request.json['local']
    category=request.json['category']
    created=datetime.datetime.now()
    updated=None
    state='Por validar'
    
    new_task = Task(author, description,local,category,created,updated,state)

    db.session.add(new_task)
    db.session.commit()

    return task_schema.jsonify(new_task)


# endpoint to show all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    all_tasks = Task.query.all()
    result = tasks_schema.dump(all_tasks)
    return jsonify(result)





# endpoint to get task detail by id
@app.route("/tasks/<id>", methods=["GET"])
def task_detail(id):
    task = Task.query.get(id)
    return task_schema.jsonify(task)




# endpoint to update task
@app.route("/tasks/<id>", methods=["PUT"])
@auth.login_required
def task_update(id):
    task = Task.query.get(id)
    
    updated=datetime.datetime.now()
    state=request.json['state']

    
    task.updated=updated
    task.state=state

    db.session.commit()
    return task_schema.jsonify(task)


# endpoint to delete task
@app.route("/tasks/<id>", methods=["DELETE"])
def task_delete(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()

    return task_schema.jsonify(task)


if __name__ == '__main__':
    app.run(debug=True)