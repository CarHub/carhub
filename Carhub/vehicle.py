#!/usr/bin/env python
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers, template
import datastore
import datetime
import logging
import models
import os
import utils
import webapp2

class VehicleExpenseEditDeleteHandler(webapp2.RequestHandler):
    def get(self, vehicleId, pageName, expenseId):
        user = users.get_current_user()

        expense = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, expenseId)
        
        if expense:
            if expense._class_name() == "BaseExpense":
                self.redirect("/vehicle/" + vehicleId + "/expenses/" + pageName + "/" + expenseId)
                return
            elif expense._class_name() == "MaintenanceRecord":
                self.redirect("/vehicle/" + vehicleId + "/maintenance/" + pageName + "/" + expenseId)
                return
            elif expense._class_name() == "FuelRecord":
                self.redirect("/vehicle/" + vehicleId + "/gasmileage/" + pageName + "/" + expenseId)
                return
        
        self.redirect("/vehicle/" + vehicleId + "/expenses")

class VehicleExpenseHandler(blobstore_handlers.BlobstoreUploadHandler):
    def get(self, vehicleId, pageName, expenseId):
        context = utils.get_context()
        user = users.get_current_user()

        if not vehicleId:
            self.redirect("/")
        else:
            context["car"] = datastore.getUserVehicle(user.user_id(), vehicleId)
            context["categories"] = datastore.getUserExpenseCategories(user.user_id())
            
            if pageName == "add":
                blobstore_url = self.request.url + "/add"
                upload_url = blobstore.create_upload_url(blobstore_url)
                context["upload_url"] = upload_url
                
                path = os.path.join(os.path.dirname(__file__), 'templates/addexpense.html')
            elif pageName == "edit":
                blobstore_url = self.request.url
                upload_url = blobstore.create_upload_url(blobstore_url)
                context["upload_url"] = upload_url
                
                baseExpense = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, expenseId)
                context["editexpenseobj"] = baseExpense

                path = os.path.join(os.path.dirname(__file__), 'templates/addexpense.html')
            elif pageName == "delete":
                # Delete record
                baseExpense = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, expenseId)
                if baseExpense:
                    image = baseExpense.picture
                    if image:
                        blobstore.BlobInfo.get(image).delete()
                    
                    baseExpense.key.delete()
                else:
                    logging.warn("No object was deleted. Couldn't find it.")

                self.redirect("/vehicle/" + vehicleId + "/expenses")
                return
            else:
                context['userexpenses'] = datastore.getAllExpenseRecords(user.user_id(), vehicleId, None, False) 
                
                expenseTotal = 0;
                for expense in context['userexpenses']:
                    expenseTotal += expense.amount
                
                context['expensetotal'] = utils.format_float(expenseTotal)

                path = os.path.join(os.path.dirname(__file__), 'templates/expenses.html')
                
            self.response.out.write(template.render(path, context))
    
    def post(self, vehicleId, pageName, expenseId):
        user = users.get_current_user()

        fileChosen = self.request.get("file", None)
        recieptKey = None
        if fileChosen:
            upload_files = self.get_uploads('file')
            blob_info = upload_files[0]
            recieptKey = str(blob_info.key())
        
        dateString = self.request.get("datePurchased", None)
        datePurchased = datetime.datetime.strptime(dateString, "%Y/%m/%d")
        
        # TODO: do we need this? it doesn't appear to be used...
        newCategory = self.request.get("newCategory", None)
        
        # find out if new category has been added
        userCatgories = datastore.getUserExpenseCategories(user.user_id())
        category = self.request.get("category", "Uncategorized")
        if not category in userCatgories:
            # this is a new category, add it to the database
            newCategoryObj = models.UserExpenseCategory()
            newCategoryObj.owner = user.user_id()
            newCategoryObj.category = category
            newCategoryObj.put()

        location = self.request.get("location", "")
        amount = float(self.request.get("amount", None))
        description = self.request.get("description", "")
        logging.info("Expense Info Obtained %s %s %s %s %d", datePurchased, category, location, description, amount)
        
        if datePurchased and amount:
            if pageName == "edit":
                expense = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, expenseId)
            else:
                expense = models.BaseExpense()
            
            expense.date = datePurchased
            expense.category = category
            expense.location = location
            expense.amount = amount
            expense.description = description
            expense.picture = recieptKey
            expense.owner = user.user_id()
            expense.vehicle = long(vehicleId)
            expense.lastmodified = datetime.datetime.now()
            
            expense.put()

        self.redirect("/vehicle/%s/expenses" % vehicleId)     

