

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

function scoring_plot(scoring) {
    var option= d3.select("#option").node().value;
    var data;
    switch(option) {
        case 'borda':
            data = scoring.borda;
            break;
        case 'plurality':
            data = scoring.plurality;
            break;
        case 'veto':
            data = scoring.veto;
            break;
        case 'approval':
            d3.select("#controlApproval").style("visibility","visible");
            var approval_select= d3.select("#approval")
                .selectAll("option")
                .data(scoring.approval.threshold)
                .enter().append("option")
                .attr("value",function(d,i) { return i; })
                .text(function(d) { return d; });

            var i= d3.select("#approval").node().value;

            data = scoring.approval.scores[i];
            break;
        case 'curvea':
            data = scoring.plurality;
    }
    var margin = {top: 20, right: 20, bottom: 60, left: 40},
        width  = $("#graph").width()-margin.right-margin.left,
        height = window.innerHeight/1.4;


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
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "start")
        .attr("dx", "1.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(30)");

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Scores");



    svg.select('.x.axis').transition().duration(750).call(xAxis);
    svg.select(".y.axis").transition().duration(750).call(yAxis);

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
        .attr("y", function(d) { return y(d.y); })
        .attr("fill",function(d) { return color(d.y); })
        .attr("height", function(d) { return height - y(d.y); });

    bars.enter().append("text")
        .attr("x", function(d) { return x(d.x)+ x.rangeBand()/2; })
        .attr("y", function(d) { return y(d.y)+10; })
        .attr("text-anchor", "middle")
        .attr("dy", "-1em")
        .attr("fill",function(d) { return color(d.y); })
        .style("font-weight","bold")
        .text( function(d) { return d.y; });



}

function condorcet_plot(data) {
    var margin = {top:80, right: 10, bottom: 20, left: 80};
    var nodes = data.nodes,
        links = data.links,
        colorTab = ["red", "#e1dd38", "green"],
        width = $("#graph").width()/2,
        height = window.innerHeight / 1.4,
        width1 = width-margin.right-margin.left,
        height1 = width-margin.right-margin.left,
        minNodeValue = d3.min(nodes, function (d) {
            return d.value;
        }),
        meanNodeValue = d3.mean(nodes, function (d) {
            return d.value;
        }),
        maxNodeValue = d3.max(nodes, function (d) {
            return d.value;
        });

    var color = d3.scale.linear()
        .domain([minNodeValue, meanNodeValue, maxNodeValue])
        .range(colorTab);




    var maxLinkValue = d3.max(links, function (d) {
        return d.value;
    });


    var x = d3.scale.ordinal().rangeBands([0, width1-margin.right-margin.left]),
        z = d3.scale.linear().domain([0, 4]).clamp(true);


    var color1 = d3.scale.linear()
        .domain([-maxLinkValue, 0, maxLinkValue])
        .range(["red", "#e1dd38", "green"]);

    var matrix = [],
        n = nodes.length;


    var i;

    for (i = 0; i < nodes.length; i++) {
        matrix[i] = d3.range(n).map(function (j) {
            return {x: j, y: i, z: 0};
        });
    }


    // Convert links to matrix; count character occurrences.
    links.forEach(function (link) {
        matrix[link.source][link.target].z = link.value;
        matrix[link.target][link.source].z = 0 - link.value;

    });


    // The default sort order.
    x.domain(d3.range(n));

    var force = d3.layout.force()
        .nodes(d3.values(nodes))
        .links(links)
        .size([width, height])
        .linkDistance(width / 1.5)
        .charge(-50)
        .on("tick", tick)
        .start();
    d3.selectAll("svg").remove();
    var svg = d3.select("#graph").append("svg")
        .attr("width", width )
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
        .style("fill", "#ccc")
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
        .attr("r", 16)
        .style("fill", function (d) {
            return color(d.value);
        })
        .style("stroke", "#fff")
        .style("stroke-width", 1.5);

    node.append("text")
        .attr("x", 22)
        .attr("dy", ".35em")
        .style("fill", function (d) {
            return color(d.value);
        })
        .text(function (d) {
            return d.name;
        });

    function tick() {
        path.attr("d", function (d) {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y;

            return "M" +
                d.source.x + "," +
                d.source.y + "L" +
                d.target.x + "," +
                d.target.y;
        });

        node
            .attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
    }

    var matrixSvg = d3.select("#graph").append("svg")
        .attr("width", width1 )
        .attr("height", height1 + margin.top + margin.bottom)
        .style("margin-left", margin.left + "px")
        .style("margin-top", margin.top + "px")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");




    var row = matrixSvg.selectAll(".row")
        .data(matrix)
        .enter().append("g")
        .attr("class", "row")
        .attr("transform", function (d, i) {
            return "translate(0," + x(i) + ")";
        })
        .each(row);

    row.append("line")
        .attr("x2", width1)
        .style("stroke", "#fff");

    row.append("text")
        .attr("x", -6)
        .attr("y", x.rangeBand() / 5)
        .attr("dy", ".32em")
        .attr("text-anchor", "end")
        .style("fill", function (d, i) {
            return color(nodes[i].value);
        })
        .text(function (d, i) {
            return nodes[i].name;
        });

    var column = matrixSvg.selectAll(".column")
        .data(matrix)
        .enter().append("g")
        .attr("class", "column")
        .attr("transform", function (d, i) {
            return "translate(" + x(i) + ")rotate(-90)";
        });

    column.append("line")
        .attr("x1", -width1)
        .style("stroke", "#fff");

    column.append("text")
        .attr("x", 6)
        .attr("y", x.rangeBand() / 5)
        .attr("dy", ".32em")
        .attr("text-anchor", "start")
        .style("fill", function (d, i) {
            return color(nodes[i].value);
        })
        .text(function (d, i) {
            return nodes[i].name;
        });

    function row(row) {
        var cell = d3.select(this).selectAll(".cell")
            .data(row)
            .enter().append("rect")
            .attr("class", "cell")
            .attr("x", function (d) {
                return x(d.x);
            })
            .attr("width", x.rangeBand())
            .attr("height", x.rangeBand())
            .style("fill", function (d) {
                return d.z == 0 ? "#ccc" : color1(d.z);
            });

    }

}

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
        height = window.innerHeight/1.4;

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
        .text(function(d, i) {return i == (matrix.length-1) ? "Winner" : "Round " + i;})
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

