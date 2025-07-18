import { buildCharts, initCharts } from "./chart.js"


let firstTime = [true, true];


const sad = {
  class: "sad",
  color: "#EB5757",
}
const dissatisfied = {
  class: "dissatisfied",
  color: "#F2994A",
}
const neutral = {
  class: "neutral",
  color: "#F2C94C",
}
const satisfied = {
  class: "satisfied",
  color: "#7ED957",
}
const verySatisfied = {
  class: "verySatisfied",
  color: "#27AE60",
}

function getMood(score) {
  if (score < 20) return sad;
  if (score < 40) return dissatisfied;
  if (score < 60) return neutral;
  if (score < 80) return satisfied;
  return verySatisfied;
}

const source = new EventSource('/stream');
// const source = new EventSource('http://localhost:8000/stream');


source.onmessage = function (event) {
  const data = JSON.parse(event.data);
  if (data.errore) {
    document.body.innerHTML += '<p style="color:red;">Errore: ' + data.errore + '</p>';
  } else {
    data.terrari.map(async (terrario, index) => {
      const { color, class: moodClass } = getMood(terrario.score);
      
      // document.querySelectorAll(".box")[index].setAttribute("class", `box ${moodClass}`);

      if (firstTime[index]) {
        initCharts(terrario, color, index);
        firstTime[index] = false;
      } else {
        buildCharts(terrario, color, index);
      }

      document.querySelectorAll(".current-humidity")[index].innerHTML = Math.round(terrario.h).toString() + "%"
      document.querySelectorAll(".current-temperature")[index].innerHTML = Math.round(terrario.t).toString() + "&#8451;"
      document.querySelectorAll(".current-pressure")[index].innerHTML = (Math.round(terrario.p / 10.13) / 100).toString() + "atm"
      // console.log(terrario.wl);
      
      document.querySelectorAll('.ml')[index].setAttribute("style", `--level: ${(Math.round(terrario.ml)).toString()}%`);
      document.querySelectorAll('.ml-label')[index].innerHTML = (Math.round(terrario.ml)).toString() + '%'
      document.querySelectorAll('.wl')[index].setAttribute("style", `--level: ${(Math.round(terrario.wl)).toString()}%`);
      document.querySelectorAll('.wl-label')[index].innerHTML = (Math.round(terrario.wl)).toString() + '%'

    })
  }
};
