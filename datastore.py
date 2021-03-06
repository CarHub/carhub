#!/usr/bin/env python
from google.appengine.api import images
from google.appengine.ext import blobstore, ndb
import datetime
import models
import utils

def get_user_vehicle(user_id, vehicle_id):
    """Gets the UserVehicle instance for the given ID

    Args:
        vehicle_id - The vehicle ID

    Returns
        The UserVehicle with the given ID, None otherwise
    """

    car = models.UserVehicle.get_by_id(long(vehicle_id))

    if car and car.owner == user_id:
        return car
    else:
        return None

def get_all_user_vehicles(user_id):
    """Gets a list of vehicles for the given user

    Args:
        user_id - The user ID

    Returns
        The list of user's vehicles
    """

    userVehiclesQuery = models.UserVehicle.query(models.UserVehicle.owner == user_id)
    return ndb.get_multi(userVehiclesQuery.fetch(keys_only=True))

def get_all_expense_records(user_id, vehicle_id, day_range=30, ascending=True, polymorphic=True, keys_only=False):
    """Gets the BaseExpense for the given vehicle ID

    Args:
        vehicle_id - The vehicle ID
        day_range - The time range

    Returns
        The list of BaseExpense
    """

    if polymorphic:
        clazz = models.BaseExpense
    else:
        clazz = models.UserExpenseRecord

    if day_range:
        delta = datetime.timedelta(days=day_range)
        date = datetime.datetime.now() - delta
        query = clazz().query(clazz.owner == user_id,
                              clazz.vehicle == long(vehicle_id),
                              clazz.date >= date)
    else:
        query = clazz().query(clazz.owner == user_id,
                              clazz.vehicle == long(vehicle_id))

    if ascending:
        query = query.order(clazz.date)
    else:
        query = query.order(-clazz.date)


    if keys_only:
        return query.fetch(keys_only=True)
    else:
        return ndb.get_multi(query.fetch(keys_only=True))

def get_base_expense_record(user_id, vehicle_id, expense_id):
    """Gets the BaseExpense for the given expense_id

    Args:
        vehicle_id - The vehicle ID
        expense_id - The expense ID

    Returns
        The BaseExpense
    """

    if expense_id:
        baseExpense = models.BaseExpense.get_by_id(long(expense_id))

        if baseExpense and str(baseExpense.owner) == str(user_id) and str(baseExpense.vehicle) == str(vehicle_id):
            return baseExpense

    return None

def get_fuel_records(user_id, vehicle_id, day_range=30, ascending=True):
    """Gets the FuelRecords for the given vehicle ID

    Args:
        vehicle_id - The vehicle ID
        day_range - The time range (None for all)

    Returns
        The list of FuelRecords
    """

    if day_range:
        delta = datetime.timedelta(days=day_range)
        date = datetime.datetime.now() - delta
        query = models.FuelRecord().query(models.FuelRecord.owner == user_id,
                                          models.FuelRecord.vehicle == long(vehicle_id),
                                          models.FuelRecord.date >= date)
    else:
        query = models.FuelRecord().query(models.FuelRecord.owner == user_id,
                                          models.FuelRecord.vehicle == long(vehicle_id))

    if ascending:
        query = query.order(models.FuelRecord.date)
    else:
        query = query.order(-models.FuelRecord.date)

    return ndb.get_multi(query.fetch(keys_only=True))

def get_avg_gas_mileage(user_id, vehicle_id):
    """Gets the Average MPG based on FuelRecords for the given vehicle ID

    Args:
        vehicle_id - The vehicle ID

    Returns
        The average mpg
    """
    fuelRecords = get_fuel_records(user_id, vehicle_id, None, False)

    milesLogged = 0
    gallonsTotal = 0
    for fuelRecord in fuelRecords:
        if fuelRecord.odometerEnd != -1 and fuelRecord.odometerStart != -1 and fuelRecord.gallons != -1:
            gallonsTotal += fuelRecord.gallons
            milesLogged += (fuelRecord.odometerEnd - fuelRecord.odometerStart)

    avgMpg = 0
    if milesLogged > 0:
        avgMpg = utils.format_float(milesLogged / gallonsTotal)

    return avgMpg

def get_total_miles(user_id, vehicle_id):
    """Gets the miles logged based on FuelRecords for the given vehicle ID

    Args:
        vehicle_id - The vehicle ID

    Returns
        The miles logged
    """
    fuelRecords = get_fuel_records(user_id, vehicle_id, None, False)

    milesLogged = 0
    for fuelRecord in fuelRecords:
        if fuelRecord.odometerEnd != -1 and fuelRecord.odometerStart != -1:
            milesLogged += (fuelRecord.odometerEnd - fuelRecord.odometerStart)

    return utils.format_int(milesLogged)

