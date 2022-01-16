import json
import os
from flask import g
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from flask import request
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug import security
from datetime import datetime
from werkzeug.exceptions import BadRequestKeyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
api = Api(app)
TOKEN = os.getenv("TOKEN")
auth = HTTPBasicAuth()

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    has_privilege = db.Column(db.Boolean, default=False, unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def hash_password(self, _password):
        self.password = security.generate_password_hash(_password)

    def verify_password(self, _password):
        return security.check_password_hash(self.password, _password)

    def __repr__(self):
        return f'<User {self.username}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False, unique=False, nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)

    sent_by = db.Column(db.Integer, db.ForeignKey('user.id'),
                            nullable=False)
    recipient = db.Column(db.Integer, db.ForeignKey('user.id'),
                                nullable=False)

    def __repr__(self):
        return f'<Message {"ID", self.id, self.subject}>'


@auth.verify_password
def verify_password(username: str, password: str) -> bool:
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@app.route('/api/send_message', methods=['POST'])
@auth.login_required
def send_message() -> str:
    if request.form['token'] == TOKEN:
        db.session.add(Message(
            subject=request.form['subject'],
            body=request.form['body'],
            sent_by=g.user.id,
            recipient=request.form['recipient'],
        ))
        db.session.commit()

        return f"<div>Sent a message to {User.query.filter_by(id=request.form['recipient']).first().username}</div>"


@app.route('/api/read_message/', methods=['GET'])
@auth.login_required
def read_message() -> str:
    user = g.user.id
    all_messages = Message.query.filter_by(recipient=user).filter_by(read=False)
    first_msg = all_messages.first()

    if first_msg is None:
        return "There are no new messages for this user"
    else:
        first_msg.read = True
        db.session.commit()
        return (f"<div>First unread message ID:{first_msg.id} "
                f" Sent by: {User.query.filter_by(id=first_msg.sent_by).first().username} "
                f" At: {first_msg.creation_date} "
                f" Subject: {first_msg.subject} "
                f" Message {first_msg.body} </div>"
                )


@app.route('/api/delete_message/<int:msg_id>', methods=['POST'])
@auth.login_required
def delete_message_byid(msg_id: int) -> str:
    message_for_deletion = Message.query.filter_by(id=msg_id).first()
    resp = f"Message ID {message_for_deletion.id} Deleted"
    db.session.delete(message_for_deletion)
    db.session.commit()
    return resp


@app.route('/api/all_msg_by_usrid/<int:usr_id>', methods=['GET'])
@auth.login_required
def all_msg_by_usrid(usr_id: int) -> str:
    all_messages = Message.query.filter_by(sent_by=usr_id).all()
    read_option = ""
    try:
        read_option = request.form['read']
    except BadRequestKeyError as e:
        "no-option-selected"
    if not read_option:
        all_messages = Message.query.filter_by(sent_by=usr_id, read=request.form['read']).all()

    response = {}
    for message in all_messages:
        response[message.id] = {
            "sent": message.sent_by,
            "subject": message.subject,
            "read": message.read,
            "body": message.body,
            "sent_to": User.query.filter_by(id=message.recipient).first().username,
        }
    return json.dumps(response)


if __name__ == '__main__':
    app.run(debug=True)
