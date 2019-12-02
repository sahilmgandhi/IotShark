function checkboxOnClick() {
    // "Data Source"
    // map each line to a boolean indicating if it's currently displayed on the graph
    self.graphSelectorStates = {
        'incoming': document.getElementById('incoming').checked,
        'outgoing': document.getElementById('outgoing').checked,
        'udp_incoming': document.getElementById('udp_incoming').checked,
        'udp_outgoing': document.getElementById('udp_outgoing').checked,
        'tcp_incoming': document.getElementById('tcp_incoming').checked,
        'tcp_outgoing': document.getElementById('tcp_outgoing').checked,
        'others_incoming': document.getElementById('others_incoming').checked,
        'others_outgoing': document.getElementById('others_outgoing').checked,
        'http_incoming': document.getElementById('http_incoming').checked,
        'http_outgoing': document.getElementById('http_outgoing').checked,
        'https_incoming': document.getElementById('https_incoming').checked,
        'https_outgoing': document.getElementById('https_outgoing').checked
    };
    updateGraphVisibility();
}

function updateGraphVisibility() {
    // "Presentation"
    // update the graph's visibility settings based on the data source variable
    self.lineChart.data.datasets[0].hidden = !self.graphSelectorStates['incoming'];
    self.lineChart.data.datasets[1].hidden = !self.graphSelectorStates['outgoing'];
    self.lineChart.data.datasets[2].hidden = !self.graphSelectorStates['udp_incoming'];
    self.lineChart.data.datasets[3].hidden = !self.graphSelectorStates['udp_outgoing'];
    self.lineChart.data.datasets[4].hidden = !self.graphSelectorStates['tcp_incoming'];
    self.lineChart.data.datasets[5].hidden = !self.graphSelectorStates['tcp_outgoing'];
    self.lineChart.data.datasets[6].hidden = !self.graphSelectorStates['others_incoming'];
    self.lineChart.data.datasets[7].hidden = !self.graphSelectorStates['others_outgoing'];
    self.lineChart.data.datasets[8].hidden = !self.graphSelectorStates['http_incoming'];
    self.lineChart.data.datasets[9].hidden = !self.graphSelectorStates['http_outgoing'];
    self.lineChart.data.datasets[10].hidden = !self.graphSelectorStates['https_incoming'];
    self.lineChart.data.datasets[11].hidden = !self.graphSelectorStates['https_outgoing'];

    self.lineChart.update();
}

function init() {
    self.graphSelectorStates = {
        'incoming': true,
        'outgoing': true,
        'udp_incoming': false,
        'udp_outgoing': false,
        'tcp_incoming': false,
        'tcp_outgoing': false,
        'others_incoming': false,
        'others_outgoing': false,
        'http_incoming': false,
        'http_outgoing': false,
        'https_incoming': false,
        'https_outgoing': false
    };
}
 
init();
