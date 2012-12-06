#!/usr/bin/env python
from google.appengine.api import users
from google.appengine.ext.webapp import template
import os
import utils
import webapp2
import datastore
import logging
import models

class SettingsHandler(webapp2.RequestHandler):
    def get(self, pageName, pageType, action, categoryId):
        context = utils.get_context()
        user = users.get_current_user()
        
        logging.warn("pageName = %s, pageType = %s" % (pageName, pageType))
        
        if user:
            if action == "delete":
                # Delete record
                category = datastore.getCategory(user.user_id(), pageType, categoryId)
                if category:
                    category.key.delete()
                else:
                    logging.warn("No category object was deleted. Couldn't find it.")
    
                self.redirect("/settings")
                return
            
            # go to regular settings page
            context["categories"] = datastore.getUserExpenseCategoryModels(user.user_id())
            context["maintcategories"] = datastore.getMaintenanceCategoryModels(user.user_id())
            path = os.path.join(os.path.dirname(__file__), 'templates/settings.html')
            self.response.out.write(template.render(path, context))
       
        else:
            self.redirect("/")
    def post(self, pageName, pageType, action, categoryId):
        user = users.get_current_user()
        if user:
            if action == "add":
                if pageType == "maintenance":
                    categories = datastore.getUserExpenseCategories(user.user_id())
                else:
                    categories = datastore.getUserExpenseCategories(user.user_id())
                    
                newName = self.request.get("categoryName", None)
                if newName and not newName in categories:
                    # this is a new category, add it to the database
                    if pageType == "maintenance":
                        newCategoryObj = models.MaintenanceCategory()
                    else:
                        newCategoryObj = models.UserExpenseCategory()
                    newCategoryObj.owner = user.user_id()
                    newCategoryObj.category = newName
                    newCategoryObj.put()
            
            if action == "edit":
                # Edit record
                category = datastore.getCategory(user.user_id(), pageType, categoryId)
                newName = self.request.get("categoryName", None)
                logging.warn("New Name %s" % newName)
                if category and newName:
                    category.category = newName
                    category.put()
                else:
                    logging.warn("No category object was edited. Couldn't find it.")
    
        self.redirect("/settings")
                
app = webapp2.WSGIApplication([
    ('/settings/?([^/]+)?/?([^/]+)?/?([^/]+)?/?(.+)?', SettingsHandler)
])

