var poolColors = function (a) {
  var pool = [];
  for(i=0;i<a;i++){
    pool.push(dynamicColors());
  }
  return pool;
}

var dynamicColors = function() {
  var r = Math.floor(Math.random() * 255);
  var g = Math.floor(Math.random() * 255);
  var b = Math.floor(Math.random() * 255);
  return "rgb(" + r + "," + g + "," + b + ")";
}

$(".playerAge").each(function() {
  var data = $(this).data('distribution');
  var title = $(this).data('title');
  var labels = data.map(function(value, index) { return value[0]; });
  var ages = data.map(function(value, index) { return value[1]; });

  var myChart = new Chart(this, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
	label: 'Age distribution',
	data: ages,
	backgroundColor: 'rgba(255, 99, 132, 0.2)',
	borderColor: 'rgba(255,99,132,1)',
	borderWidth: 1
      }]
    },
    options: {
      title: {
	display: true,
	position: 'bottom',
	text: title,
      },
      scales: {
	yAxes: [{
	  ticks: {
	    max: 10,
	    min: 0,
	    stepSize: 1,
	  }
	}]
      }
    }
  });
});

$(".playerColleges").each(function() {
  var data = $(this).data('distribution');
  var title = $(this).data('title');
  var labels = data.map(function(value, index) { return value[0]; });
  var colleges = data.map(function(value, index) { return value[1]; });

  var myChart = new Chart(this, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
	label: 'College distribution',
	data: colleges,
	backgroundColor: poolColors(labels.length),
      }]
    },
    options: {
      title: {
	display: true,
	position: 'bottom',
	text: title,
      },
      legend: {
	display: false,
      }
    }
  });
});

$(".playerWeightHeight").each(function() {
  var data = $(this).data('distribution');
  var title = $(this).data('title');

  var myChart = new Chart(this, {
    type: 'bubble',
    data: {
      datasets: [{
	label: 'Weight/height distribution',
	data: data,
	backgroundColor:"#FF6384",
	hoverBackgroundColor: "#FF6384",
      }]
    },
    options: {
      title: {
	display: true,
	position: 'bottom',
	text: title,
      },
    }
  });
});

$(".draftRound").each(function() {
  var data = $(this).data('distribution');
  var title = $(this).data('title');
  var labels = data.map(function(value, index) { return value[0]; });
  var ages = data.map(function(value, index) { return value[1]; });

  var myChart = new Chart(this, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
	label: 'Draft round distribution',
	data: ages,
	backgroundColor: 'rgba(255, 99, 132, 0.2)',
	borderColor: 'rgba(255,99,132,1)',
	borderWidth: 1
      }]
    },
    options: {
      title: {
	display: true,
	position: 'bottom',
	text: title,
      },
      scales: {
	yAxes: [{
	  ticks: {
	    max: 12,
	    min: 0,
	    stepSize: 1,
	  }
	}]
      }
    }
  });
});

$(".playerPoints").each(function() {
  var data = $(this).data('distribution');
  var title = $(this).data('title');
  var labels = data.map(function(value, index) { return value[0]; });
  var avg_points = data.map(function(value, index) { return value[1]; });
  var total_points = data.map(function(value, index) { return value[2]; });

  var myChart = new Chart(this, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
	{
	  label: "Total points",
	  data: total_points,
	  yAxisID: "total",
	  borderColor: 'rgba(0, 183, 238, 1)',
	  borderWidth: 2,
	  fill: false,
	},
	{
	  label: "Points per game",
	  data: avg_points,
	  yAxisID: "average",
	  borderColor: 'rgba(140, 198, 62, 1)',
	  borderWidth: 2,
	  fill: false,
	},
      ]
    },
    options: {
      scales: {
	xAxes: [{
	  ticks: {
	    autoSkip: false,
	    maxRotation: 45,
	    minRotation: 45,
	  }
	}],
	yAxes: [
	  {
	    id: 'average',
	    position: 'right',
	    display: false,
	    ticks: {
	      max: 30,
	      min: 0,
	      stepSize: 5,
	    }
	  },
	  {
	    id: 'total',
	    position: 'left',
	    ticks: {
	      max: 450,
	      min: 0,
	      stepSize: 50,
	    }
	  }
	]
      }
    },
  });
});

$(".adp").each(function() {
  var data = $(this).data('distribution');
  var title = $(this).data('title');
  var labels = data.map(function(value, index) { return value[0]; });
  var adp = data.map(function(value, index) { return value[1]; });
  var dynasty_adp = data.map(function(value, index) { return value[2]; });

  var myChart = new Chart(this, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
	{
	  label: "ADP",
	  data: adp,
	  borderColor: 'rgba(0, 183, 238, 1)',
	  borderWidth: 2,
	  fill: false,
	},
	{
	  label: "Dynasty ADP",
	  data: dynasty_adp,
	  borderColor: 'rgba(255, 99, 132, 1)',
	  borderWidth: 2,
	  fill: false,
	},
      ]
    },
    options: {
      scales: {
	xAxes: [{
	  ticks: {
	    autoSkip: false,
	    maxRotation: 45,
	    minRotation: 45,
	  }
	}],
	yAxes: [
	  {
	    ticks: {
	      max: 180,
	      min: 0,
	      stepSize: 12,
	    }
	  },
	]
      }
    },
  });
});

$(".points").each(function() {
  var data = $(this).data('distribution');
  var title = $(this).data('title');
  var labels = data.map(function(value, index) { return value[0]; });
  var points = data.map(function(value, index) { return value[1]; });
  var averages = data.map(function(value, index) { return value[2]; });
  var maximums = data.map(function(value, index) { return value[3]; });
  var minimums = data.map(function(value, index) { return value[4]; });

  var myChart = new Chart(this, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
	{
	  label: "Points",
	  data: points,
	  borderColor: 'rgba(0, 183, 238, 1)',
	  borderWidth: 2,
	  fill: false,
	},
	{
	  label: "Average",
	  data: averages,
	  pointBackgroundColor: 'rgba(140, 198, 62, 0.5)',
	  pointRadius: 5,
	  showLine: false,
	},
	{
	  label: "Maximum",
	  data: maximums,
	  pointBackgroundColor: 'rgba(255, 99, 132, 0.5)',
	  pointRadius: 3,
	  showLine: false,
	},
	{
	  label: "Minimum",
	  data: minimums,
	  pointBackgroundColor: 'rgba(255, 99, 132, 0.5)',
	  pointRadius: 3,
	  showLine: false,
	},
      ]
    },
    options: {
      title: {
	display: true,
	position: 'top',
	text: title,
      },
      scales: {
	xAxes: [{
	  ticks: {
	    autoSkip: false,
	    maxRotation: 45,
	    minRotation: 45,
	  }
	}],
	yAxes: [
	  {
	    ticks: {
	      max: 200,
	      min: 20,
	      stepSize: 20,
	    }
	  },
	]
      }
    },
  });
});
