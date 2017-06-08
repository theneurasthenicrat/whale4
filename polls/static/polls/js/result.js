

var url=d3.select("#url_poll").property("value");
var method=d3.select("#method").property("value");
var preference=d3.select("#preference").property("value");
d3.select("#controlApproval").style("visibility","hidden");
d3.select("#controlCondorcet").style("visibility","hidden");
d3.select("#Shuffle_randomized").style("visibility","hidden");


function drawGraph() {
    d3.json(url, function(error, data) {
	d3.select("#waiter").style("display", "none");
	d3.select("#option").on("change", function() {return updateGraph(data);});
	
	d3.select("#approval").on("change", function() {return updateGraph(data);});
	d3.select("#palette").on("change", function() {return updateGraph(data);});
	d3.select("#graph_type").on("change", function() {return updateGraph(data);});
	
	d3.select(window).on('resize', function() {return updateGraph(data);});

	updateGraph(data);
    });
}

function updateGraph(data) {
    method= parseInt(method);
    
    switch(method) {
    case 1:
        if(preference == "Approval") {
            d3.select("#control").style("visibility","hidden");
        }
        scoring_plot(data.scoring);
        break;
    case 2:
        condorcet_plot(data);
        break;
    case 3:
        runoff_plot(data.runoff);
        break;
    case 4:
        randomized(data.randomized);
    }
}

drawGraph();


function wrap(text, width) {
    text.each(function(d) {
        var text = d3.select(this),
	    words = text.text().split(/\s+|[#]/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1, // ems
            y = text.attr("y"),
            x = text.attr("x"),
            dy = parseFloat(text.attr("dy")),
            tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");
	while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
            }
        }
    });
}

function getTextWidth(txt, fontname, fontsize){
  // Create a dummy canvas (render invisible with css)
  var c=document.createElement('canvas');
  // Get the context of the dummy canvas
  var ctx=c.getContext('2d');
  // Set the context.font to the font that you are using
  ctx.font = fontsize + 'px' + fontname;
  // Measure the string 
  // !!! <CRUCIAL>  !!!
  var length = ctx.measureText(txt).width;
  // !!! </CRUCIAL> !!!
  // Return width
  return length;
}
