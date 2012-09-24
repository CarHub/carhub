package edu.se319.team1.carhub.servlets;

import java.io.IOException;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import edu.se319.team1.carhub.UserWrapper;
import edu.se319.team1.carhub.data.DatastoreUtils;

/**
 * Delete all CarResponseString
 */
@SuppressWarnings("serial")
public class DeleteAllCarResponseString extends HttpServlet {

	@Override
	public void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		UserWrapper user = UserWrapper.getInstance(req.getSession(false));

		if (user != null && user.isAdmin()) {
			DatastoreUtils.deleteAllCarResponseStrings();

			resp.sendRedirect("/admin/admin.jsp");
		} else {
			resp.sendRedirect("/");
		}
	}
}
