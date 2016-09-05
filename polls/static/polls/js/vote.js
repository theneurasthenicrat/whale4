
$(function() {
    $('ol#sortable li').hide();


    $('#submit').addClass("disabled");

    var initial_pos=[];

    $( "ul#list_init li" ).each( function( index, element ){
        var id_candidate=  $( this ).attr('id') ;
        var value_candidate=$('#id_value'+id_candidate ).val();
        if (value_candidate!=""){
             initial_pos.push(value_candidate+':'+id_candidate);
        }
    });
    initial_pos.sort().reverse();
        for (i = 0; i < initial_pos.length; i++) {
            var arr = initial_pos[i].split(":");
            var id_candidate = parseInt(arr[1]);
            rank(id_candidate);
        }

   $( "ol#sortable li" ).each( function( i, element ){
      $( this ).css('background-color', color(i));
       
    });



});

var worst = 1;
var nbCandidates =$("#sortable").children().length;
    var colorTab = ["green", "#e1dd38", "red"];
var color = d3.scale.linear().domain([0, (nbCandidates-1) / 2, nbCandidates-1]).range(colorTab);

function valid() {
    if (worst!=nbCandidates+1) {
        $('#submit').addClass("disabled");
    }
    else {
        $('#submit').removeClass("disabled");
    }
}

function rank(n) {
    var unsortedItem=$('#' + n );
    var sortedItem=$('#sorted' + worst);
    var valueItem=$('#id_value' + n);
    unsortedItem.hide();
    sortedItem.html(unsortedItem.html());
    sortedItem.attr('title',n);
    valueItem.val( nbCandidates-worst);
    sortedItem.show();
    worst++;
    valid();
}


function unrank(n) {
    var sortedItem=$('#' + n );
    var title_text=  sortedItem.attr('title');
    var unsortedItem=$('#' +title_text);
    unsortedItem.show();
    var valueItem=$('#id_value' + title_text);
    valueItem.val('');
    var arr =n.split("d");
    var pos= parseInt(arr[1]);
    var i;
    for (i=pos+1; i < worst; i++) {
        var sortedNext=$('#sorted' + i );
        var valueItemNext=$('#id_value' + sortedNext.attr('title'));
        valueItemNext.val(nbCandidates-i+1);
        sortedItem.html(sortedNext.html());
        sortedItem.attr('title',sortedNext.attr('title'));
        sortedItem=sortedNext;
    }
    sortedItem.html('');
    sortedItem.attr('title','');
    sortedItem.hide();
    worst--;
    valid();
}


