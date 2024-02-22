from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return make_response([message.to_dict() for message in messages], 200)
    elif request.method == 'POST':
        request_dict = request.get_json()
        app.logger.warning(f'request_dict: {request_dict}')
        message = Message(
            username = request_dict.get('username'),
            body = request_dict.get('body')
        )
        db.session.add(message)
        db.session.commit()

        return make_response(message.to_dict(), 201)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if message == None:
        response_body = {
            'message': f'Message {id} not found.'
        }
        return make_response(response_body, 404)
    elif request.method == 'PATCH':
        request_dict = request.get_json()
        app.logger.warning(f'request_dict: {request_dict}')
        for attr in request_dict:
            setattr(message, attr, request_dict.get(attr))
        db.session.add(message)
        db.session.commit()

        return make_response(message.to_dict(), 200)
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        response_body = {
            'message': f'Message {id} is deleted'
        }
        return make_response(response_body, 200)

if __name__ == '__main__':
    app.run(port=5555,debug=True)
