function createChart(data) {
  var urlParams = new URLSearchParams(location.search);
  var chartType = urlParams.has("chart_type") ? urlParams.get("chart_type") : "bar";
  var stacked = chartType === "line" ? true : false;
  var fun = urlParams.has("fun") ? urlParams.get("fun") : "mean"

  aggregators = {
    "len": {"unit": "Hlášení", "label": "Počet hlášení"},
    "total": {"unit": "t", "label": "Celkové emise"},
    "mean": {"unit": "t", "label": "Průměrné emise"},
    "median": {"unit": "t", "label": "Medián emisí"},
  }

  var unit = aggregators[fun]["unit"]
  var label = aggregators[fun]["label"]

  var ctx = document.getElementById("myChart").getContext('2d');
  var myChart = new Chart(ctx, {
      type: chartType,
      data: data,
      options: {
        maintainAspectRation: false,
        title: {
          display: true,
          text: `${label} v kraji za rok`,
          fontSize: 18
        },
        scales: {
            yAxes: [{
                stacked: stacked,
                scaleLabel: {
                  display: true,
                  labelString: `${unit} / rok`,
                  fontSize: 16
                },
                ticks: {
                  beginAtZero:true
                }
            }],
            xAxes: [{
                scaleLabel: {
                  display: true,
                  labelString: "Rok",
                  fontSize: 16
                },
            }]
        },
        legend: {
          "position": "right",
        },
    }
  });
};

function runChart() {
  var urlParams = new URLSearchParams(location.search);
  var chemical = urlParams.get("chemical")
  var fun = urlParams.has("fun") ? urlParams.get("fun") : "mean"

  if (chemical) {
    fetch(`/api/by-regions/${chemical}?fun=${fun}`)
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        createChart(data)
      });
  }
}
