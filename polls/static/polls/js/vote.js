
 $(function() {

     var nbCandidates = 3;
var worst = 1;
var ranks = [-1, -1, -1];
var origs = [-1, -1, -1];
var vals = [1, 2, 3];
     //var colorTab = ["#b8da40", "#e1dd38", "#c31616"];
//var color = d3.scale.linear().domain([0, nbCandidates / 2, nbCandidates]).range(colorTab);


$('ul#sortable li').hide();
     


  function rank1(n) {
    var unsortedItem = $('#unsorted' + n.toString());
    var sortedItem = $('#sorted' + worst.toString());
    var sortedItemSpan = $('#sorted' + worst + ' span');
    //var option = $('#option' + n);

    sortedItem.attr('title', unsortedItem.attr('title'));
    sortedItemSpan.html(unsortedItem.html());
    sortedItem.css('display', 'block');

    unsortedItem.css('display', 'none');
    unsortedItem.html('');
    unsortedItem.attr('title', '');

   // option.attr('value', vals[worst]);

    origs[worst] = n;
    ranks[n] = worst;
    worst++;

    /*console.log("origs -> " + origs);
    console.log("ranks -> " + ranks);*/
}



     function unrank1(n) {
    var unsortedItem = $('#unsorted' + origs[n]);
    var sortedItem = $('#sorted' + n);
    var sortedItemSpan = $('#sorted' + n + ' span');
    var option = $('#option' + origs[n]);

    unsortedItem.attr('title', sortedItem.attr('title'));
    unsortedItem.html(sortedItemSpan.html());
    unsortedItem.css('display', 'inline-block');

    ranks[origs[n]] = -1;
    next = $('#sorted' + n);
    nextSpan = $('#sorted' + n + ' span');
    for (var i = n + 1; i < worst; i++) {
	origs[i - 1] = origs[i];
	ranks[origs[i - 1]]--;
        $('#option' + origs[i - 1]).attr('value', vals[ranks[origs[i - 1]]]);
	next = $('#sorted' + i);
	nextSpan = $('#sorted' + i + ' span');
	sortedItemSpan.html(nextSpan.html());
	sortedItem.attr('title', next.attr('title'));
	sortedItem = next;
	sortedItemSpan = nextSpan;
    }

    next.css('display', 'none');
    nextSpan.html('');

    option.attr('value', '');

    worst--;
    origs[worst] = -1;

/*    console.log("origs -> " + origs);
    console.log("ranks -> " + ranks);*/
}


});

 var worst = 1;
 function rank(n) {
     var unsortedItem=$('#' + n );
     var sortedItem=$('#sorted' + worst);
     var title_text=  unsortedItem.attr('title');
     unsortedItem.hide();
     sortedItem.html(title_text);
     sortedItem.attr('title',title_text );
     sortedItem.show();
     worst++;
}



function unrank(n) {
    var sortedItem=$('#' + n );
    var title_text=  sortedItem.attr('title');
    var unsortedItem=$('#' +title_text);
    unsortedItem.show();
    var arr =n.split("d");
    var pos= parseInt(arr[1]);
    var i;
    for (i=pos+1; i < worst; i++) {
        var sorted=$('#sorted' + i );
        var title_text2=  sorted.attr('title');
       sortedItem.html(title_text2);
        sortedItem.attr('title',title_text2);
        sortedItem=sorted;
    }
    sortedItem.html('');
    sortedItem.attr('title','');
    sortedItem.hide();
    worst--;
}