function randomized(data){
    var treeData = data.list;
    var round=data.round;

    var margin = {top: 20, right: 120, bottom: 20, left: 120},
        width = $("#graph").width() - margin.right - margin.left,
        height = window.innerHeight/1.4- margin.top - margin.bottom;

    var colorRange = d3.scale.category20();

    var i = 0;

    var tree = d3.layout.tree()
        .size([height, width]);

    

    d3.select("svg").remove();
    var svg = d3.select("#graph").append("svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    root = treeData[0];

    update(root);

    function update(source) {

        // Compute the new tree layout.
        var nodes = tree.nodes(root).reverse(),
            links = tree.links(nodes);

        // Normalize for fixed-depth.
        nodes.forEach(function (d) {
            d.y = width-d.depth*width/round;
        });

        // Declare the nodesâ€¦
        var node = svg.selectAll("g.node")
            .data(nodes, function (d) {
                return d.id || (d.id = ++i);
            });

        // Enter the nodes.
        var nodeEnter = node.enter().append("g")
            .attr("class", "node")
            .attr("transform", function (d) {
                return "translate(" +  (d.y) + "," +  (d.x) + ")";
            });



        nodeEnter.append("circle")
            .attr("r", 10)
            .style("fill", function (d) {return colorRange(d.name);})
            .style("stroke", function (d) {return colorRange(d.name);});

        nodeEnter.append("text")
            .attr("x", 0)
            .attr("y",-20)
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .text(function (d) {return d.name;})
            .style("fill", function (d) {return colorRange(d.name);});

        nodeEnter.append("text")
            .attr("x", width/(round*2)-10)
            .attr("y",-10)
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .text(function (d) {return d.diff;})
            .style("fill", function (d) {return colorRange(d.name);});


        var link = svg.selectAll("path.link")
            .data(links, function (d) {
                return d.target.id;
            });


        link.enter().insert("path", "g")
            .attr("class", "link")
            .attr("d", elbow);

        function elbow(d, i) {
            return "M" + d.target.y + "," + d.target.x
                + "H" + (d.source.y-width/(round*2)) + "V" + d.source.x + "H" + d.source.y
                + (d.source.children ? "" : "h" + margin.right);
        }
    }

}
