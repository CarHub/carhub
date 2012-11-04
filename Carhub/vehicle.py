#!/usr/bin/env python
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
import datastore
import datetime
import logging
import models
import os
import utils
import webapp2

class VehicleExpenseHandler(webapp2.RequestHandler):
    def get(self, vehicleId, pageName):
        context = utils.get_context()
        user = users.get_current_user()
        context["car"] = datastore.getUserVehicle(vehicleId)
        context["categories"] = datastore.getUserExpenseCategories(user.user_id())
        
        # TODO: this needs to grab based on vehicle chosen also
        # TODO: get all types of expenses
        userExpensesQuery = models.BaseExpense.query(models.BaseExpense.owner == user.user_id())
        userExpenses = ndb.get_multi(userExpensesQuery.fetch(keys_only=True))
        if len(userExpenses) > 0:
            context['userexpenses'] = userExpenses 
        
        if not vehicleId:
            self.redirect("/")
        else:
            if pageName == "add":
                path = os.path.join(os.path.dirname(__file__), 'templates/addexpense.html')
            else:
                path = os.path.join(os.path.dirname(__file__), 'templates/expenses.html')
                
            self.response.out.write(template.render(path, context))
    
    def post(self, vehicleId, model):
        currentUser = users.get_current_user()
        
        logging.info("entered the Expense post function")
        
        if currentUser:
            dateString = self.request.get("datePurchased", None)
            datePurchased = datetime.datetime.strptime(dateString, "%m-%d-%Y")
            newCategory = self.request.get("newCategory", None)
            
            if newCategory:
                category = newCategory
                newCategoryObj = models.UserExpenseCategory()
                newCategoryObj.owner = currentUser.user_id()
                newCategoryObj.category = newCategory

                if not newCategoryObj.category in datastore.getUserExpenseCategories(currentUser.user_id()):
                    newCategoryObj.put()

            else:
                category = self.request.get("category", None)

            location = self.request.get("location", None)
            amount = float(self.request.get("amount", None))
            description = self.request.get("description", None)
            logging.info("Expense Info Obtained %s %s %s %s %d", datePurchased, category, location, description, amount)
            
            if datePurchased and category and location and amount and description:
                expense = models.BaseExpense()
                expense.date = datePurchased
                expense.category = category
                expense.location = location
                expense.amount = amount
                expense.description = description
                
                expense.owner = currentUser.user_id()
                expense.vehicle = vehicleId
                expense.lastmodified = datetime.datetime.now()
                
                expense.put()

        self.redirect("/vehicle/%s/expenses" % vehicleId)

class VehicleHandler(webapp2.RequestHandler):
    def get(self, vehicleId, pageName):
        context = utils.get_context()
        
        # If the path doesn't contain a first parameter, just show the garage
        if not vehicleId:
            path = os.path.join(os.path.dirname(__file__), 'templates/garage.html')
            self.response.out.write(template.render(path, context))
            
        # If the first path parameter is "add", show the add vehicle page 
        elif vehicleId == "add":
            context["vehicles"] = datastore.getListOfMakes()
            
            path = os.path.join(os.path.dirname(__file__), 'templates/addvehicle.html')
            self.response.out.write(template.render(path, context))
        
        # If we have a first path parameter, and it isn't add, use that as
        # the vehicle ID and show that vehicle's page
        else:
            context["car"] = datastore.getUserVehicle(vehicleId)
                
            if pageName == "maintenance":
                path = os.path.join(os.path.dirname(__file__), 'templates/maintenance.html')
            elif pageName == "gasmileage":
                path = os.path.join(os.path.dirname(__file__), 'templates/gasmileage.html')
            elif pageName == "charts":
                path = os.path.join(os.path.dirname(__file__), 'templates/charts.html')
            elif pageName == "news":
                path = os.path.join(os.path.dirname(__file__), 'templates/news.html')
            elif pageName == "addrecord":
                path = os.path.join(os.path.dirname(__file__), 'templates/addrecord.html')
            else:
                path = os.path.join(os.path.dirname(__file__), 'templates/car.html')
                
            self.response.out.write(template.render(path, context))
    
    def post(self, makeOption, model):
        currentUser = users.get_current_user()

        if currentUser:
            make = self.request.get("make", None)
            model = self.request.get("model", None)
            year = self.request.get("year", None)
            
            if make and model and year:
                vehicle = models.UserVehicle()
                vehicle.make = make
                vehicle.model = model
                vehicle.year = year
                vehicle.owner = currentUser.user_id()
                vehicle.lastmodified = datetime.datetime.now()
                
                vehicle.put()
            
        self.redirect("/")

app = webapp2.WSGIApplication([
    ('/vehicle/([^/]+)/expenses/?(.+?)?', VehicleExpenseHandler),
    ('/vehicle/([^/]+)?/?(.+?)?', VehicleHandler),
], debug=True)