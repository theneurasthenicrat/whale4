

var url=d3.select("#url_poll").property("value");
var method=d3.select("#method").property("value");

function graph() {

    d3.json(url, function(error, data) {

        d3.select("#controlApproval").style("visibility","hidden");
        method= parseInt(method);

        switch(method) {
            case 1:
                scoring_plot(data.scoring);
                break;
            case 2:
                condorcet_plot(data.condorcet);
                break;

            case 3:
                runoff_plot(data.runoff);
                break;
            case 4:
                randomized(data.randomized);

        }
    });
}



graph();

d3.select("#option").on("change", graph);

d3.select("#approval").on("change", graph);

d3.select(window).on('resize', graph);



