from google.appengine.ext import ndb


# Define a model
class Group(ndb.Model):
    name = ndb.StringProperty(indexed=True, required=True)
    number_of_people = ndb.IntegerProperty(indexed=True, required=True)
    created_on = ndb.DateTimeProperty(indexed=True, required=True)
    admin = ndb.StringProperty(indexed=True, required=True)
    users = ndb.StringProperty(indexed=True)

    @staticmethod
    def get_group(name):
        user = Group.query().filter(ndb.GenericProperty("name") == name).get()
        return user
    