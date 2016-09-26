
function condorcet_plot( condorcet) {
    var option = d3.select("#option").node().value;
    var data;
    switch (option) {
        case 'copeland0':
            data = condorcet.copeland0;
            condorcet_chart(data);
            break;
        case 'copeland1':
            data =  condorcet.copeland1;
            condorcet_chart(data);
            break;
        case 'simpson':
            data =  condorcet.copeland1;
            condorcet_chart(data);

    }
}



function condorcet_chart(data) {
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

    var nodes = data.nodes,
        links = data.links,
        colorTab = ["red", "#e1dd38", "green"],
        width =   $("#graph").width()/1.5,
        height = window.innerHeight / 2,
        minNodeValue = d3.min(nodes, function (d) {return d.value;}),
        minlinkValue = d3.min(links, function (d) {return d.value;}),
        meanNodeValue = d3.mean(nodes, function (d) {return d.value;}),
        maxNodeValue = d3.max(nodes, function (d) {return d.value;}),
        maxlinkValue = d3.max(links, function (d) {return d.value;}),
        color = d3.scale.linear().domain([minNodeValue, meanNodeValue, maxNodeValue]).range(colorTab)
        strokeRange = d3.scale.linear().domain([minlinkValue, maxlinkValue]).range([0.5,3]);
    
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
        .attr("class", "arrowEndSelected")
        .attr("viewBox", "0 0 10 10")
        .attr("refX", 20)
        .attr("refY", 5)
        .attr("markerUnits", "userSpaceOnUse")
        .attr("markerWidth", 16)
        .attr("markerHeight",16)
        .attr("orient", "auto")
        .style("fill", "#999999")
        .append("svg:path")
        .attr("d", "M 0 0 L 10 5 L 0 10 z");
    
    var path = svg.append("svg:g").selectAll("path")
        .data(links)
        .enter().append("svg:path")
        .attr("class", "link")
        .style("stroke-width", function (d) { return  strokeRange(d.value);})
        .style("stroke-dasharray", function (d) { return "4," + (d.value == 0 ? "4" : "0"); })
        .style("stroke", "#999999")
        .attr("marker-end", function (d) { return  (d.value == 0 ? "" : "url(#end)"); });

    var node = svg.selectAll(".node")
        .data(nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);

    node.append("circle")
        .attr("r", 16)
        .style("fill", function (d) {return color(d.value);})
        .style("stroke", "#fff")
        .style("stroke-width", 1.5);

    node.append("text")
        .attr("x", 0)
        .attr("y", -25)
        .attr("dy", ".35em")
        .attr("text-anchor", "middle")
        .style("fill", function (d) {return color(d.value);})
        .text(function (d) {return d.name+"("+d.value+")";});

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

    var margin = {top:100, right: 10, bottom: 20, left: 100},
        duel_text=d3.select("#duel_text").property("value"),
        nodes = data.nodes,
        matrix = data.matrix,
        n = nodes.length,
        colorTab = ["red", "#e1dd38", "green"],
        width =(( $(window).width()>970) ? $("#graph").width()/1.6 : $("#graph").width())-margin.right-margin.left,
        height = (( $(window).width()>970) ? $("#graph").width()/1.6 : $("#graph").width())-margin.right-margin.left,
        minNodeValue = d3.min(nodes, function (d) {return d.value;}),
        meanNodeValue = d3.mean(nodes, function (d) {return d.value;}),
        maxNodeValue = d3.max(nodes, function (d) {return d.value;}),
        orders = d3.range(n).sort(function(a, b) { return nodes[b].value- nodes[a].value; })
        max = d3.max(matrix.map(function(array) {return d3.max(array, function (d) {return d.z;});})),
        mean = d3.mean(matrix.map(function(array) {return d3.mean(array, function (d) {return d.z;});})),
        min = d3.min(matrix.map(function(array) {return d3.min(array, function (d) {return d.z==0?max:d.z;});})),
        color = d3.scale.linear().domain([minNodeValue,meanNodeValue,maxNodeValue]).range(colorTab),
        x = d3.scale.ordinal().rangeBands([0, width-margin.right-margin.left]).domain(orders),
        z = d3.scale.linear().domain([0, 4]).clamp(true),
        color1 = d3.scale.linear().domain([min, mean, max]).range(colorTab);

    var matrixSvg = d3.select("#graph")
        .append("svg")
        .attr("width", width+margin.left+margin.right )
        .attr("height", height + margin.top + margin.bottom)
        .style("margin-left", margin.left + "px")
        .style("margin-top", margin.top + "px")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    var row = matrixSvg.selectAll(".row")
        .data(matrix)
        .enter().append("g")
        .attr("class", "row")
        .attr("transform", function (d, i) {return "translate(0," + x(i) + ")";})
        .each(row);

    row.append("rect")
        .attr("x",width-margin.left-margin.right+1)
        .attr("y", 0)
        .attr("width", x.rangeBand())
        .attr("height", x.rangeBand())
        .style("fill", "#ccc");

    row.append("line")
        .attr("x2", width-margin.left-margin.right+x.rangeBand())
        .style("stroke","#fff");

    row.append("text")
        .attr("x", -6)
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "end")
        .style("fill", function (d, i) {return color(nodes[i].value);})
        .text(function (d, i) {return nodes[i].name;});


    row.append("text")
        .attr("x",width-margin.left+10)
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "middle")
          .style("fill", "white")
        .text(function (d, i) {return nodes[i].value;});

    var column = matrixSvg.selectAll(".column")
        .data(matrix)
        .enter().append("g")
        .attr("class", "column")
        .attr("transform", function (d, i) {return "translate(" + x(i) + ")rotate(-90)";});

    column.append("line")
        .attr("x1", -(width-margin.top-10))
        .style("stroke","#fff");

    column.append("text")
        .attr("x", 6)
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "start")
        .style("fill", function (d, i) {return color(nodes[i].value);})
        .text(function (d, i) {return nodes[i].name;});

    matrixSvg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y",width-margin.left-margin.right+x.rangeBand() / 2)
        .attr("x",6)
        .attr("dy", ".32em")
        .style("text-anchor", "start")
        .text(duel_text);

    function row(row) {
        var cell = d3.select(this).selectAll(".cell")
            .data(row)
            .enter().append("g");

        cell.append("rect")
            .attr("class", "cell")
            .attr("x", function (d) {return x(d.x);})
            .attr("width", x.rangeBand())
            .attr("height", x.rangeBand())
            .style("fill", function (d) {return d.z == 0 ? "#ccc" : color1(d.z);});

        cell.append("text")
            .attr("x", function (d) {return x(d.x)+x.rangeBand() / 2;})
            .attr("y", x.rangeBand() / 2)
            .attr("dy", ".32em")
            .attr("text-anchor", "middle")
            .style("fill", "white")
            .text(function (d) {return d.z;});


    }

}
