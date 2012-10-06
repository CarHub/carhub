<%@page language="java" contentType="text/html"%>

<!DOCTYPE html>
<html>
<head>
	<jsp:include page="/includes.jsp" />
	<script type="text/javascript" src="https://www.google.com/jsapi"></script>
	<script type="text/javascript">
		google.load("visualization", "1", {packages:["corechart"]});
		google.setOnLoadCallback(drawChart);
	
		function drawChart() {
			var data = new google.visualization.DataTable();
			data.addColumn('string', '');
			data.addColumn('number', '');

			var currentDate = new Date();
			var arr = [];
			for (var i = 10; i >= 0; i--) {
				var rand = Math.random();
				var result = 35;
				if (rand > .5) {
					result += (rand * 5); 
				} else {
					result -= (rand * 5);
				}
				
				var tmp = [];
				var tmpDate = new Date(currentDate.getTime() - (i * 604800000));
				tmp.push((tmpDate.getMonth() + 1) + "/" + tmpDate.getDate());
				tmp.push(result);
				
				arr.push(tmp);
			}
			
			data.addRows(arr);

			var options = { title: 'Average Gas Milage' };
	        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
	        chart.draw(data, options);
		}
	</script>
	
	<title>CarHub</title>
</head>
<body>
	<jsp:include page="/user/navbar.jsp" />

	<div class="container-fluid center-block">
		<div class="well">
			<div id="chart_div"></div>
		</div>
	</div>
</body>
</html>