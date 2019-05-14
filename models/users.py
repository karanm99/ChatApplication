from google.appengine.ext import ndb

# Define a model


class Users(ndb.Model):
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True, indexed=True)
    password = ndb.StringProperty(required=True)

    @staticmethod
    def get_user(email_id):
        user = Users.query().filter(ndb.GenericProperty("email") == email_id).get()
        return user
