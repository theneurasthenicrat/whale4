var color_palettes = {
    "classical": ["red", "#e1dd38", "green"],
    "grayscale": ["#000", "#444", "#888"]
};


function runoff_plot(runoff) {
    var option= d3.select("#option").node().value;
    var round_text=d3.select("#round").property("value");
    var winner_text=d3.select("#winner").property("value");

    var data;
    var list;
    switch(option) {
        case 'stv':
            data = runoff.stv;
            list = runoff.stv_list;
            break;
        case 'trm':
            data = runoff.trm;
            list = runoff.trm_list;

    }
    var colorTab = color_palettes[d3.select("#palette").node().value],
        width = $("#graph").width()-150,
        height = window.innerHeight/2;

    var matrix = data;
    var color = d3.scale.linear()
        .domain([0,0.5,1])
        .range(colorTab);

    var margin = {top: 20, right: 100, bottom: 20, left: 20};

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
        .text(function(d, i) {return i == (matrix.length-1) ? winner_text : round_text +" "+ (i+1);});


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
        .style("fill",function(d,i,j) {return  d3.min(matrix[j], function (d) {return d.plurality;}) == d3.max(matrix[j], function (d) {return d.plurality;}) ? color(1) :color((d.plurality-d3.min(matrix[j], function (d) {return d.plurality;}))/
            (d3.max(matrix[j], function (d) {return d.plurality;})-d3.min(matrix[j], function (d) {return d.plurality;})));})
        .attr("opacity", 0.8);

    insideG
        .append("text")
        .attr("fill", "#fff")
        .attr("font-weight", "bold")
        .attr("text-anchor", "middle")
        .attr("x", 10+cand_width/2)
        .attr("y",cand_height/2)
        .attr("dy", ".35em")
        .text(function(d){return d.letter+" ("+d.plurality+")";});


    matrixSvg.selectAll(".cand")
        .data(list).enter()
        .append("text")
        .attr("fill", "black")
        .attr("font-weight", "bold")
        .attr("text-anchor", "start")
        .attr("x", 0)
        .attr("y",10)
        .attr("transform", function(d, j) {return "translate(" + (width) + "," + (j*height/n)+ ")"; })
        .attr("dy", ".35em")
        .attr("class",'cand')
        .text(function(d){return d.letter+": "+d.name;})
        .call(wrap,margin.right);

}
