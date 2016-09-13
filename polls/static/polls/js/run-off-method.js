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

    var n= matrix[0].length;
    var round= matrix.length;
     var padding_round=10;
     var padding_cand=10;
     var padding_cand_round=10;
     var margin_text_round=15;
     var margin_text=50;
     var round_step=(width/round)-padding_round;
     var cand_width=(round_step-padding_round)-padding_cand_round;
     var cand_height=((height-margin_text)/n)-padding_cand;
     var cand_height_padding=((height-margin_text)/n);


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
        .attr("width",round_step)
        .attr("height", height)
        .attr("fill", "#cccccc")
        .attr("opacity",0.5);


    roundG
        .append("text")
        .attr("x",round_step/2 )
         .attr("y",margin_text_round)
        .attr("dy", ".35em")
        .attr("text-anchor", "middle")
        .text(function(d, i) {return i == (matrix.length-1) ? "Winner" : "Round " + (i+1);});


    var roundElmt = row.selectAll(".round")
        .data(function(d) {return d;});

    row
        .attr("transform", function(d, i) {return "translate(" + ( (width/round) * i)  + ")"; });

    var insideG = roundElmt.enter()
        .append("g")
        .attr("class", function(d, i) {return "g" + i;});


    roundElmt
        .attr("transform", function(d, j) {return "translate(" + 0 + "," + (margin_text+(cand_height_padding*j))+ ")"; });

    insideG
        .append("rect")
        .attr("x", "10px")
        .attr("width",cand_width)
        .attr("height",cand_height)
        .style("fill",function(d, i,j) {return matrix[j].length==1?color(i): color((i)/(matrix[j].length-1));})
        .attr("opacity", 0.8);

    insideG
        .append("text")
        .attr("fill", "#fff")
        .attr("font-weight", "bold")
        .attr("text-anchor", "middle")
        .attr("x", cand_width/2)
        .attr("y",cand_height/2)
        .attr("dy", ".35em")
        .text(function(d){return d.name+" ("+d.plurality+")";});

}