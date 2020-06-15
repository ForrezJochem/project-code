let html_slider;
var oldValueX = -1;
var chartNummber = 5;
var counter = 0;
let data0 = [];
let data1 = [];
let data2 = [];
let data3 = [];

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);


const listenToSocket = function () {
  socket.on("B2F_connected", function () {
    console.log("verbonden met de socket");
  });
  socket.on("B2F_verandering_graph_ldr", function (jsonObject) {
    showData(jsonObject);
  });
  socket.on("B2F_verandering_graph_solar", function (jsonObject) {
    showData(jsonObject);
  });
};




const showData = function (data) {
  let converted_labels = [];
  let converted_data = [];
  if (counter < 4) {
    for (const d of data) {
      if (counter == 0){
        data0.push(d.waarde)
      } else if (counter == 1){
        data1.push(d.waarde)
      } else if (counter == 2){
        data2.push(d.waarde)
      } else if (counter == 3){
        data3.push(d.waarde)
        converted_labels.push(d.date)
      };
    };
  }
  counter++
  if (counter == 4) {
    console.log("draw multi")
    counter++
    drawMultiChart(converted_labels, data0, data1, data2, data3)
  }
  if (counter > 5) {
    for (const i of data) {
      converted_labels.push(i.date);
      converted_data.push(i.waarde);
    };
    drawChart(converted_labels, converted_data)
  }
};


const drawChart = function (labels, data) {
  console.log(chartNummber)
  txt = "fout"
  if ((chartNummber == 5) || (chartNummber == 7)) {
    txt = "voltage"
  } else if ((chartNummber == 6) || (chartNummber == 8)) {
    txt = "current"
  } else {
    txt = `ldr${chartNummber}`
  }
  console.log(chartNummber)
  let ctx = document.querySelector(`.js-chart-nummber${chartNummber}`).getContext("2d");
  let config = {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: "waarde: ",
          backgroudColor: "white",
          borderColor: 'rgba(33, 150, 243, 1)',
          data: data,
          fill: false
        }
      ]
    },
    options: {

      title: {
        display: true,
        text: txt
      },
      tooltips: {
        mode: "index",
        intersect: true
      },
      hover: {
        mode: "nearest",
        intersect: true
      },
      scales: {
        xAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: "tijd"
            }
          }
        ],
        yAxes: [
          {
            display: true,
            scaleLabel: {
              display: true,
              labelString: "waarde"
            }
          }
        ]
      }
    }
  };
  chartNummber += 1;
  let myChart = new Chart(ctx, config);
};





const drawMultiChart = function (labels, data0, data1, data2, data3) {
  var ctx = document.querySelector(".js-multi-Chart").getContext("2d");
  console.log(data0)
  console.log(data1)
  console.log(data2)
  console.log(data3)
  console.log(labels)
  let config = {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'ldr 1',
        fill: false,
        backgroundColor: "red",
        borderColor: "red",
        data: data0,
      }, {
        label: 'ldr 2',
        fill: false,
        backgroundColor: "green",
        borderColor: "green",
        data: data1,
      }, {
        label: 'ldr 3',
        fill: false,
        backgroundColor: "blue",
        borderColor: "blue",
        data: data2,
      }, {
        label: 'ldr 4',
        fill: false,
        backgroundColor: "orange",
        borderColor: "orange",
        data: data3,
      }]
    },
    options: {
      responsive: true,
      title: {
        display: true,
        text: 'Chart light ldr'
      },
    }
  };
  let myChart = new Chart(ctx, config);
};




document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  socket.emit("F2B_home_connect")
  listenToSocket();
});
