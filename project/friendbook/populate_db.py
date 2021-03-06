import os
from datetime import datetime
import pytz
import uuid
utc=pytz.UTC

def populate():
    add_user(username="gayoung", password="test", role="author", active=1, git="gayoung")
    add_user(username="matt", password="test", role="author", active=1, git="")
    add_user(username="bob", password="test", role="author", active=1, git="")
    add_user(username="david", password="test", role="author", active=1, git="")
    add_user(username="sarah", password="test", role="author", active=1, git="")
    add_friend(username1="bob", username2="gayoung", accept=0)
    add_friend(username1="gayoung", username2="matt", accept=1)
    add_friend(username1="david", username2="matt", accept=1)

def add_user(username, password, role, active, git):
    today = utc.localize(datetime.now())
    guid = uuid.uuid4()
    user = Users.objects.get_or_create(guid = guid, username=username, password=password, role=role, register_date=today, active=active, github_account=git)[0]
    return user

def add_friend(username1, username2, accept):
    friend = Friends.objects.get_or_create(username1=username1, username2=username2, accept=accept)
    return friend

# Start execution here!
if __name__ == '__main__':
    print "Starting Rango population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'friendbook.settings')
    from main.models import Users, Posts, Comment, Friends
    populate()