def get_cost_per_mile(user_id, vehicle_id):
    """Gets the miles logged based on FuelRecords for the given vehicle ID

    Args:
        vehicle_id - The vehicle ID

    Returns
        The miles logged
    """
    fuelRecords = get_fuel_records(user_id, vehicle_id, None, False)

    milesLogged = 0
    costTotal = 0
    costPerMile = 0
    for fuelRecord in fuelRecords:
        if fuelRecord.odometerEnd != -1 and fuelRecord.odometerStart != -1:
            milesLogged += (fuelRecord.odometerEnd - fuelRecord.odometerStart)
            costTotal += (fuelRecord.gallons * fuelRecord.costPerGallon)

    if milesLogged > 0:
        costPerMile = costTotal/milesLogged

    return utils.format_float(costPerMile)

def get_n_fuel_records(user_id, vehicle_id, numberToFetch=10, ascending=True):
    """Gets the FuelRecords for the given vehicle ID

    Args:
        vehicle_id - The vehicle ID
        day_range - The time range
        numberToFetch - The number of records to fetch

    Returns
        The list of FuelRecords
    """

    query = models.FuelRecord().query(models.FuelRecord.owner == user_id,
                                      models.FuelRecord.vehicle == long(vehicle_id))

    if ascending:
        query = query.order(models.FuelRecord.date)
    else:
        query = query.order(-models.FuelRecord.date)
    return ndb.get_multi(query.fetch(numberToFetch, keys_only=True))

def get_maintenance_records(user_id, vehicle_id, day_range=30, ascending=True):
    """Gets the MaintenanceRecords for the given vehicle ID

    Args:
        vehicle_id - The vehicle ID
        day_range - The time range

    Returns
        The list of MaintenanceRecords
    """

    if day_range:
        delta = datetime.timedelta(days=day_range)
        date = datetime.datetime.now() - delta
        query = models.MaintenanceRecord().query(models.MaintenanceRecord.owner == user_id,
                                                 models.MaintenanceRecord.vehicle == long(vehicle_id),
                                                 models.MaintenanceRecord.date >= date)
    else:
        query = models.MaintenanceRecord().query(models.MaintenanceRecord.owner == user_id,
                                                 models.MaintenanceRecord.vehicle == long(vehicle_id))

    if ascending:
        query = query.order(models.MaintenanceRecord.date)
    else:
        query = query.order(-models.MaintenanceRecord.date)

    return ndb.get_multi(query.fetch(keys_only=True))

def get_n_maint_records(user_id, vehicle_id, category_id, numberToFetch=10, ascending=True):
    """Gets the Maintenance Records for the given vehicle ID

    Args:
        vehicle_id - The vehicle ID
        day_range - The time range
        numberToFetch - The number of records to fetch

    Returns
        The list of FuelRecords
    """

    query = models.MaintenanceRecord().query(models.MaintenanceRecord.owner == user_id,
                                             models.MaintenanceRecord.vehicle == long(vehicle_id),
                                             models.MaintenanceRecord.categoryid == category_id)

    if ascending:
        query = query.order(models.FuelRecord.date)
    else:
        query = query.order(-models.FuelRecord.date)
    return ndb.get_multi(query.fetch(numberToFetch, keys_only=True))

def get_maintenance_categories(user_id, user_categories=True, default_categories=True, as_strings=False):
    """Gets a list of maintenance categories

    Args:
        user_id - The user ID
        default_categories - whether or not to include defaults

    Returns
        A list of categories for that user
    """
    users = []
    if user_categories:
        users.append(user_id)
    if default_categories:
        users.append("defaultMaintCategory")

    query = models.ExpenseCategory().query(models.ExpenseCategory.category == "Maintenance",
                                           models.ExpenseCategory.owner.IN(users))
    results = ndb.get_multi(query.fetch(keys_only=True))

    # If there isn't anything returned, add the default models and re-query
    if default_categories and len(results) == 0:
        add_default_maintenance_categories()
        results = ndb.get_multi(query.fetch(keys_only=True))

    if not as_strings:
        return results
    else:
        toRet = []

        for c in results:
            if not c.subcategory in toRet:
                toRet.append(c.subcategory)

        toRet.sort()
        return toRet

def add_default_maintenance_categories():
    """Adds the default expense categories to the DB"""
    models.ExpenseCategory(owner="defaultMaintCategory", category="Maintenance", subcategory="Oil Change").put()
    models.ExpenseCategory(owner="defaultMaintCategory", category="Maintenance", subcategory="Repair").put()
    models.ExpenseCategory(owner="defaultMaintCategory", category="Maintenance", subcategory="Recall").put()
    models.ExpenseCategory(owner="defaultMaintCategory", category="Maintenance", subcategory="Uncategorized").put()

