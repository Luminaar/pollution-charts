function titleText(from, to, data) {
  var suffix
  if (from == to) suffix = `v roce ${from}`
  else suffix = `v letech ${from}-${to}`

  var sum = data.datasets[0].data.reduce((a, b)=>a + b, 0)

  return `Počty měření podle typu emisí, ${suffix} (celkem ${sum} měření)`
}

function createChart(data) {

  const urlParams = new URLSearchParams(window.location.search);
  year_from = urlParams.has("year_from") ? urlParams.get("year_from") : 2004
  year_to = urlParams.has("year_to") ? urlParams.get("year_to") : 2012
  console.log(year_from)
  console.log(year_to)


  var ctx = document.getElementById("myChart").getContext('2d');
  var myChart = new Chart(ctx, {
      type: "pie",
      data: data,
      options: {
        maintainAspectRation: false,
        title: {
          display: true,
          text: titleText(year_from, year_to, data),
          fontSize: 18
        },
        legend: {
          "position": "right",
        },
    }
  });
};


function runChart() {
  const urlParams = new URLSearchParams(window.location.search);
  year_from = urlParams.has("year_from") ? urlParams.get("year_from") : 2004
  year_to = urlParams.has("year_to") ? urlParams.get("year_to") : 2012
  chemical = urlParams.get("chemical")

  if (chemical) {
    fetch(`/api/chemical/${chemical}?year_from=${year_from}&year_to=${year_to}`)
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        createChart(data)
      });
  }
}
