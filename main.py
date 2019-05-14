import webapp2
import os
from google.appengine.ext.webapp import template
from models.users import Users
from models.group import Group
from models.message import Message
import datetime
from gaesessions import get_current_session
import base64
import json
import logging
PATH = os.path.dirname(__file__)+'/views'


class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.is_active():
            logging.info(
                "session is already active! Redirecting it to Home page")
            self.redirect('/home')
        path = os.path.join(PATH, 'main.html')
        context = {
            'data': 'WelcomeHandler'
        }
        self.response.write(template.render(path, context))

    def post(self):
        email = self.request.get("email")
        password = self.request.get("password")
        password = base64.b64decode(password)
        user = Users.get_user(email)
        if user and user.password == password:
            session = get_current_session()
            if session.is_active():
                session.terminate()
            # start a session for the user (old one was terminated)
            session['account'] = user
            response = {}
            response['status'] = 200
            response['message'] = 'login-success'
            logging.info("Login Success with user {0}".format(user.name))
            self.response.out.write(json.dumps(response))
        else:
            response = {}
            response['status'] = 401
            response['message'] = 'login-failed'
            logging.info("Login attepmt failed!")
            self.response.out.write(json.dumps(response))


class HomePageHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if not session.is_active():
            self.redirect('/')
        path = os.path.join(PATH, 'home.html')
        group_data = Group.query().fetch()
        logging.info("fetched Group data")
        user_data = Users.query().fetch()
        logging.info("fetched user data")
        user = session['account']
        context = {
            'current_user': user,
            'group_data': group_data,
            'user_data': user_data
        }
        self.response.write(template.render(path, context))


class GroupHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if not session.is_active():
            self.redirect('/')
        path = os.path.join(PATH, 'group.html')
        data = 'Hello'
        context = {
            'data': data
        }
        logging.info("Group creation page rendered")
        self.response.write(template.render(path, context))

    def post(self):
        # create a new group
        session = get_current_session()
        user = session['account']
        name = self.request.get("name")
        date = datetime.datetime.now()
        group = Group.get_group(name)
        logging.info("fetched Group data for current name")
        if not group:
            key = Group(name=name, created_on=date, number_of_people=0,
                        admin="karanm@gmail.com", users="").put()
            response = {}
            response['status'] = 200
            response['message'] = 'Group Created Successfully'
            logging.info("Group created successfully")
            self.response.out.write(json.dumps(response))
        else:
            response = {}
            response['status'] = 412
            response['message'] = 'Group already exist'
            logging.info("Group already exist")
            self.response.out.write(json.dumps(response))


class GroupChatHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        user = session['account']
        name = self.request.params.get('name')
        data = Message.get_messages(name)
        logging.info("fetched message data of group {0}".format(name))
        msgs = []
        for i in data:
            mg = {
                'msg': i.text,
                'sender_name': i.sender_name,
                'sent_to': i.sent_to,
                'created_on': str(i.created_on),
            }
            msgs.append(mg)

        response = {
            'user': user.name,
            'chat_with': name,
            'data': json.dumps(msgs),
            'status': 200
        }
        self.response.out.write(json.dumps(response))


class MessageHandler(webapp2.RequestHandler):

    def post(self):
        session = get_current_session()
        group_name = self.request.get("name")
        print group_name
        user = session['account']
        print user
        sender_name = user.name
        message = self.request.get("msg")
        date = datetime.datetime.now()
        current_user = user.email
        to_person = group_name
        key = Message(created_on=date, sender_name=sender_name, sent_by=current_user, sent_to=to_person,
                      text=message, status="read").put()
        logging.info("{0} sends message to {1}, Updated in db".format(
            sender_name, to_person))
        print key
        url = '/group/chat?name={0}'.format(group_name)
        self.redirect(url)


class UserSession(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.is_active():
            session.terminate()
        logging.info("Session is terminated,Logout!")
        self.redirect('/')


class RegistrationHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(PATH, 'register.html')
        context = {
            'data': 'register'
        }
        self.response.write(template.render(path, context))

    def post(self):
        name = self.request.get("name")
        email_id = self.request.get("email_id")
        password = self.request.get("password")
        password = base64.b64decode(password)
        user = Users.get_user(email_id)
        if user:
            response = {}
            response['status'] = 412
            response['message'] = 'User already exist'
            logging.info("User already exist")
            self.response.out.write(json.dumps(response))
        else:
            user = Users(email=email_id, password=password, name=name)
            user.put()
            response = {}
            response['status'] = 200
            response['message'] = 'user created successfully'
            logging.info("user created successfully")
            self.response.out.write(json.dumps(response))


class PersonalChatHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        user = session['account']
        name = self.request.params.get('name')
        data = Message.get_user_messeges(user.name, name)
        logging.info('Message fetched for chat with {0}'.format(name))
        msgs = []
        for i in data:
            mg = {
                'msg': i.text,
                'sender_name': i.sender_name,
                'sent_to': i.sent_to,
                'created_on': str(i.created_on),
            }
            msgs.append(mg)

        response = {
            'user': user.name,
            'chat_with': name,
            'data': json.dumps(msgs),
            'status': 200
        }
        self.response.out.write(json.dumps(response))

    def post(self):
        session = get_current_session()
        chat_with = self.request.get("chat_with")
        user = session['account']
        sender_name = user.name
        message = self.request.get("message")
        message = base64.b64decode(message)
        date = datetime.datetime.now()
        current_user = user.email
        to_person = chat_with
        key = Message(created_on=date, sender_name=sender_name, sent_by=current_user, sent_to=to_person,
                      text=message, status="read").put()
        logging.info("message created successfully")
        response = {}
        response['status'] = 200
        response['message'] = 'message sent'
        self.response.out.write(json.dumps(response))


app = webapp2.WSGIApplication([('/', WelcomeHandler),
                               ('/home', HomePageHandler),
                               ('/createGroup', GroupHandler),
                               ('/group/chat', GroupChatHandler),
                               ('/group/message', MessageHandler),
                               ('/logout', UserSession),
                               ('/register', RegistrationHandler),
                               ('/personal/chat', PersonalChatHandler),
                               ], debug=True)
