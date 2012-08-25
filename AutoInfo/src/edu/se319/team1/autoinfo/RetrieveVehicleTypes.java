package edu.se319.team1.autoinfo;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.jdo.PersistenceManager;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.PreparedQuery;
import com.google.appengine.api.datastore.PreparedQuery.TooManyResultsException;
import com.google.appengine.api.datastore.Query;
import com.google.appengine.api.datastore.Query.CompositeFilterOperator;
import com.google.appengine.api.datastore.Query.FilterPredicate;
import com.google.appengine.api.datastore.Transaction;
import com.google.appengine.labs.repackaged.org.json.JSONArray;
import com.google.appengine.labs.repackaged.org.json.JSONException;
import com.google.appengine.labs.repackaged.org.json.JSONObject;

import edu.se319.team1.autoinfo.data.Vehicle;

@SuppressWarnings("serial")
public class RetrieveVehicleTypes extends HttpServlet {

	/**
	 * The logger for AppEngine
	 */
	private static final Logger log = Logger.getLogger(RetrieveVehicleTypes.class.getSimpleName());

	@Override
	public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		PersistenceManager pm = PMF.get().getPersistenceManager();
		Date currentTime = new Date();
		List<Vehicle> vehicleList = new ArrayList<Vehicle>();

		// Grab the data from cars.com
		URL url = new URL("http://www.cars.com/js/mmyCrp.js");
		InputStream stream = url.openStream();

		// Convert the result into a string
		String serverResponse = Utilities.convertStreamToString(stream);

		// Just get the data part (the JSONArray)
		serverResponse = serverResponse.substring(serverResponse.indexOf('['), serverResponse.lastIndexOf(']') + 1);

		try {
			// Get the wrapping JSONArray
			JSONArray arr = new JSONArray(serverResponse);

			// For each entry in the JSONArray (each make is an entry)
			for (int i = 0; i < arr.length(); i++) {
				JSONObject obj = (JSONObject) arr.get(i);
				JSONObject make = (JSONObject) obj.get("mk");
				JSONArray models = (JSONArray) obj.get("mds");

				String makeString = make.getString("n");

				for (int j = 0; j < models.length(); j++) {
					JSONObject obj1 = (JSONObject) models.get(j);
					String model = obj1.getString("dn");
					String years = obj1.getString("yrs");

					// Years is a comma-delimited string of years
					String[] yearList = years.split(",");

					// Create a new Vehicle for each model year
					for (String year : yearList) {
						Vehicle vehicle = new Vehicle(makeString, model, year);
						vehicleList.add(vehicle);

						log.log(Level.FINE, vehicle.toString());
					}
				}
			}
		} catch (JSONException e) {
			log.log(Level.WARNING, e.getMessage());
			log.log(Level.WARNING, Arrays.toString(e.getStackTrace()));
			e.printStackTrace();
		}

		// Go through the list and add new entries, and update times
		// of pre-exisiting entries
		try {
			// Get the Datastore Service
			DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();

			for (Vehicle v : vehicleList) {
				Query q = new Query(Vehicle.class.getSimpleName());
				FilterPredicate make = new FilterPredicate(Vehicle.VehicleColumns.MAKE, Query.FilterOperator.EQUAL, v.getMake());
				FilterPredicate model = new FilterPredicate(Vehicle.VehicleColumns.MODEL, Query.FilterOperator.EQUAL, v.getModel());
				FilterPredicate year = new FilterPredicate(Vehicle.VehicleColumns.YEAR, Query.FilterOperator.EQUAL, v.getYear());

				q.setFilter(CompositeFilterOperator.and(make, model, year));

				try {
					// Prepare the query. Try and get the result as a single entity.
					//  - If the result is null, we don't have a record, so we want to add it
					//  - If the pq.asSingleEntity method throws a TooManyResultsException, just log an error
					Transaction txn = datastore.beginTransaction();
					PreparedQuery pq = datastore.prepare(q);
					Entity result = pq.asSingleEntity();

					// If result isn't null, update the last modified time to the current time
					if (result != null) {
						result.setProperty(Vehicle.VehicleColumns.LAST_MODIFIED, currentTime);
					} else {
						// If the result is null, we want to add the vehicle to the database
						pm.makePersistent(v);
					}

					if (txn.isActive()) {
						txn.commit();
					}
				} catch (TooManyResultsException ex) {
					log.log(Level.WARNING, "More than one result...");
					log.log(Level.WARNING, v.toString());
				}
			}
		} finally {
			pm.close();
		}

		// TODO: query database for records with old lastmodified times and possibly delete them...
	}
}
