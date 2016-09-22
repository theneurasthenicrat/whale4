function scoring_plot(scoring) {

    d3.select("#controlApproval").style("visibility","hidden");
    var option = d3.select("#option").node().value,
        data;
    switch (option) {
        case 'borda':
            data = scoring.borda;
            bar_chart(data);
            break;
        case 'plurality':
            data = scoring.plurality;
            bar_chart(data);
            break;
        case 'veto':
            data = scoring.veto;
            bar_chart(data);
            break;
        case 'approval':
            d3.select("#controlApproval").style("visibility", "visible");
            var theMiddle = Math.floor(scoring.approval.threshold.length/2);
            d3.select("#approval")
                .selectAll("option")
                .data(scoring.approval.threshold)
                .enter().append("option")
                .attr("value", function (d, i) {return i;})
                .attr("selected",function (d, i) {if (i==theMiddle ){return" selected"};})
                .text(function (d) {return d;});

            var i = d3.select("#approval").node().value;
            data = scoring.approval.scores[i];
            bar_chart(data);
            break;
        case 'curvea':
            data = scoring.curve_approval;
           curve_approval(data);
    }

}


function bar_chart(data) {
    var margin = {top: 40, right: 20, bottom: 150, left: 60},
        width  = $("#graph").width()-margin.right-margin.left,
        height = window.innerHeight/2,
        yMax=d3.max(data, function(d) { return d.y }),
        yMin=d3.min(data, function(d) { return d.y }),
        yMean=d3.mean(data, function(d) { return d.y }),
        x = d3.scale.ordinal().rangeRoundBands([0, width], .1).domain(data.map(function(d) { return d.x; })),
        y = d3.scale.linear().range([height, 0]).domain([Math.min(0, yMin),Math.max(0, yMax) ]),
        xAxis = d3.svg.axis().scale(x).orient("bottom"),
        yAxis = d3.svg.axis().scale(y).orient("left"),
        color = d3.scale.linear().range(["red", "#e1dd38", "green"]).domain([yMin,yMean,yMax]);

    d3.select("svg").remove();

    var svg = d3.select("#graph").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var bars = svg.selectAll(".bar").data(data);

    bars.exit()
        .transition()
        .duration(750)
        .attr("y", y(0))
        .attr("height", height - y(0))
        .style('fill-opacity', 1e-6)
        .remove();

    bars.enter().append("rect")
        .attr("class", "bar")
        .attr("y", y(0))
        .attr("height", height - y(0));

    bars.transition().duration(750)
        .attr("x", function(d) { return x(d.x); })
        .attr("width", x.rangeBand())
        .attr("y", function(d) { return y(Math.max(0, d.y)); })
        .attr("fill",function(d) { return color(d.y); })
        .attr("height", function(d) { return Math.abs( y(d.y)-y(0 ));});

    bars.enter().append("text")
        .attr("x", function(d) { return x(d.x)+ x.rangeBand()/2; })
        .attr("y", function(d) { return  d.y >0 ?y(d.y):y(d.y)+30; })
        .attr("text-anchor", "middle")
        .attr("dy", "-1em")
        .attr("fill",function(d) { return color(d.y); })
        .style("font-weight","bold")
        .text( function(d) { return d.y; });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + y(0) + ")")
        .call(xAxis)
        .selectAll("text")
        .attr("x", 12)
        .attr("y", 0)
        .attr("transform", function() { return  yMin >=0 ?"rotate(45)":"rotate(90)"; })
        .style("text-anchor", "start");


    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x",0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Scores");

}


function curve_approval(data) {
    var approval_text=d3.select("#approval_text").property("value"),
        scores_text=d3.select("#scores_text").property("value"),
        margin = {top: 20, right: 20, bottom: 60, left: 60},
        width  = $("#graph").width()-margin.right-margin.left-140,
        height = window.innerHeight/2,
        x = d3.scale.ordinal().rangeRoundBands([0, width], .1).domain(data.map(function(d) { return d.x; })),
        y = d3.scale.linear().range([height, 0]).domain([0, d3.max(data, function(d) { return d.y; })]),
        xAxis = d3.svg.axis().scale(x).orient("bottom").innerTickSize(-height).outerTickSize(0),
        yAxis = d3.svg.axis().scale(y).orient("left"),
        color = d3.scale.category10(),
        line = d3.svg.line().x(function(d) { return x(d.x)+x.rangeBand()/2; }).y(function(d) { return y(d.y); }).interpolate("monotone");

    d3.select("svg").remove();

    var svg = d3.select("#graph").append("svg")
        .attr("width", width + margin.left + margin.right+140)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var dataNest = d3.nest()
        .key(function(d) {return d.candidate;})
        .entries(data);

    dataNest.forEach(function(d,i) {

        svg.append("path")
            .attr("class", "line")
            .attr("d", line(d.values))
            .attr("fill","none")
            .style("stroke",  color(d.key) );

        svg.append("text")
            .attr("x", 10)
            .attr("transform",  "translate(" +( x(d.values[d.values.length -1].x)+x.rangeBand()/2) + "," + i*30 + ")" )
            .attr("dy", "0.35em")
            .style("fill",  color(d.key) )
            .text( d.key);

    });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x",0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text(scores_text);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    svg.append("text")
        .attr("y", height+margin.bottom/2)
        .attr("x",width/ 2)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text(approval_text);

}