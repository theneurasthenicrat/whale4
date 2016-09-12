function runoff_plot(runoff) {
    var option= d3.select("#option").node().value;
    var data;
    switch(option) {
        case 'stv':
            data = runoff.stv;

            break;
        case 'trm':
            data = runoff.trm;

    }
    var colorTab = [ "green","#e1dd38","red"],
        width = $("#graph").width()-50,
        height = window.innerHeight/2;

    var matrix = data;
    var color = d3.scale.linear()
        .domain([0,0.5,1])
        .range(colorTab);

    var margin = {top: 20, right: 20, bottom: 20, left: 20};


    var x = d3.scale.ordinal().rangeBands([0, width]);
    x.domain(d3.range(matrix.length));

    var y = d3.scale.ordinal().rangeBands([0, height-170]);
    y.domain(d3.range(matrix[0].length));


    d3.selectAll("svg").remove();

    var matrixSvg = d3.select("#graph").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .style("margin-left", margin.left + "px")
        .style("margin-top", margin.top + "px")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var row = matrixSvg.selectAll(".round")
        .data(matrix);

    var roundG = row.enter()
        .append("g")
        .attr("class", "round")
        .attr("id", function(d, i) {return "round" + i;});

    roundG
        .append("rect")
        .attr("y", 0)
        .attr("width",x.rangeBand()-10)
        .attr("height", height)
        .attr("fill", "yellow")
        .attr("opacity", 0.1);

    roundG
        .append("text")
        .attr("x", 0)
        .attr("dy", ".35em")
        .attr("text-anchor", "start")
        .text(function(d, i) {return i == (matrix.length-1) ? "Winner" : "Round " + (i+1);})
        .attr("transform", function(d, j) {return "translate(" + (y.rangeBand()/ 2) + "," + (50 / 2) + ")"; });

    var roundElmt = row.selectAll(".round")
        .data(function(d) {return d;});

    row
        .attr("transform", function(d, i) {return "translate(" + ( x.rangeBand() * i)  + ")"; });

    var insideG = roundElmt.enter()
        .append("g")
        .attr("class", function(d, i) {return "g" + i;});
    var n= matrix[0].length;

    roundElmt
        .attr("transform", function(d, j) {return "translate(" + 0 + "," + (((height-100)/n * j )+100)+ ")"; });

    insideG
        .append("rect")
        .attr("x", "10px")
        .attr("y", "-1em")
        .attr("width", x.rangeBand()-30)
        .attr("height", y.rangeBand())
        .style("fill",function(d, i,j) {return matrix[j].length==1?color(i): color((i)/(matrix[j].length-1));})
        .attr("opacity", 0.8);

    insideG
        .append("text")
        .attr("fill", "#fff")
        .attr("font-weight", "bold")
        .attr("text-anchor", "start")
        .attr("x", x.rangeBand()/6)
        .attr("y", y.rangeBand()/6)
        .attr("dy", ".35em")
        .text(function(d){return d.name;});

}