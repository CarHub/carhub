<%@ page language="java" contentType="text/html"%>
<!DOCTYPE html>
<html>
<head>
	<jsp:include page="/includes.jsp" />

	<title>CarHub</title>
</head>
<body>
	<jsp:include page="/user/navbar.jsp" />

	<div class="container-fluid center-block">
		<div class="well well-small">
			<table class="table table-hover">
				<tr>
					<td>Reload Vehicles from Cars.com</td>
					<td>
						<form action="/cron/fetchvehicleinfo" method="GET">
							<button type="submit" class="btn pull-right">Reload</button>
						</form>
					</td>
				</tr>
				<tr>
					<td>Delete all Vehicles</td>
					<td>
						<form action="/admin/deletevehicles" method="POST">
							<button type="submit" class="btn btn-danger pull-right">Delete</button>
						</form>
					</td>
				</tr>
				<tr>
					<td>Delete all CarResponseString</td>
					<td>
						<form action="/admin/deletecarresponsestring" method="POST">
							<button type="submit" class="btn btn-danger pull-right">Delete</button>
						</form>
					</td>
				</tr>
				<tr>
					<td>Clear Server Cache</td>
					<td>
						<form action="/admin/clearmemcache" method="POST">
							<button type="submit" class="btn btn-danger pull-right">Delete</button>
						</form>
					</td>
				</tr>
			</table>
		</div>
	</div>
</body>
</html>