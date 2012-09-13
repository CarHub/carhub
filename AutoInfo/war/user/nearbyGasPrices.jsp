<%@page import="com.google.appengine.api.users.UserServiceFactory"%>
<%@page import="com.google.appengine.api.users.UserService"%>
<%@page import="edu.se319.team1.carhub.UserWrapper"%>
<%@page language="java" contentType="text/html"%>

<%
	UserWrapper user = UserWrapper.getInstance();
%>
<!DOCTYPE html>
<html>
<head>
	<jsp:include page="/includes.jsp" />

	<title>CarHub</title>
</head>
<body>
	<div class="navbar navbar-inverse navbar-fixed-top">
		<div class="navbar-inner">
			<div class="container">
				<a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</a>
			
				<a class="brand" href="/">CarHub</a>
				
				<div class="nav-collapse collapse">
					<jsp:include page="/user/navbar.jsp" />
					
					<div class="nav pull-right">
						<jsp:include page="/username.jsp" />
					</div>
				</div>
			</div>
		</div>
	</div>

	<div class="container-fluid center-block">
		<div class="row-fluid">
			<jsp:include page="/sideNav.jsp" />

			<div class="well well-small span9">
				<h2>Nearby Gas Prices</h2>

				<form action="form_action.asp" method="get">
					<input type="checkbox" name="vehicle" value="Bike" /> Detect my
					location<br /> <br /> Zip Code: <input type="text" name="fname" /><br />
					<br /> <input type="submit" value="Get Gas" />
				</form>
				
				<table class="table">

				<tr>
				<th>Name</th>
				<th>Location</th>
				<th>Price</th>
				<th>Last Updated</th>
				</tr>
				
				<tr>
				<td>Kum N' Go</td>
				<td>Ames, IA</td>
				<td>3.76</td>
				<td>Today</td>
				</tr>
				
				<tr>
				<td>Casey's</td>
				<td>Ames, IA</td>
				<td>3.84</td>
				<td>Today</td>
				</tr>
				
				<tr>
				<td>Shell</td>
				<td>Ames, IA</td>
				<td>3.90</td>
				<td>9/10/2012</td>
				</tr>
				
				<tr>
				<td>Quick Trip</td>
				<td>Ames, IA</td>
				<td>3.56</td>
				<td>9/4/2012</td>
				</tr>
				
				</table>

			</div>
		</div>
	</div>
</body>
</html>