const getCiambellaOptions = (data, color) => ({
    chart: {
        height: 220,
        type: "radialBar",
    },

    series: data,
    labels: ["Score"], // usa SOLO una volta
    colors: [color],
    plotOptions: getCiambellaPlotOptions(color),

});

const getCiambellaPlotOptions = (color) => ({
radialBar: {
            hollow: {
                margin: 0,
                size: "40%"
            },
            dataLabels: {
                showOn: "always",
                name: {
                    show: true,
                    color: color,
                    fontSize: "1rem",
                    margin: 0,
                    offsetY: -10
                },
                value: {
                    color: color,
                    fontSize: "1.5rem",
                    show: true,
                    offsetY: 5

                }
            }
        }
})

const getBarOptions = (data, labels, color) => ({
    chart: {
        type: 'line',
        height: 100,
        toolbar: { show: false }
    },
    series: [{
        name: 'Valori',
        data: data // i tuoi 5 valori
    }],
    xaxis: {
        categories: labels,
        labels: {
            show: false
        },
        axisBorder: { show: false },
        axisTicks: { show: false }
    },
    yaxis: {
        min: 20,
        max: 35,
        show: false
    },
    grid: {
        show: false
    },
    plotOptions: {
        bar: {
            horizontal: false,
            columnWidth: '4px',
            barHeight: '50%',
            borderRadius: 2
        }
    },
    dataLabels: {
        enabled: false
    },
    colors: [color]
})

let score = []
let bar = []

export const initCharts = (terrario, color, index) => {
    score[index] = new ApexCharts(
        document.querySelectorAll(".score-chart")[index],
        getCiambellaOptions([terrario?.score ?? 0], color)
    );
    score[index].render();
    
    bar[index] = new ApexCharts(
        document.querySelectorAll(".temperature-chart")[index], 
        getBarOptions(
            terrario?.temperatures.map(entry => entry.temperature), 
            terrario?.temperatures.map(entry => entry.timestamp), 
            color)
    );
    bar[index].render();
};

export const buildCharts = (terrario, color, index) => {
    if (!score[index]) return;

    score[index].updateSeries([terrario?.score ?? 0]);
    score[index].updateOptions({
        colors: [color],
        labels: ["Score"], // importante: serve per mostrare il `name`
        plotOptions: getCiambellaPlotOptions(color)
    });    

    const barTimestamps = terrario.temperatures.map(entry => entry.timestamp);
    const barData = terrario.temperatures.map(entry => entry.temperature);
    
    bar[index].updateSeries([{data: barData?? 0}]);
    bar[index].updateOptions({colors: [color], xaxis: {categories: barTimestamps}})

};
