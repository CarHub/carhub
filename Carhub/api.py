from google.appengine.ext import endpoints
from protorpc import remote
from models import *
import auth_util
import logging

ANDROID_CLIENT_ID = '280486107933.apps.googleusercontent.com'
ANDROID_DEBUG_CLIENT_ID = '280486107933-4r3v4nis34qimv27bc3pb8vppk38nvho.apps.googleusercontent.com'
CLIENT_ID = '280486107933-fkp13pk6dv84vdkumqu1vj5hh0o74he3.apps.googleusercontent.com'

# TODO: this probably isn't the best solution, but it should work for now
def get_user_by_auth(uid):
    user = User.query(User.google_oauth == uid).get()

    if user:
        return user
    else:
        current_user = endpoints.get_current_user()
        user_by_email = User.query(User.email_address == current_user.email()).get()

        if user_by_email:
            user_by_email.google_oauth = uid
            user_by_email.put()

        return user_by_email

@endpoints.api(name='carhub',version='v1',
               description='CarHub API',
               hostname='car-hub.appspot.com',
               audiences=[CLIENT_ID, ANDROID_CLIENT_ID, ANDROID_DEBUG_CLIENT_ID],
               allowed_client_ids=[ANDROID_CLIENT_ID, ANDROID_DEBUG_CLIENT_ID, CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID])
class CarHubApi(remote.Service):

    @UserVehicle.query_method(user_required=True, path='vehicles', name='vehicles.list')
    def VehiclesList(self, query):
        auth_user_id = auth_util.get_google_plus_user_id()
        user = get_user_by_auth(auth_user_id)

        if user:
            return query.filter(UserVehicle.owner == str(user.key.id()))
        else:
            raise endpoints.UnauthorizedException('Unknown user.')

application = endpoints.api_server([CarHubApi], restricted=False)
