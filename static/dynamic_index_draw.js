$(document).ready(function () {

    const config = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                    label: "Overall Incoming Bytes",
                    backgroundColor: 'rgb(99, 255, 99)',
                    borderColor: 'rgb(99, 255, 99)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['incoming']
                },
                {
                    label: "Overall Outgoing Bytes",
                    backgroundColor: 'rgb(56, 22, 247)',
                    borderColor: 'rgb(56, 22, 247)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['outgoing']
                },
                {
                    label: "UDP Incoming Bytes",
                    backgroundColor: 'rgb(1, 197, 139)',
                    borderColor: 'rgb(1, 197, 139)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['udp_incoming']
                },
                {
                    label: "UDP Outgoing Bytes",
                    backgroundColor: 'rgb(161, 89, 249)',
                    borderColor: 'rgb(161, 89, 249)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['udp_outgoing']
                },
                {
                    label: "TCP Incoming Bytes",
                    backgroundColor: 'rgb(255, 150, 80)',
                    borderColor: 'rgb(255, 150, 80)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['tcp_incoming']
                },
                {
                    label: "TCP Outgoing Bytes",
                    backgroundColor: 'rgb(23, 205, 241)',
                    borderColor: 'rgb(23, 205, 241)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['tcp_outgoing']
                },
                {
                    label: "Other Connection Protocol Incoming Bytes",
                    backgroundColor: 'rgb(255, 91, 135)',
                    borderColor: 'rgb(255, 91, 135)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['others_incoming']
                },
                {
                    label: "Other Connection Protocol Outgoing Bytes",
                    backgroundColor: 'rgb(173, 228, 117)',
                    borderColor: 'rgb(173, 228, 117)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['others_outgoing']
                },
                {
                    label: "HTTP Incoming Bytes",
                    backgroundColor: 'rgb(255, 140, 255)',
                    borderColor: 'rgb(255, 140, 255)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['http_incoming']
                },
                {
                    label: "HTTP Outgoing Bytes",
                    backgroundColor: 'rgb(254, 196, 73)',
                    borderColor: 'rgb(254, 196, 73)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['http_outgoing']
                },
                {
                    label: "HTTPS Incoming Bytes",
                    backgroundColor: 'rgb(88, 99, 249)',
                    borderColor: 'rgb(88, 99, 249)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['https_incoming']
                },
                {
                    label: "HTTPS Outgoing Bytes",
                    backgroundColor: 'rgb(237, 75, 52)',
                    borderColor: 'rgb(237, 75, 52)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-left",
                    hidden: !self.graphSelectorStates['https_outgoing']
                },
                {
                    label: "Is the User Talking to the Voice Assistant?",
                    backgroundColor: 'rgb(225, 141, 94)',
                    borderColor: 'rgb(225, 141, 94)',
                    data: [],
                    fill: false,
                    yAxisID: "y-axis-right"
                }
            ],
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Bytes Sent by Device'
            },
            legend: {
                labels: {
                    filter: function (legendItem, chartData) {
                        return !legendItem.hidden; // return false to hide the label
                    }
                }
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Time (s)'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Bytes',
                    },
                    id: 'y-axis-left',
                    position: 'left'
                }, {
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Is the User Talking to the Assistant?',
                    },
                    id: 'y-axis-right',
                    position: 'right',
                    ticks: {
                        suggestedMin: 0,
                        suggestedMax: 1,
                        stepSize: 1
                    }
                }]
            }
        }
    };

    const context = document.getElementById('canvas').getContext('2d');

    self.lineChart = new Chart(context, config);

    // User States at the current moment
    let user_speaking = 0;

    // Packetdump Data
    const source_packetdump = new EventSource("/chart-data");

    source_packetdump.onmessage = function (event) {
        const data = JSON.parse(event.data);
        config.data.labels.push(data.time);
        config.data.datasets[0].data.push(data.incoming_bytes);
        config.data.datasets[1].data.push(data.outgoing_bytes);
        config.data.datasets[2].data.push(data.udp_incoming_bytes);
        config.data.datasets[3].data.push(data.udp_outgoing_bytes);
        config.data.datasets[4].data.push(data.tcp_incoming_bytes);
        config.data.datasets[5].data.push(data.tcp_outgoing_bytes);
        config.data.datasets[6].data.push(data.others_incoming_bytes);
        config.data.datasets[7].data.push(data.others_outgoing_bytes);
        config.data.datasets[8].data.push(data.http_incoming_bytes);
        config.data.datasets[9].data.push(data.http_outgoing_bytes);
        config.data.datasets[10].data.push(data.https_incoming_bytes);
        config.data.datasets[11].data.push(data.https_outgoing_bytes);
        config.data.datasets[12].data.push(user_speaking);
        self.lineChart.update();

        document.getElementById('cumulative_total_bytes').innerHTML = data.cumulative_total_bytes;
        document.getElementById('cumulative_incoming_bytes').innerHTML = data.cumulative_incoming_bytes;
        document.getElementById('cumulative_outgoing_bytes').innerHTML = data.cumulative_outgoing_bytes;
        document.getElementById('cumulative_udp_incoming_bytes').innerHTML = data.cumulative_udp_incoming_bytes;
        document.getElementById('cumulative_udp_outgoing_bytes').innerHTML = data.cumulative_udp_outgoing_bytes;
        document.getElementById('cumulative_tcp_incoming_bytes').innerHTML = data.cumulative_tcp_incoming_bytes;
        document.getElementById('cumulative_tcp_outgoing_bytes').innerHTML = data.cumulative_tcp_outgoing_bytes;
        document.getElementById('cumulative_others_incoming_bytes').innerHTML = data.cumulative_others_incoming_bytes;
        document.getElementById('cumulative_others_outgoing_bytes').innerHTML = data.cumulative_others_outgoing_bytes;
        document.getElementById('cumulative_http_incoming_bytes').innerHTML = data.cumulative_http_incoming_bytes;
        document.getElementById('cumulative_http_outgoing_bytes').innerHTML = data.cumulative_http_outgoing_bytes;
        document.getElementById('cumulative_https_incoming_bytes').innerHTML = data.cumulative_https_incoming_bytes;
        document.getElementById('cumulative_https_outgoing_bytes').innerHTML = data.cumulative_https_outgoing_bytes;

    }

    // Userstate Data
    const source_userstate = new EventSource("/user-state-data");

    source_userstate.onmessage = function (event) {
        const data = JSON.parse(event.data);
        user_speaking = data.user_speaking;
    }
});