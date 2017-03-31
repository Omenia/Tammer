google.load("visualization", "1", {packages: ["corechart"]});
google.setOnLoadCallback(updateChart);

$.ajaxSetup({ cache: false });

var branches = null;
var branches2 = null;
var additional_data = null;
var chartType = 0;

var options = {
    title: 'Branch risk analysis',
    hAxis: {title: 'Gap', minValue: 0},
    vAxis: {title: 'Inventory', minValue: 0},
    colorAxis: {colors: ['yellow', 'red'], legend: {position: 'bottom'}, maxValue: 10, minValue: 0},
    sizeAxis: {minValue: 5, maxSize: 5},
    chartArea: {
        width: '80%',
        height: '80%',
        backgroundColor: {
            fill: '#E8F9F8'
        }
    },
    bubble: {
        textStyle: {
            fontSize: 12,
            fontName: 'Times-Roman',
            auraColor: 'none'
        }
    }
};

var options2 = {
    title: 'Branch risk analysis',
    hAxis: {title: 'Days since commit'},
    vAxis: {title: 'Gap'},
    colorAxis: {colors: ['yellow', 'red'], legend: {position: 'bottom'}, maxValue: 10, minValue: 0},
    sizeAxis: {minValue: 3, maxSize: 50},
    chartArea: {
        width: '80%',
        height: '80%',
        backgroundColor: {
            fill: '#E8F9F8'
        }
    },
    bubble: {
        textStyle: {
            color: 'none',
            fontSize: 12,
            fontName: 'Times-Roman',
            auraColor: 'none'
        }
    },
    explorer: {
        actions: ['dragToZoom', 'rightClickToReset'],
        axis: 'Both',
        maxZoomOut: 1.5,
        maxZoomIn: 0.1
    }
};

function changeType(t) {
    chartType = t;
    redrawChart();
}

function updateChart() {
    $("#nappula").click(function () {
        var repo_url = $("#repo_url").val();
        console.log("Start analysing repository: " + repo_url);
        var data = {repo_url: repo_url};
        $.ajax({
            url: "/update",
            type: "POST",
            contentType: "application/json",
            dataType: "text",
            processData: false,
            data: JSON.stringify(data),
            success: function (result) {
                console.log("success: " + JSON.stringify(result.responseText));
            },
            error: function (result) {
                console.log("error: " + JSON.stringify(result.responseText));
            },
            complete: function (result) {
                $("#spinner").hide();
                console.log("complete: " + JSON.stringify(result.responseText));
                document.location.href = "index.html";
            }
        });
        $("#spinner").show();
    });

    $.getJSON("data.json", function (data) {
        branches = google.visualization.arrayToDataTable(data.charts.Original);
        branches2 = google.visualization.arrayToDataTable(data.charts.Prototype);
        options.title = options2.title = data.url;
        redrawChart();
    }).error(function() {$("#chartNotFound").show();});
}

function selectHandler() {
    var selectedItem = chart.getSelection()[0];
    if (selectedItem.row != null) {
        //    alert('Last commit by ' + additional_data[selectedItem.row + 1][0] + ', ' + additional_data[selectedItem.row + 1][1]);
    }
}

var chart = null;
function redrawChart() {
    chart = new google.visualization.BubbleChart(document.getElementById('chart'));
    google.visualization.events.addListener(chart, 'select', selectHandler);
    if(chartType == 0) chart.draw(branches, options);
    else if(chartType == 1) chart.draw(branches2, options2);
}

$(document).ready(function () {
    $(window).resize(function () {
        if(chartType == 0) chart.draw(branches, options);
        else if(chartType == 1) chart.draw(branches2, options2);
    });
});
