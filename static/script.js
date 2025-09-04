// Temperature & Humidity Data (ये बाद में Jinja variables से आएगा)
var tlabels = [
  "Jan","Feb","Mar","Apr","May","Jun",
  "Jul","Aug","Sep","Oct","Nov","Dec"
];
var tvalues = [10, 20, 30, 25, 15, 35, 40, 45, 30, 20, 25, 50];

var hlabels = [
  "Jan","Feb","Mar","Apr","May","Jun",
  "Jul","Aug","Sep","Oct","Nov","Dec"
];
var hvalues = [40, 50, 60, 55, 45, 65, 70, 75, 60, 50, 55, 80];

// Temperature Chart
var ctx = document.getElementById("tlineChart").getContext("2d");
var tlineChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: tlabels,
    datasets: [{
      label: "TEMPERATURE",
      data: tvalues,
      fill: false,
      borderColor: "rgb(75, 192, 192)",
      backgroundColor: "rgb(75, 192, 192)",
      tension: 0.1,
    }],
  },
  options: {
  responsive: false,
  maintainAspectRatio: true ,
  // aspectRatio: 2, // ✅ auto adjust karega
  // plugins: {
  //   legend: { display: true }
  // }
}


});

// Humidity Chart
var ctx2 = document.getElementById("hlineChart").getContext("2d");
var hlineChart = new Chart(ctx2, {
  type: "line",
  data: {
    labels: hlabels,
    datasets: [{
      label: "HUMIDITY",
      data: hvalues,
      fill: false,
      borderColor: "rgb(75, 192, 192)",
      backgroundColor: "rgb(75, 192, 192)",
      tension: 0.1,
    }],
  },
  options: {
  responsive: false,
  maintainAspectRatio: true,
  // aspectRatio: 2, // ✅ auto adjust karega
  // plugins: {
  //   legend: { display: true }
  // }
},



});
