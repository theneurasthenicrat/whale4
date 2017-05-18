var color_palettes_weak = {
    "classical": ["red", "#e1dd38", "green"],
    "grayscale": ["#888", "#444", "#000"]
};

var neutral_palettes = {
    "classical": "#3375b3",
    "grayscale": "#000"
}
    

var color_palettes_strong = {
    "classical": ["red", "#e1dd38", "green"],
    "grayscale": ["#fff", "#888", "#000"]
};

var color_palettes_stroke = {
    "classical": function(i) {return "#000";},
    "grayscale": function(i) {return (i <= 0.5 ? "#000" : "#fff");}
}

function condorcet_plot(data) {
    var option = d3.select("#option").node().value;

    switch (option) {
    case 'copeland':
        data.scores = copeland(data);
        break;	
    case 'simpson':
        data.scores = simpson(data);
    }
    condorcet_chart(data);	
}

function simpson(data) {
    scores = data.matrix.map(function(d, i) {
	min = Number.MAX_SAFE_INTEGER;
	for (var k in d) {
	    if (i != k) {
		if (min > d[k]) {
		    min = d[k];
		}
	    }
	}
	return min});
    return scores;
}

function copeland(data) {
    matrix = data.matrix;
    scores = [];
    for (var i in matrix) {
	scores.push(0);
	for (var j in matrix[i]) {
	    if (matrix[i][j] > matrix[j][i]) {
		scores[i]++;
	    }
	    if (i != j && matrix[i][j] == matrix[j][i]) {
		scores[i] += 0.5;
	    }
	}
    }
    return scores;
}


function condorcet_chart(data) {
    d3.selectAll("svg").remove();
    d3.select("#controlCondorcet").style("visibility", "visible");
    var option = d3.select("#graph_type").node().value;

    switch (option) {
        case 'node':
            node_link(data);
            break;
        case 'matrix':
            matrix_graph(data);
    }

}

