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
  data = JSON.parse(data.replace(/\(/g, "[").replace(/\)/g, "]"));
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

$(".playerAvgPoints").each(function() {
  var data = $(this).data('distribution');
  var title = $(this).data('title');
  var labels = data.map(function(value, index) { return value[0]; });
  var points = data.map(function(value, index) { return value[1]; });

  var myChart = new Chart(this, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
	label: title,
	data: points,
	backgroundColor: 'rgba(255, 99, 132, 0.2)',
	borderColor: 'rgba(255,99,132,1)',
	borderWidth: 1
      }]
    },
    options: {
      scales: {
	xAxes: [{
	  ticks: {
	    autoSkip: false
	  }
	}],
	yAxes: [{
	  ticks: {
	    max: 18,
	    min: 0,
	    stepSize: 1,
	  }
	}]
      }
    },
  });
});
