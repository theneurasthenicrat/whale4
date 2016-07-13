$(document).ready(function() {
    var dataJson;
    var url_poll =$("#url_poll").val();
    var url=url_poll+"?result=scoremethod";
    $.getJSON(url,  function(data) {
        dataJson=data;
        for( var i = 0 ; i < data.Approval.threshold.length ; i++ ) {
            $("#approval_method").append("<option>"+data.Approval.threshold[i]+"</option>");
        }
          plot_function(dataJson);
    });

    $("#score_method ,#approval_method").change(function () {
        plot_function(dataJson);
    });

    $('#radioBtn a').on('click', function(){
        var sel = $(this).data('title');
        var tog = $(this).data('toggle');
        $('#plot').val(sel);
        plot_function(dataJson);
        $('a[data-toggle="'+tog+'"]').not('[data-title="'+sel+'"]').removeClass('active btn-primary').addClass('notActive btn-default');
        $('a[data-toggle="'+tog+'"][data-title="'+sel+'"]').removeClass('notActive btn-default').addClass('active btn-primary');
    });

});


function plot_function(dataJson) {
    var method = $("#score_method option:selected").val();
    var plot =$("#plot").val();
    var approval = $("#approval_method option:selected").text();
    var scores;
    var name;
    var candidates=dataJson.candidates;
    $("#approval").hide();
    switch (method) {
        case "Borda":
            name="Borda";
            scores = dataJson.Borda;
            break;
        case "Veto":
            name="Veto";
            scores = dataJson.Veto;
            break;
        case "Plurality":
            name="Plurality";
            scores = dataJson.Plurality;
            break;
        case "Approval":
            name="Approval";
            $("#approval").show();
            var i=0;
            while ((dataJson.Approval.threshold[i] !=approval) &&(i < dataJson.Approval.threshold.length)) {
                i=i+1;
            }
            scores = dataJson.Approval.scores[i];
    }

    var data;
    var layout;
    if (plot=="bar"){
        data = [{
            x:candidates,
            y:scores,
            type: plot
        }];
        layout = {
            title: name,
            annotations: annotationContent
        };

        var annotationContent = [];


        for( var i = 0 ; i < candidates.length ; i++ ){
            var result = {
                x: candidates[i],
                y: scores[i],
                text: scores[i],
                xanchor: 'center',
                yanchor: 'bottom',
                showarrow: false
            };
            annotationContent.push(result);
        }

    }
    else{
        var data = [{
            values: scores,
            labels: candidates,
            type: plot
        }];
        layout = {
            height: 400,
            width: 500
        };

    }
    
var d3 = Plotly.d3;

var WIDTH_IN_PERCENT_OF_PARENT = 60,
    HEIGHT_IN_PERCENT_OF_PARENT = 80;


var gd3 = d3.select('body')
    .select('#myDiv')
    .style({
        width: WIDTH_IN_PERCENT_OF_PARENT + '%',
        height: HEIGHT_IN_PERCENT_OF_PARENT + 'vf',

    });

var gd = gd3.node();

Plotly.newPlot(gd, data, layout);

window.onresize = function() {
    Plotly.Plots.resize(gd);
};



}

