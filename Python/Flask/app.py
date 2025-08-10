from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return f'<Task %r {self.id}>'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        task_content = request.form.get('content')
        if task_content:
            new_task = Todo(content=task_content)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('home'))
    todos = Todo.query.order_by(Todo.date_created).all()
    return render_template('index.html', todos=todos)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/complete/<int:id>')
def complete(id):
    task = Todo.query.get_or_404(id)
    task.completed = 1
    db.session.commit()
    return redirect(url_for('home'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)