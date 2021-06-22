from ..config.mysqlconnection import connectToMySQL
from flask import flash
import re

from ..models import message

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__(self, data):
        self.id=data['id']
        self.first_name=data['first_name']
        self.last_name=data['last_name']
        self.email=data['email']
        self.password=data['password']
        self.created_at=data['created_at']
        self.updated_at=data['updated_at']
        self.messages=[]

    @classmethod
    def get_all_except(cls, data):
        query="SELECT * FROM users WHERE id!=%(id)s "\
            "ORDER BY last_name ASC;"
        results=connectToMySQL('private_wall_schema').query_db(query, data)
        all_users_except=[]
        if results!=False or results[0]!=None:
            for row in results:
                row_data={
                    'id':row['id'],
                    'first_name':row['first_name'],
                    'last_name':row['last_name'],
                    'email':row['email'],
                    'password':row['password'],
                    'created_at':row['created_at'],
                    'updated_at':row['updated_at']
                }
                all_users_except.append(cls(row_data))
        return all_users_except


    @classmethod
    def get_one(cls, data):
        query="SELECT * FROM users AS recipients "\
            "LEFT JOIN messages ON recipients.id=messages.recipient_id "\
            "LEFT JOIN users AS senders ON messages.sender_id=senders.id "\
            "WHERE recipients.id=%(id)s;"
        results=connectToMySQL('private_wall_schema').query_db(query, data)
        recipient=cls(results[0])
        print(results)
        if results[0]['messages.id']!=None:
            for row in results:
                row_data={
                    'id':row['messages.id'],
                    'message':row['message'],
                    'sender_id': row['sender_id'],
                    'sender_name': row['senders.first_name'],
                    'recipient_id': row['recipient_id'],
                    'created_at':row['messages.created_at'],
                    'updated_at':row['messages.updated_at']
                }
                recipient.messages.append(message.Message(row_data))
        return recipient

    @classmethod
    def get_by_email(cls, data):
        query="SELECT * FROM users WHERE email=%(email)s;"
        result=connectToMySQL('private_wall_schema').query_db(query, data)
        print(result)
        if len(result)<1:
            return False
        return cls(result[0])

    @classmethod
    def create(cls, data):
        query="INSERT INTO users (first_name, last_name, email, password, created_at, updated_at)"\
            "VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW())"
        result=connectToMySQL('private_wall_schema').query_db(query, data)
        return result

    @staticmethod
    def validate(data):
        is_valid=True
        if len(data['first_name'])<2:
            flash('*First name must be at least two characters', 'register_errors')
            is_valid=False

        if len(data['last_name'])<2:
            flash('*Last name must be at least two characters', 'register_errors')
            is_valid=False

        if not EMAIL_REGEX.match(data['email']):
            flash('*Invalid email address', 'register_errors')
            is_valid=False
        elif User.check_duplicate(data):
            flash(f"*{data['email']} is already in use on this site", 'register_errors')
            is_valid=False

        if len(data['password'])<8:
            flash('*Passwords must be at least eight characters', 'register_errors')
            is_valid=False
        elif data['password']!=data['confirm_password']:
            flash('*Passwords do not match', 'errors')
            is_valid=False

        return is_valid


    @staticmethod
    def check_duplicate(data):
        query='SELECT * FROM emails WHERE email=%(email)s;'
        results=connectToMySQL('private_wall_schema').query_db(query, data)
        is_dup=False
        if results!=False and len(results)>0:
            is_dup=True
        return is_dup