class VehicleMaintenanceHandler(webapp2.RequestHandler):
    def get(self, vehicleId, pageName, maintenanceId):
        context = utils.get_context()
        user = users.get_current_user()
        
        if not vehicleId:
            path = os.path.join(os.path.dirname(__file__), 'templates/garage.html')
            self.response.out.write(template.render(path, context))
        else:
            context["car"] = datastore.getUserVehicle(user.user_id(), vehicleId)
            categories = datastore.getMaintenanceCategories(user.user_id())
            if len(categories) > 0:
                context["categories"] = categories
            
            if pageName == "add":
                blobstore_url = self.request.url + "/add"
                upload_url = blobstore.create_upload_url(blobstore_url)
                context["upload_url"] = upload_url
                
                path = os.path.join(os.path.dirname(__file__), 'templates/addexpense.html')
            elif pageName == "edit":
                blobstore_url = self.request.url
                upload_url = blobstore.create_upload_url(blobstore_url)
                context["upload_url"] = upload_url
                
                maintenanceRecord = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, maintenanceId)
                context["editmaintenanceobj"] = maintenanceRecord

                path = os.path.join(os.path.dirname(__file__), 'templates/addexpense.html')
            elif pageName == "delete":
                # Delete record
                maintenanceRecord = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, maintenanceId)
                if maintenanceRecord:
                    image = maintenanceRecord.picture
                    if image:
                        blobstore.BlobInfo.get(image).delete()
                        
                    maintenanceRecord.key.delete()
                else:
                    logging.warn("No maintenance record object was deleted. Couldn't find it.")

                self.redirect("/vehicle/" + vehicleId + "/maintenance")
                return
            
            else:
                path = os.path.join(os.path.dirname(__file__), 'templates/maintenance.html')
            
                maintRecords = datastore.getMaintenanceRecords(user.user_id(), vehicleId, None)
            
                if len(maintRecords) > 0:
                    context["maintRecords"] = maintRecords
                
            self.response.out.write(template.render(path, context))
    
    def post(self, vehicleId, pageName, maintenanceId):
        user = users.get_current_user()
        
        logging.info("entered the Maintenance Expense post function")
        
        if user:
            dateString = self.request.get("datePurchased", None)
            datePurchased = datetime.datetime.strptime(dateString, "%Y/%m/%d")
            
            category = self.request.get("category", "Uncategorized")
            maintCategories = datastore.getMaintenanceCategories(user.user_id())
            
            if not (category in maintCategories):
                newCategoryObj = models.MaintenanceCategory()
                newCategoryObj.owner = user.user_id()
                newCategoryObj.category = category
                newCategoryObj.put()

            location = self.request.get("location", "")
            amount = float(self.request.get("amount", None))
            description = self.request.get("description", "")
            odometer = self.request.get("odometerEnd", None)
            if odometer:
                odometer = int(odometer)
            else:
                odometer = -1
            logging.info("Maintenance Info Obtained %s %s %s %s %f %d", datePurchased, category, location, description, amount, odometer)
            
            if datePurchased and amount:
                if pageName == "edit":
                    maintRec = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, maintenanceId)
                else:
                    maintRec = models.MaintenanceRecord()
                
                maintRec.date = datePurchased
                maintRec.category = category
                maintRec.location = location
                maintRec.amount = amount
                maintRec.description = description
                maintRec.odometer = odometer
                maintRec.owner = user.user_id()
                maintRec.vehicle = long(vehicleId)
                maintRec.lastmodified = datetime.datetime.now()
                
                maintRec.put()

        self.redirect("/vehicle/%s/maintenance" % vehicleId)