function node_link(data) {
    var candidates = data.candidates;
    var matrix = data.matrix;
    var scores = data.scores;
    var m = data.nbVoters;
    var n = candidates.length;
    
    var width = $("#graph").width()/1.5;
    var height = window.innerHeight / 2;

    var nodes = candidates.map(function(d, i) {return {"name": d, "value": scores[i]};});
    var links = create_links(matrix);

    var minNodeValue = d3.min(scores);
    var minlinkValue = d3.min(links, function (d) {return d.value;});
    var meanNodeValue = d3.mean(scores);
    var maxNodeValue = d3.max(scores);
    var maxlinkValue = d3.max(links, function (d) {return d.value;});
    var color = d3.scale.linear().domain([minNodeValue, meanNodeValue, maxNodeValue]).range(color_palettes_weak[d3.select("#palette").node().value]);
    var strokeRange = d3.scale.linear().domain([minlinkValue, maxlinkValue]).range([0.5,3]);
    
    var force = d3.layout.force()
        .nodes(nodes)
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
        .text(function (d) {return d.name+" ("+d.value+")";});

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

function create_links(matrix) {
    links = [];
    for (var i  = 0; i < matrix.length; i++) {
	for (var j = i + 1; j < matrix[i].length; j++) {
	    if (matrix[i][j] > matrix[j][i]) {
		links.push({"source": i, "target": j, value: matrix[i][j] - matrix[j][i]});
	    } else {
		links.push({"source": j, "target": i, value: matrix[j][i] - matrix[i][j]});
	    }
	}
    }
    console.log(links);
    return links;
}

function matrix_graph(data){
    var candidates = data.candidates;
    var matrix = data.matrix;
    var scores = data.scores;
    var m = data.nbVoters;
    var n = candidates.length;

    var margin = {top:100, right: 10, bottom: 10, left: 100};
    var init_graph_width =  $("#graph").width() - 20;
    var init_graph_height = $(window).height() - 40 - 60 - $(".polltitle").height();
    var smallest_dim = init_graph_width < init_graph_height ? init_graph_width : init_graph_height;
    var width = smallest_dim - margin.right - margin.left;
    var height = smallest_dim - margin.top - margin.bottom;
    var duel_text=d3.select("#duel_text").property("value");
    
    var orders = d3.range(n).sort(function(a, b) { return data.scores[b] - data.scores[a]; });
    orders.push(n); // We do this because we need another column for the scores...
    var color_scores = d3.scale.linear().domain([d3.min(data.scores),d3.mean(data.scores),d3.max(data.scores)]).range(color_palettes_weak[d3.select("#palette").node().value]);
    var color_majority = d3.scale.linear().domain([0, m / 2, m]).range(color_palettes_strong[d3.select("#palette").node().value]);
    var color_neutral = neutral_palettes[d3.select("#palette").node().value];
    var stroke = function(i) {return color_palettes_stroke[d3.select("#palette").node().value](d3.scale.linear().domain([0, m]).range([0, 1])(i));};
    console.log(stroke(d3.min(data.scores)));
    var x = d3.scale.ordinal().rangeBands([0, smallest_dim-margin.right-margin.left]).domain(orders);
    var z = d3.scale.linear().domain([0, 4]).clamp(true);
    
    var svg = d3.select("#graph")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .style("margin", "10px")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var row = svg.selectAll(".row")
        .data(data.matrix)
        .enter().append("g")
        .attr("class", "row")
        .attr("transform", function (d, i) {return "translate(0," + x(i) + ")";})
        .each(row);

    row.append("rect")
        .attr("x",n*x.rangeBand()+1)
        .attr("y", 0)
	.transition()
        .attr("width", x.rangeBand())
        .attr("height", x.rangeBand())
    	.style("stroke", "#fff")
        .style("stroke-width", function(d) {return x.rangeBand() > 25 ? "2" : "0";})
        .style("fill", color_neutral);

    row.append("text")
        .attr("x", -6)
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "end")
        .style("fill", function (d, i) {return color_scores(data.scores[i]);})
        .text(function (d, i) {return (x.rangeBand() < 64 && candidates[i].length > 10) ? (candidates[i].slice(0,10) + " [...]") : candidates[i];})
        .call(wrap, margin.left - 5);
    
    row.append("text")
        .attr("x",n*x.rangeBand()+(x.rangeBand() / 2))
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "middle")
	.transition()
        .style("fill", "#fff")
        .text(function (d, i) {return x.rangeBand() > 18 ? data.scores[i] : "";});

    
    var column = svg.selectAll(".column")
        .data(data.matrix)
        .enter().append("g")
        .attr("class", "column")
        .attr("transform", function (d, i) {return "translate(" + x(i) + ")rotate(-90)";});

    column.append("text")
        .attr("x", 6)
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "start")
        .style("fill", function (d, i) {return color_scores(data.scores[i]);})
        .text(function (d, i) {return (x.rangeBand() < 64 && candidates[i].length > 10) ? (candidates[i].slice(0,10) + " [...]") : candidates[i];})
        .call(wrap, margin.top - 5);
    
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y",n*x.rangeBand()+(x.rangeBand() / 2))
        .attr("x",6)
        .attr("dy", ".32em")
        .style("text-anchor", "start")
        .text(duel_text);

    function row(row, i) {
        var cell = d3.select(this).selectAll(".cell")
            .data(row)
            .enter().append("g");

        cell.append("rect")
            .attr("class", "cell")
	    .transition()
	    .attr("x", function (d, j) {return x(j);})
            .attr("width", x.rangeBand())
            .attr("height", x.rangeBand())
	    .style("stroke", "#fff")
            .style("stroke-width", function(d) {return x.rangeBand() > 25 ? "2" : "0";})
            .style("fill", function (d, j) {return i == j ? "#ccc" : color_majority(d);});

        cell.append("text")
            .attr("x", function (d, j) {return x(j)+x.rangeBand() / 2;})
            .attr("y", x.rangeBand() / 2)
            .attr("dy", ".32em")
            .attr("text-anchor", "middle")
	    .transition()
            .style("fill", function(d, i) {return stroke(d);})
            .text(function (d) {return x.rangeBand() > 18 ? d : "";});
    }
}
