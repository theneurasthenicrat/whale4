function scoring_plot(scoring) {
     d3.select("#controlApproval").style("visibility","hidden");
    var option = d3.select("#option").node().value;
    var data;
    switch (option) {
        case 'borda':
            data = scoring.borda;
            bar_char(data);
            break;
        case 'plurality':
            data = scoring.plurality;
            bar_char(data);
            break;
        case 'veto':
            data = scoring.veto;
            bar_char(data);
            break;
        case 'approval':
            d3.select("#controlApproval").style("visibility", "visible");
            var theMiddle = Math.floor(scoring.approval.threshold.length/2);
            var approval_select = d3.select("#approval")
                .selectAll("option")
                .data(scoring.approval.threshold)
                .enter().append("option")
                .attr("value", function (d, i) {
                    return i;
                })
                .attr("selected",function (d, i) {
                    if (i==theMiddle ){return" selected"};
                })
                .text(function (d) {
                    return d;
                });

            var i = d3.select("#approval").node().value;

            data = scoring.approval.scores[i];
            bar_char(data);
            break;
        case 'curvea':
            data = scoring.curve_approval;
           curve_approval(data);

    }
}



 function bar_char(data) {
    var margin = {top: 40, right: 20, bottom: 150, left: 60},
        width  = $("#graph").width()-margin.right-margin.left,
        height = window.innerHeight/2;


    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], .1);

    var y = d3.scale.linear()
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");



    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var color = d3.scale.linear()
        .range(["red", "#e1dd38", "green"]);
     


    d3.select("svg").remove();
    var svg = d3.select("#graph").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    x.domain(data.map(function(d) { return d.x; }));
   var yMax=d3.max(data, function(d) { return d.y });
     var yMin=d3.min(data, function(d) { return d.y });
    y.domain([Math.min(0, yMin),yMax ]);
    color.domain([d3.min(data, function(d) { return d.y; }),d3.mean(data, function(d) { return d.y; }),d3.max(data, function(d) { return d.y; })]);

     
    var bars = svg.selectAll(".bar").data(data)

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
        .attr("height", function(d) { return Math.abs( y(d.y)-y(0 ));})

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
             .attr("transform", function() { return  data[0].y >0 ?"rotate(45)":"rotate(90)"; })
             .style("text-anchor", "start")
             .call(wrap,x.rangeBand());


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


    function wrap(text, width) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split("#").reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        y = text.attr("y"),
        dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
      }
    }
  });
}


 }






function curve_approval(data) {

    var margin = {top: 20, right: 20, bottom: 60, left: 40},
        width  = $("#graph").width()-margin.right-margin.left,
        height = window.innerHeight/2;



// Set the ranges
    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width]);
    var y = d3.scale.linear().range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var color = d3.scale.category10();

    
    
    var line = d3.svg.line()
        .x(function(d) { return x(d.x); })
        .y(function(d) { return y(d.y); })
      .interpolate("basis");

  d3.select("svg").remove();
  var svg = d3.select("#graph").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    

    x.domain(data.map(function(d) { return d.x; }));

    y.domain([0, d3.max(data, function(d) { return d.y; })]);

    // Nest the entries by symbol
    var dataNest = d3.nest()
        .key(function(d) {return d.candidate;})
        .entries(data);

    // Loop through each symbol / key
    dataNest.forEach(function(d,i) {

        svg.append("path")
            .attr("class", "line")
            .attr("d", line(d.values))
            .attr("fill","none")
            .style("stroke",  color(d.key) );

        svg.append("text")
            .attr("x", 10)
            .attr("transform",  "translate(" + x(d.values[d.values.length -1].x) + "," + i*30 + ")" )
            .attr("dy", "0.35em")
            .style("font", "10px sans-serif")
            .style("stroke",  color(d.key) )
            .text( d.key);

    });

    // Add the X Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);


}