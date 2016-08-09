


var div_container= d3.select("body").append("div")
                        .attr("class", "container");

div_container.append("div")
                    .attr("class","well")
                    .append("h2").text("sondage title")
                    .append("h3").text("method title");


var div_control= div_container.append("div")
    .attr("class","container-fluid form-group");


div_control.append("label")
    .attr("for","control")
    .attr("class"," col-sm-2 control-label")
    .text("label method");

var div_control_select = div_control.append("div").attr("class", "col-sm-5")
    .append("select")
    .attr("id","control")
    .attr("class"," form-control");

var url=d3.select("#url_poll").property("value");

d3.json(url, function(error, data) {


var dataOptions = data.scoring.candidates;
var options= div_control_select.selectAll("option")
             .data(dataOptions)
             .enter()
             .append("option")
             .text(function(d){return d;});

    });




var btn_back= div_container.append("div")
                .attr("class","margin2")
                .append("a")
                .attr("href","http://127.0.0.1:8000/polls/results/64a72410-1e37-431c-b56f-b5abe56df701" )
                .attr("class","btn btn-custom btn-lg  col-md-3 ")
                .text("Back to all results");