
function condorcet_plot(data) {
      d3.selectAll("svg").remove();
    d3.select("#controlCondorcet").style("visibility", "visible");

    var option = d3.select("#graph_type").node().value;

    switch (option) {
        case 'node':

            nodes_links(data);
            break;
        case 'matrix':

            matrix_graph(data);
    }

}

function nodes_links(data) {
        var margin = {top:80, right: 10, bottom: 20, left: 80};
    var nodes = data.nodes,
        links = data.links,
        colorTab = ["red", "#e1dd38", "green"],
        width =   $("#graph").width()/1.5,
        height = window.innerHeight / 2,

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




    var force = d3.layout.force()
        .nodes(d3.values(nodes))
        .links(links)
        .size([width, width])
        .linkDistance(width/ 2)
        .on("tick", tick)
        .start();

       var svg = d3.select("#graph")
        .append("svg")
        .attr("width", width )
        .attr("height", width);


    svg.append("svg:defs").selectAll("marker")
        .data(["end"])
        .enter().append("svg:marker")
        .attr("id", String)
        .attr("viewBox", "0 0 10 10")
        .attr("refX", 18)
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
        .attr("x", 0)
         .attr("y", -20)
        .attr("dy", ".35em")
        .attr("text-anchor", "middle")
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

}

function matrix_graph(data){

    var margin = {top:80, right: 10, bottom: 20, left: 80};
    var nodes = data.nodes,
        links = data.links,
        colorTab = ["red", "#e1dd38", "green"],
        width =  ( $(window).width()>970) ? $("#graph").width()/2 : $("#graph").width(),
        height = window.innerHeight / 2,
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
        .domain([nodes.length, 5,0])
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






    var matrixSvg = d3.select("#graph")
        .append("svg")
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
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "end")
        .style("fill", function (d, i) {
            return color(i);
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
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "start")
        .style("fill", function (d, i) {
            return color(i);
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
