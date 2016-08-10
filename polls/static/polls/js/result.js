

var url=d3.select("#url_poll").property("value");
var method=d3.select("#method").property("value");

function graph() {
    d3.json(url, function(error, data) {
        d3.select("#controlApproval").style("visibility","hidden");
        method= parseInt(method);
        switch(method) {
            case 1:
                var option= d3.select("#option").node().value;

                var data;
                switch(option) {
                    case 'borda':
                        data = data.scoring.borda;
                        scoring_plot(data);
                        break;
                    case 'plurality':
                        data = data.scoring.plurality;
                        scoring_plot(data);
                        break;
                    case 'veto':
                        data = data.scoring.veto;
                        scoring_plot(data);
                        break;
                    case 'approval':
                        d3.select("#controlApproval").style("visibility","visible");
                        var approval_select= d3.select("#approval")
                            .selectAll("option")
                            .data(data.scoring.approval.threshold)
                            .enter().append("option")
                            .attr("value",function(d,i) { return i; })
                            .text(function(d) { return d; });

                        var i= d3.select("#approval").node().value;

                        data = data.scoring.approval.scores[i];
                        scoring_plot(data);
                        break;
                    default:
                        data = data.scoring.plurality;
                        scoring_plot(data);
                }

                break;


            case 2:
                var data = data.condorcet;
                condorcet_plot(data);

                break;

            default:

        }




    });
}


graph();

d3.select("#option").on("change", graph);

d3.select("#approval").on("change", graph);

function scoring_plot(data) {
    var margin = {top: 20, right: 20, bottom: 30, left: 40},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

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
    y.domain([0, d3.max(data, function(d) { return d.y; })]);
    color.domain([d3.min(data, function(d) { return d.y; }),d3.mean(data, function(d) { return d.y; }),d3.max(data, function(d) { return d.y; })]);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Scores");

    var bar= svg.selectAll(".bar")
        .data(data)
        .enter();

    bar.append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return x(d.x); })
        .attr("width", x.rangeBand())
        .attr("y", function(d) { return y(d.y); })
        .attr("fill",function(d) { return color(d.y); })
        .attr("height", function(d) { return height - y(d.y); });

}

function condorcet_plot(data) {
    var nodes = data.nodes,
        links = data.links,
        colorTab = ["red", "#e1dd38", "green"],
        width = 500,
        height = 500,
        width1 = 350,
        height1 = 350,
        minNodeValue = d3.min(nodes, function(d) { return d.value; }),
        meanNodeValue = d3.mean(nodes, function(d) { return d.value; }),
        maxNodeValue = d3.max(nodes, function(d) { return d.value; });

    var color = d3.scale.linear()
        .domain([minNodeValue,meanNodeValue ,maxNodeValue])
        .range(colorTab);

    var margin = {top: 100, right: 20, bottom: 20, left: 100};


    var maxLinkValue = d3.max(links, function(d) { return d.value; });


    var x = d3.scale.ordinal().rangeBands([0, width1]),
        z = d3.scale.linear().domain([0, 4]).clamp(true);




    var color1 = d3.scale.linear()
        .domain([-maxLinkValue,0,maxLinkValue])
        .range(["red", "#e1dd38", "green"]);

    var matrix = [],
        n = nodes.length;



    var i;

    for (i = 0; i < nodes.length;i++) {
        matrix[i] = d3.range(n).map(function(j) { return {x: j, y: i, z: 0}; });
    }


    // Convert links to matrix; count character occurrences.
    links.forEach(function(link) {
        matrix[link.source][link.target].z = link.value;
        matrix[link.target][link.source].z = 0-link.value;

    });



    // The default sort order.
    x.domain(d3.range(n));

    var force = d3.layout.force()
        .nodes(d3.values(nodes))
        .links(links)
        .size([width, height])
        .linkDistance(300)
        .charge(-50)
        .on("tick", tick)
        .start();

    var svg = d3.select("#graph").append("svg")
        .attr("width", width)
        .attr("height", height);

    svg.append("svg:defs").selectAll("marker")
        .data(["end"])
        .enter().append("svg:marker")
        .attr("id", String)
        .attr("viewBox", "0 0 10 10")
        .attr("refX", 20)
        .attr("refY", 5)
        .attr("markerWidth", 10)
        .attr("markerHeight", 10)
        .attr("orient", "auto")
        .style("fill","#ccc")
        .append("svg:path")
        .attr("d", "M 0 0 L 10 5 L 0 10 z");

    var path = svg.append("svg:g").selectAll("path")
        .data(links)
        .enter().append("svg:path")
        .attr("class", "link")
        .attr("stroke-width", 1.5)
        .style("stroke", "#ccc")
        .attr("marker-end", "url(#end)");

    var node = svg.selectAll(".node")
        .data(nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);

    node.append("circle")
        .attr("r",16)
        .style("fill", function(d) { return color(d.value); })
        .style("stroke","#fff")
        .style("stroke-width",1.5);

    node.append("text")
        .attr("x", 22)
        .attr("dy", ".35em")
        .style("fill", function(d) { return color(d.value); })
        .text(function(d) { return d.name; });

    function tick() {
        path.attr("d", function(d) {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y;

            return "M" +
                d.source.x + "," +
                d.source.y + "L" +
                d.target.x + "," +
                d.target.y;
        });

        node
            .attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")"; });
    }

    var matrixSvg = d3.select("#graph").append("svg")
        .attr("width", width1 + margin.left + margin.right)
        .attr("height", height1 + margin.top + margin.bottom)
        .style("margin-left", margin.left + "px")
        .style("margin-top", margin.top + "px")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");




    matrixSvg.append("rect")
        .attr("width", width1)
        .attr("height", height1);

    var row = matrixSvg.selectAll(".row")
        .data(matrix)
        .enter().append("g")
        .attr("class", "row")
        .attr("transform", function(d, i) {  return "translate(0," + x(i) + ")"; })
        .each(row);

    row.append("line")
        .attr("x2", width1)
        .style("stroke","#fff");

    row.append("text")
        .attr("x", -6)
        .attr("y", x.rangeBand() / 5)
        .attr("dy", ".32em")
        .attr("text-anchor", "end")
        .style("fill", function(d,i) { return color(nodes[i].value); })
        .text(function(d, i) { return nodes[i].name; });

    var column = matrixSvg.selectAll(".column")
        .data(matrix)
        .enter().append("g")
        .attr("class", "column")
        .attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-90)"; });

    column.append("line")
        .attr("x1", -width1)
        .style("stroke","#fff");

    column.append("text")
        .attr("x", 6)
        .attr("y", x.rangeBand() / 5)
        .attr("dy", ".32em")
        .attr("text-anchor", "start")
        .style("fill", function(d,i) { return color(nodes[i].value); })
        .text(function(d, i) { return nodes[i].name; });

    function row(row) {
        var cell = d3.select(this).selectAll(".cell")
            .data(row)
            .enter().append("rect")
            .attr("class", "cell")
            .attr("x", function(d) { return x(d.x); })
            .attr("width", x.rangeBand())
            .attr("height", x.rangeBand())
            .style("fill", function(d) { return d.z==0 ?"#ccc" :color1(d.z ); });

    }


}