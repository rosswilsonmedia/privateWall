from ..config.mysqlconnection import connectToMySQL
from flask import flash

from ..models import user

class Message:
    def __init__(self, data):
        self.id=data['id']
        self.message=data['message']
        self.sender_id=data['sender_id'] #User object expected
        self.sender_name=data['sender_name']
        self.recipient_id=data['recipient_id'] #User object expected
        self.created_at=data['created_at']
        self.updated_at=data['updated_at']

    @classmethod
    def create(cls, data):
        query="INSERT INTO messages (message, sender_id, recipient_id, created_at, updated_at)"\
            "VALUES (%(message)s, %(sender_id)s, %(recipient_id)s, NOW(), NOW())"
        result=connectToMySQL('private_wall_schema').query_db(query, data)
        print(result)
        return result

    @classmethod
    def delete(cls, data):
        query="DELETE FROM messages WHERE id=%(id)s;"
        result=connectToMySQL('private_wall_schema').query_db(query, data)
        return result

    @staticmethod
    def validate(data):
        is_valid=True
        if len(data['message'])<5:
            flash('*message must be more than five charaters', 'message_errors')
            is_valid=False
        return is_valid