var betas = {},
    symbols = [],
    startDate = null,
    endDate = null;

$("#symbol_input").tokenInput("http://127.0.0.1:5000/companies",
    {
        'minChars': 2,
        'searchDelay': 200,
        'jsonContainer': 'companies',
        'propertyToSearch': 'DISPLAY',
        'theme': 'mac',
        'onAdd': function (item) {
            symbols.push(item.id);
            // if (startDate && endDate) {
            //     getBetas([item.id], startDate, endDate);
            // }
        },
        'onDelete': function (item) {
            var idx = symbols.indexOf(item);
            if (idx > -1){
                symbols.splice(idx, 1);
            }
            removeBeta(item.id);
            removeBeta('Portfolio');
        }
    });

$('#retrieve_button').on('click', function(){
    getBetas();
});

$("#date_range").dateRangePicker({
    autoClose:true,
    startDate: '2007-11-30',
    endDate: '2017-12-20',
    monthSelect: true,
    yearSelect: true,

    setValue: function(s){
        if(!$(this).attr('readonly') && !$(this).is(':disabled') && s != $(this).val()) {
            startDate = s.substr(0, 10);
            endDate = s.substr(-10, 10);
            $(this).val(s);
        }
    }
});

function removeBeta(symbol){
    delete betas[symbol];
    drawChart();
}

function getBetas() {
    var window = $('#window').val();
    data = {'start': startDate,
            'end':endDate,
            'symbols':symbols,
            'window':window};

    $.ajax({
        //TODO replace URL
        url: 'http://127.0.0.1:5000/betas',
        method: 'POST',
        data: data,
        dataType: 'json',
        success: function (response) {
            Object.keys(response).forEach(function(symbol){
               betas[symbol] = response[symbol];
            });
            drawChart();
        }
    });
}


function drawChart() {
    var graphs = [];
    var valueAxes = []

    var chartDataObj = {};


    Object.keys(betas).forEach(function (symbol) {

        Object.keys(betas[symbol]).forEach(function (date) {
            if (!chartDataObj[date]) {
                chartDataObj[date] = {};
            }
            chartDataObj[date][symbol] = betas[symbol][date];
        });


        graphs.push(
            {
                "id": symbol,
                "bullet": "round",
                "bulletBorderAlpha": 1,
                "bulletColor": "#FFFFFF",
                "bulletSize": 1,
                "hideBulletsCount": 50,
                "lineThickness": 2,
                "title": symbol,
                "useLineColorForBulletBorder": true,
                "valueField": symbol
            });

        valueAxes.push({
            "id": symbol,
            "axisAlpha": 0,
            "position": "left",
            "ignoreAxisWidth": true
        });
    });

    var chartData = [];
    Object.keys(chartDataObj).forEach(function (date) {
        var currChange = chartDataObj[date];
        currChange['date'] = date;
        chartData.push(currChange);
    });
    var chart = AmCharts.makeChart("chart_div", {
        "type": "serial",
        "theme": "light",
        "marginRight": 40,
        "marginLeft": 40,
        "autoMarginOffset": 20,
        "mouseWheelZoomEnabled": true,
        "dataDateFormat": "YYYY-MM-DD",
        "legend": {
            "useGraphSettings": true
        },
        "valueAxes": valueAxes,
        "graphs": graphs,
        "chartScrollbar": {
            "graph": "g1",
            "oppositeAxis": false,
            "offset": 30,
            "scrollbarHeight": 80,
            "backgroundAlpha": 0,
            "selectedBackgroundAlpha": 0.1,
            "selectedBackgroundColor": "#888888",
            "graphFillAlpha": 0,
            "graphLineAlpha": 0.5,
            "selectedGraphFillAlpha": 0,
            "selectedGraphLineAlpha": 1,
            "autoGridCount": true,
            "color": "#AAAAAA"
        },
        "chartCursor": {
            "pan": true,
            "valueLineEnabled": true,

            "cursorAlpha": 1,
            "cursorColor": "#258cbb",
            "limitToGraph": "g1",
            "valueLineAlpha": 0.2,
            "valueZoomable": true
        },
        "valueScrollbar": {
            "oppositeAxis": false,
            "offset": 50,
            "scrollbarHeight": 10
        },
        "categoryField": "date",
        "categoryAxis": {
            "parseDates": true,
            "dashLength": 1,
            "minorGridEnabled": true
        },
        "dataProvider": chartData
    });

    chart.addListener("rendered", zoomChart);

    zoomChart();

    function zoomChart() {
        chart.zoomToIndexes(chart.dataProvider.length - 40, chart.dataProvider.length - 1);
    }
}