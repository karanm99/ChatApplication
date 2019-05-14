from google.appengine.ext import ndb


# Define a model
class Message(ndb.Model):
    created_on = ndb.DateTimeProperty(indexed=True, required=True)
    sender_name = ndb.StringProperty(indexed=True, required=True)
    sent_by = ndb.StringProperty(indexed=True, required=True)
    sent_to = ndb.StringProperty(indexed=True, required=True)
    text = ndb.StringProperty(indexed=True, required=True)
    status = ndb.StringProperty(indexed=True)

    @staticmethod
    def get_messages(sent_to):
        msg = Message.query().fetch()
        chat = []
        for i in msg:
            print i
            if i.sent_to == sent_to:
                chat.append(i)
        chat.sort(key=lambda x: x.created_on)
        return chat

    @staticmethod
    def get_user_messeges(user_name, chat_with):
        msg = Message.query().fetch()
        chat = []
        for i in msg:
            if i.sender_name == user_name and i.sent_to == chat_with:
                chat.append(i)
            if i.sender_name == chat_with and i.sent_to == user_name:
                chat.append(i)

        chat.sort(key=lambda x: x.created_on)
        return chat
