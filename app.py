
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField ,SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'abcd'

db = SQLAlchemy(app)

# Database models
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __init__(self, username=None, password=None):
        if not username:
            raise ValueError("'username' cannot be None")
        if not password:
            raise ValueError("'password' cannot be None")
        self.username = username
        self.password = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    description = db.Column(db.String(50))
    is_done = db.Column(db.Boolean, default=False)

# Form classes
class AuthForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password ', validators=[DataRequired()])
    submit = SubmitField('Login')

class TaskForm(FlaskForm):
    task = StringField('New task', validators=[DataRequired()])
    submit = SubmitField('Add new task')

# Routes
@app.route('/', methods=['GET', 'POST'])
def auth():
    form = AuthForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.checkpw(form.password.data.encode("utf8"), user.password):
                session['logged_in'] = user.id
                return redirect(url_for('todo', user_id=user.id))

    return render_template('index.html', form=form, message='')

@app.route('/html/<int:user_id>/todo', methods=['GET', 'POST'])
def todo(user_id):
    if session['logged_in'] != user_id:
        return redirect(url_for('auth'))
    form = TaskForm()
    if form.validate_on_submit():
        task = Tasks(user_id=user_id, description=form.task.data, is_done=False)
        form.task.data = ''
        db.session.add(task)
        db.session.commit()
        # redirect to prevent form reposting
        return redirect(url_for('todo', user_id=user_id))
    category = Tasks.query.filter_by(user_id=user_id, is_done=False)
    return render_template('account.html', form=form, user_id=user_id, category=category, is_done=False)

@app.route('/html/<int:user_id>/done', methods=['GET', 'POST'])
def done(user_id):
    if session['logged_in'] != user_id:
        return redirect(url_for('auth'))
    form = TaskForm()
    if form.validate_on_submit():
        task = Tasks(user_id=user_id, description=form.task.data, is_done=True)
        form.task.data = ''
        db.session.add(task)
        db.session.commit()
        # redirect to prevent form reposting
        return redirect(url_for('done', user_id=user_id))
    category = Tasks.query.filter_by(user_id=user_id, is_done=True)
    return render_template('account.html', form=form, user_id=user_id, category=category, is_done=True)

@app.route('/html/<int:user_id>/convert<int:task_id>', methods=['GET', 'POST'])
def convert(user_id, task_id):
    if session['logged_in'] != user_id:
        return redirect(url_for('auth'))
    task = Tasks.query.get_or_404(task_id)
    task.is_done = not task.is_done
    db.session.commit()

    if (not task.is_done):
        return redirect(url_for('done', user_id=user_id))
    else:
        return redirect(url_for('todo', user_id=user_id))

@app.route('/html/<int:user_id>/update<int:task_id>', methods=['GET', 'POST'])
def update(user_id, task_id):
    if session['logged_in'] != user_id:
        return redirect(url_for('auth'))
    form = TaskForm()
    task = Tasks.query.get_or_404(task_id)
    current_description = task.description
    if form.validate_on_submit():
        task.description = form.task.data
        db.session.commit()

        if (task.is_done):
            return redirect(url_for('done', user_id=user_id))
        else:
            return redirect(url_for('todo', user_id=user_id))
        
    return render_template('update.html', form=form, description=current_description)

@app.route('/html/<int:user_id>/delete<int:task_id>', methods=['GET', 'POST'])
def delete(user_id, task_id):
    if session['logged_in'] != user_id:
        return redirect(url_for('auth'))
    task = Tasks.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    if (task.is_done):
        return redirect(url_for('done', user_id=user_id))
    else:
        return redirect(url_for('todo', user_id=user_id))

@app.route('/html/<int:user_id>/logout', methods=['GET', 'POST'])
def logout(user_id):
    if session['logged_in'] != user_id:
        return redirect(url_for('auth'))
    session['logged_in'] = None
    return redirect(url_for('auth'))

@app.route('/json', methods=['GET', 'POST'])
def show_json():
    users_tasks = []
    users = Users.query.all()
    for user in users:
        user_info = {
            'user_id': user.id,
            'username': user.username,
            'todo_tasks': [],
            'done_tasks': []
        }

        todo_tasks = Tasks.query.filter_by(user_id=user.id, is_done=False).all()
        done_tasks = Tasks.query.filter_by(user_id=user.id, is_done=True).all()
        for task in todo_tasks:
            user_info['todo_tasks'].append({
                'task_id': task.id,
                'description': task.description
            })
        for task in done_tasks:
            user_info['done_tasks'].append({
                'task_id': task.id,
                'description': task.description
            })

        users_tasks.append(user_info)

    return jsonify(users_tasks=users_tasks)

@app.route('/json/<int:user_id>', methods=['GET', 'POST'])
def show_user_json(user_id):
    user = Users.query.get_or_404(user_id)
    user_info = {
        'user_id': user.id,
        'username': user.username,
        'todo_tasks': [],
        'done_tasks': []
    }
    
    todo_tasks = Tasks.query.filter_by(user_id=user_id, is_done=False).all()
    done_tasks = Tasks.query.filter_by(user_id=user_id, is_done=True).all()
    for task in todo_tasks:
        user_info['todo_tasks'].append({
            'task_id': task.id,
            'description': task.description
        })
    for task in done_tasks:
        user_info['done_tasks'].append({
            'task_id': task.id,
            'description': task.description
        })

    return jsonify(user_info)


if __name__ == '__main__':
    app.run(debug=True)