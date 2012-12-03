from google.appengine.api import users
import hashlib
import datastore

def get_context(list_vehicles=True):
    context = {}
    context['loginurl'] = users.create_login_url("/")
    context['logouturl'] = users.create_logout_url("/")

    user = users.get_current_user()
    if user:
        userobj = {}
        userobj['isAdmin'] = users.is_current_user_admin()
        userobj['username'] = user.nickname()
        userobj['profilePic'] = "http://www.gravatar.com/avatar/%s?s=40" % hashlib.md5(user.email()).hexdigest()
        context['user'] = userobj
        
        if list_vehicles:
            userVehicles = datastore.getUserVehicleList(user.user_id())
            
            if len(userVehicles) > 0:
                context['uservehicles'] = sorted(userVehicles, key=lambda UserVehicle:UserVehicle.name())
            
            dateNotifications = datastore.getActiveDateNotifications(user.user_id())
            mileNotifications = datastore.getActiveMileageNotifications(user.user_id())
            totalNotifications = len(dateNotifications) + len(mileNotifications)
            
            if totalNotifications > 0:
                context['dateNotifications'] = dateNotifications
                context['mileNotifications'] = mileNotifications
                context['totalNotifications'] = totalNotifications
        
    else:
        context['user'] = None

    return context

def format_int(number):
    return '{:,d}'.format(number)

def format_float(number):
    return '{:,.2f}'.format(number)

def format_date(timestamp):
    return timestamp.strftime("%Y/%m/%d")
