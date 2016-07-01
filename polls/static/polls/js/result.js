$(document).ready(function() {

    var dataJson;

    $.getJSON("http://127.0.0.1:8000/polls/viewPoll/6662c8fa-b5f9-4b5a-84a2-cf4a7caff469?result=scoremethod",  function(data) {
    })
        .done(function(data) {

            var candidates=data.Borda.candidates;
            var borda_scores=data.Borda.scores;
            var plurality_scores=data.Plurality.scores;
            var  veto_scores=data.Veto.scores;
            dataJson={candidates:candidates,Borda:borda_scores,Plurality:plurality_scores,Veto:veto_scores}
            plot_function(dataJson);
        });

    $("#score_method").change(function () {

        plot_function(dataJson);
    })

     $("input[name='plot']").change(function () {

        plot_function(dataJson);
    })

});


function plot_function(dataJson) {
    var method = $("#score_method option:selected").val();
    var plot =$("input[name='plot']:checked").val();
    var scores;
    var name;
    var candidates=dataJson.candidates;
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
            scores = dataJson.Plurality;

    }

    var data = [
        {
            x:candidates,
            y:scores,
            type: 'bar'
        }
    ];
    var annotationContent = [];
    layout = {
        title: name,
        annotations: annotationContent
    };

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

    var h4 = [{
        values: scores,
        labels: candidates,
        type: 'pie'
    }];

    var layout1 = {
        height: 400,
        width: 500
    };
    if (plot=="bar"){
        Plotly.newPlot('myDiv', data,layout);
    }
     else{
         Plotly.newPlot('myDiv', h4,layout1);
    }


}