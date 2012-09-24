<%@page import="java.net.URLEncoder"%>
<%@page import="edu.se319.team1.carhub.UserWrapper"%>
<%@page import="com.google.appengine.api.users.UserServiceFactory"%>
<%@ page language="java" contentType="text/html"%>

<%
	UserWrapper user = UserWrapper.getInstance(request.getSession(false));
	String fbURL = "http://www.facebook.com/dialog/oauth?client_id=176948449109248&redirect_uri=" + URLEncoder.encode("http://carhub.us/login_fb.do", "UTF-8") + "&scope=email";
%>

<% if (user.isLoggedIn()) { %>
<ul class="nav">
	<li class="hidden-phone">
		<% 
		String profilePictureUrl = user.getProfilePictureUrl();
		if (profilePictureUrl != null) {
		%>
		<img src="<%=profilePictureUrl %>" height="40px" width="40px" />
		<% } else { %>
		<a href="http://gravatar.com/emails" style="padding:0 0 0;" rel="tooltip" title="Change your avatar at gravatar.com" data-placement="bottom">
			<img src="http://www.gravatar.com/avatar/<%=user.getMd5() %>?s=40" />
		</a>
		<% } %>
	</li>
	<li class="dropdown">
		<a href="#" class="dropdown-toggle" data-toggle="dropdown"><%=user.getNickname() %> <b class="caret hidden-phone"></b></a>
		<ul class="dropdown-menu">
			<% if (user.isAdmin()) { %>
			<li><a href="/admin/admin.jsp">Admin</a></li>
			<% } %>
			<li><a href="/user/settings.jsp">Settings</a></li>
			<li class="divider"></li>
			<li><a href="<%= UserServiceFactory.getUserService().createLogoutURL("/") %>">Logout</a></li>
		</ul>
	</li>
</ul>

<% } else { %>
<li>
	<a href="<%= fbURL %>"><img src="/img/fb_connect.png" /></a>
</li>
<% } %>