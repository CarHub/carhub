<%@page import="com.google.appengine.api.users.UserServiceFactory"%>
<%@page import="com.google.appengine.api.users.UserService"%>
<%@page import="edu.se319.team1.autoinfo.UserWrapper"%>
<%@page language="java" contentType="text/html"%>

<%
	UserWrapper user = UserWrapper.getInstance();
%>
<!DOCTYPE html>
<html>
<head>
	<link type="text/css" href="/css/bootstrap.min.css" rel="stylesheet" />
	<link type="text/css" href="/css/auto.css" rel="stylesheet" />
	<script type="text/javascript" src="/js/jquery.min.js"></script>
	<script type="text/javascript" src="/js/bootstrap.min.js"></script>

	<title>Automotive Info</title>
</head>
<body>
	<div class="navbar navbar-fixed-top">
		<div class="navbar-inner">
			<div class="container">
				<a class="brand" href="/">Automotive Info</a>
				<ul class="nav">
					<li><a href="/">Home</a></li>
					<li class="divider-vertical"></li>
					<% if (user.isAdmin()) { %>
					<li><a href="/admin/admin.jsp">Admin</a></li>
					<% } %>
				</ul>
				
				
				<ul class="nav pull-right">
					<jsp:include page="/username.jsp" />
				</ul>
			</div>
		</div>
	</div>

	<div class="container">
		<h2>Welcome...</h2>
		<p>Nothing exciting to see yet...</p>
	</div>
</body>
</html>