class VehicleGasMileageHandler(webapp2.RequestHandler):
    def get(self, vehicleId, pageName, fuelRecordId):
        context = utils.get_context()
        user = users.get_current_user()
        context["car"] = datastore.getUserVehicle(user.user_id(), vehicleId)
        context["categories"] = datastore.getUserExpenseCategories(user.user_id())
        context['userfuelrecords'] = datastore.getFuelRecords(user.user_id(), vehicleId, None, False)
        
        # TODO: do we need this latestFuel record?
        latestFuel = datastore.getNFuelRecords(user.user_id(), vehicleId, 1, False)
        if latestFuel and len(latestFuel) > 0:
            context["lastfuelrecord"] = latestFuel[0]
        
        i = 0
        mpgTots = 0
        mpgTotal = 0
        gallonsTotal = 0
        milesLogged = 0
        for fuelRecord in context['userfuelrecords']:
            if fuelRecord.mpg > -1 and fuelRecord.gallons > -1:
                i = i + 1
                mpgTots += fuelRecord.mpg
                mpgTotal += fuelRecord.mpg * fuelRecord.gallons
                gallonsTotal += fuelRecord.gallons
            if fuelRecord.odometerEnd != -1 and fuelRecord.odometerStart != -1:
                milesLogged += (fuelRecord.odometerEnd - fuelRecord.odometerStart)
        
        if i != 0:
            context['avgmpg'] = utils.format_float(mpgTotal / gallonsTotal)
        else:
            context['avgmpg'] = 0

        # add milestotal as a comma-delimited string
        context['milestotal'] = utils.format_int(milesLogged)
        
        if not vehicleId:
            self.redirect("/")
        else:
            if pageName == "add":
                blobstore_url = self.request.url + "/add"
                upload_url = blobstore.create_upload_url(blobstore_url)
                context["upload_url"] = upload_url
                
                path = os.path.join(os.path.dirname(__file__), 'templates/addexpense.html')
            elif pageName == "edit":
                blobstore_url = self.request.url
                upload_url = blobstore.create_upload_url(blobstore_url)
                context["upload_url"] = upload_url
                
                fuelRecord = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, fuelRecordId)
                context["editfuelrecordobj"] = fuelRecord

                path = os.path.join(os.path.dirname(__file__), 'templates/addexpense.html')
            elif pageName == "delete":
                # Delete record
                fuelRecord = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, fuelRecordId)
                if fuelRecord:
                    image = fuelRecord.picture
                    if image:
                        blobstore.BlobInfo.get(image).delete()

                    fuelRecord.key.delete()
                else:
                    logging.warn("No fuel record object was deleted. Couldn't find it.")

                self.redirect("/vehicle/" + vehicleId + "/maintenance")
                return
                
            else:
                path = os.path.join(os.path.dirname(__file__), 'templates/gasmileage.html')
                
            self.response.out.write(template.render(path, context))
    
    def post(self, vehicleId, pageName, fuelRecordId):
        # TODO: handle what to do if the optional fields are not entered.
        user = users.get_current_user()
        
        logging.info("entered the Gas Mileage Expense post function")
        
        if user:
            dateString = self.request.get("datePurchased", None)
            datePurchased = datetime.datetime.strptime(dateString, "%Y/%m/%d")

            location = self.request.get("location", "")
            amount = float(self.request.get("amount", None))
            costPerGallon = float(self.request.get("pricepergallon", None))
            fuelGrade = self.request.get("grade")
            
            # try to get from last fuel record if user wants to, or else try to get it from 
            #      the manual entry tab if it is not entered then assume it is -1 which means N/A
            useOdometerLastRecord = self.request.get("sinceLastFuelRecord", False)
            
            lastFuelRecord = None
            if useOdometerLastRecord:
                # find the previous gas record and grab the odometer reading
                latestFuel = datastore.getNFuelRecords(user.user_id(), vehicleId, 1, False)
                if latestFuel and len(latestFuel) > 0:
                    lastFuelRecord = latestFuel[0]
                    odometerStart = lastFuelRecord.odometerEnd
            if not lastFuelRecord:
                # try to get from manual odometer start entry
                odometerStart = self.request.get("odometerStart", None)
                if odometerStart and odometerStart != "Enter Odometer Start":
                    odometerStart = int(odometerStart)
                else:
                    odometerStart = -1
            
            
            odometerEnd = self.request.get("odometerEnd", None)
            if odometerEnd:
                odometerEnd = int(odometerEnd)
            else:
                odometerEnd = -1
            
            gallons = amount / costPerGallon
            if odometerEnd != -1 and odometerStart != -1:
                mpg = (odometerEnd - odometerStart) / gallons
            else:
                mpg = -1;
                    
            logging.info("Expense Info Obtained %s %s %d %d %d %d", datePurchased, location, amount, costPerGallon, odometerStart, odometerEnd)
            
            if datePurchased and amount and costPerGallon:
                if pageName == "edit":
                    record = datastore.getBaseExpenseRecord(user.user_id(), vehicleId, fuelRecordId)
                else:
                    record = models.FuelRecord()
                    
                record.date = datePurchased
                #TODO: this is the category for all Fuel Records, move to a constants file
                record.category = "Fuel Record"
                record.location = location
                record.amount = amount
                #TODO: this is the description for all fuel records, move to a constants file
                record.description = "Filled up with gas"
                record.gallons = gallons
                record.costPerGallon = costPerGallon
                record.fuelGrade = fuelGrade 
                record.odometerStart = odometerStart
                record.odometerEnd = odometerEnd
                record.mpg = mpg
                record.owner = user.user_id()
                record.vehicle = long(vehicleId)
                record.lastmodified = datetime.datetime.now()
                
                record.put()

        self.redirect("/vehicle/%s/gasmileage" % vehicleId)