def get_expense_categories(user_id, user_categories=True, default_categories=True, as_strings=False):
    """Gets a list of user categories

    Args:
        user_id - The user ID
        default_categories - whether or not to include defaults

    Returns
        A list of categories for that user
    """
    users = []
    if user_categories:
        users.append(user_id)
    if default_categories:
        users.append("defaultCategory")

    query = models.ExpenseCategory().query(models.ExpenseCategory.category != "Maintenance",
                                           models.ExpenseCategory.owner.IN(users))
    results = ndb.get_multi(query.fetch(keys_only=True))

    # If there isn't anything returned, add the default models and re-query
    if default_categories and len(results) == 0:
        add_default_expense_categories()
        results = ndb.get_multi(query.fetch(keys_only=True))

    if not as_strings:
        return results
    else:
        toRet = []

        for r in results:
            if r.subcategory and not r.subcategory in toRet:
                toRet.append(r.subcategory)
            elif not r.category in toRet:
                toRet.append(r.category)

        toRet.sort()
        return toRet

def add_default_expense_categories():
    """Adds the default expense categories to the DB"""

    # If you change this be sure to change the fuel record post function to be able to find it.
    models.ExpenseCategory(owner="defaultCategory", category="Fuel Up").put()
    models.ExpenseCategory(owner="defaultCategory", category="Car Wash").put()
    models.ExpenseCategory(owner="defaultCategory", category="Uncategorized").put()

def get_category_by_id(user_id, category_id):
    """Gets the BaseExpense for the given expense_id

    Args:
        vehicle_id - The vehicle ID
        expense_id - The expense ID

    Returns
        The BaseExpense
    """

    if category_id:
        expenseCategory = models.ExpenseCategory.get_by_id(long(category_id))

        if expenseCategory:
            return expenseCategory

    return None

def get_category_by_name(user_id, category_name, maintenance_only=False):
    """Gets the BaseExpense for the given expense_id

    Args:
        vehicle_id - The vehicle ID
        expense_id - The expense ID

    Returns
        The BaseExpense
    """
    if maintenance_only:
        query = models.ExpenseCategory().query(models.ExpenseCategory.category == "Maintenance",
                                               models.ExpenseCategory.subcategory == category_name,
                                               models.ExpenseCategory.owner.IN([user_id, "defaultMaintCategory"]))
    else:
        query = models.ExpenseCategory().query(ndb.AND(models.ExpenseCategory.owner.IN([user_id, "defaultCategory", "defaultMaintCategory"]),
                                                       ndb.OR(models.ExpenseCategory.category == category_name,
                                                              models.ExpenseCategory.subcategory == category_name)))

    category = query.get()
    return category

def get_current_odometer(user_id, vehicle_id):
    """Gets the user's last recorded mileage for specified vehicle

    Args:
        user_id - The user's ID
        vehicle_id - The vehicle's mileage we are querying

    Returns
        The last recorded mileage
    """

    lastMaintMileage = 0
    lastFuelMileage = 0

    maintRecordQuery = models.MaintenanceRecord().query(models.MaintenanceRecord.owner == user_id,
                                                        models.MaintenanceRecord.vehicle == vehicle_id)
    maintRecordQuery = maintRecordQuery.order(-models.MaintenanceRecord.odometer)
    lastMaintRecord = maintRecordQuery.get()
    if lastMaintRecord:
        lastMaintMileage = lastMaintRecord.odometer

    mileageQuery = models.FuelRecord().query(models.FuelRecord.owner == user_id,
                                             models.FuelRecord.vehicle == vehicle_id)
    mileageQuery = mileageQuery.order(-models.FuelRecord.odometerEnd)
    lastFuelRecord = mileageQuery.get()
    if lastFuelRecord:
        lastFuelMileage = lastFuelRecord.odometerEnd

    maxmileage = lastMaintMileage
    if lastFuelMileage > lastMaintMileage:
        maxmileage = lastFuelMileage

    return maxmileage

def get_total_cost(user_id, vehicle_id):
    """Gets the total spent on the specified vehicle

    Args:
        user_id - The user's ID
        vehicle_id - The vehicle's mileage we are querying

    Returns
        The total spent on the specified vehicle
    """

    totalCost = 0

    baseExpenses = get_all_expense_records(user_id, vehicle_id, None)

    for b in baseExpenses:
        totalCost += b.amount

    return totalCost

def delete_base_expense(user_id, expense):
    """Deletes a BaseExpense

    Args:
        user_id - The user's ID
        expense - The expense to delete
    """
    if expense and expense.owner == user_id:
        image = expense.picture
        if image:
            images.delete_serving_url(image)
            blobstore.BlobInfo.get(image).delete()

        expense.key.delete()

def delete_user_vehicle(user_id, vehicle_id):
    """Deletes a UserVehicle, along with any related records

    Args:
        user_id - The user's ID
        vehicle_id - The vehicle to delete
    """
    vehicle = get_user_vehicle(user_id, vehicle_id)
    if vehicle:
        expenseRecords = get_all_expense_records(user_id, vehicle_id, None)
        for r in expenseRecords:
            delete_base_expense(user_id, r)

        vehicle.key.delete()