class VehicleHandler(webapp2.RequestHandler):
    def get(self, vehicleId, pageName):
        context = utils.get_context()
        currentUserId = users.get_current_user().user_id()
        
        # If the path doesn't contain a first parameter, just show the garage
        if not vehicleId:
            path = os.path.join(os.path.dirname(__file__), 'templates/garage.html')
            
        # If the first path parameter is "add", show the add vehicle page 
        elif vehicleId == "add":
            context["vehicles"] = datastore.getListOfMakes()
            
            path = os.path.join(os.path.dirname(__file__), 'templates/addvehicle.html')
        
        # If we have a first path parameter, and it isn't add, use that as
        # the vehicle ID and show that vehicle's page
        else:
            context["car"] = datastore.getUserVehicle(currentUserId, vehicleId)
            context["latestMilage"] = utils.format_int(datastore.getLastRecordedMileage(currentUserId, long(vehicleId)))
            context["totalCost"] = utils.format_float(datastore.getTotalCost(currentUserId, long(vehicleId)))
            
            if not context["car"]:
                self.redirect("/")
            
            if pageName == "charts":
                path = os.path.join(os.path.dirname(__file__), 'templates/charts.html')
            elif pageName == "news":
                path = os.path.join(os.path.dirname(__file__), 'templates/news.html')
            else:
                path = os.path.join(os.path.dirname(__file__), 'templates/car.html')
                
        self.response.out.write(template.render(path, context))
    
    def post(self, makeOption, model):
        user = users.get_current_user()

        if makeOption == "add":
            make = self.request.get("make", None)
            model = self.request.get("model", None)
            year = self.request.get("year", None)
            
            if make and model and year:
                vehicle = models.UserVehicle()
                vehicle.make = make
                vehicle.model = model
                vehicle.year = year
                vehicle.owner = user.user_id()
                vehicle.lastmodified = datetime.datetime.now()
                
                vehicle.put()
        elif model == "update":
            vehicle = datastore.getUserVehicle(user.user_id(), makeOption)
            if vehicle:
                color = self.request.get("color", None)
                plates = self.request.get("plates", None)
                
                # Conditionally update the vehicle object
                vehicle.color = color if color else color.plates
                vehicle.plates = plates if plates else vehicle.plates
                
                vehicle.lastmodified = datetime.datetime.now()
                vehicle.put()
                
                self.redirect("/vehicle/%d" % vehicle.key.id())
                return

        elif model == "delete":
            datastore.deleteUserVehicle(user.user_id(), makeOption)
            
        self.redirect("/")
        
app = webapp2.WSGIApplication([ 
    ('/vehicle/([^/]+)/expenses/?([^/]+)?/?(.+)?', VehicleExpenseHandler),
    ('/vehicle/([^/]+)/expense/?([^/]+)?/?(.+)?', VehicleExpenseEditDeleteHandler),                 
    ('/vehicle/([^/]+)/maintenance/?([^/]+)?/?(.+)?', VehicleMaintenanceHandler),
    ('/vehicle/([^/]+)/gasmileage/?([^/]+)?/?(.+)?', VehicleGasMileageHandler),
    ('/vehicle/([^/]+)?/?(.+?)?', VehicleHandler),
], debug=True)
