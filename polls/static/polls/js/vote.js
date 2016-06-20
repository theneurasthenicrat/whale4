
 $(function() {
$('ol#sortable li').hide();
});

 var worst = 1;
 var nbCandidates =$("#sortable").children().length;
 function rank(n) {
     var unsortedItem=$('#' + n );
     var sortedItem=$('#sorted' + worst);
     var valueItem=$('#id_value' + n);
     unsortedItem.hide();
     sortedItem.html(unsortedItem.html());
     sortedItem.attr('title',n);
     valueItem.val( nbCandidates-worst+1);
     sortedItem.show();
     worst++;
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
        valueItemNext.val(nbCandidates-i+2);
       sortedItem.html(sortedNext.html());
        sortedItem.attr('title',sortedNext.attr('title'));
        sortedItem=sortedNext;
    }
    sortedItem.html('');
    sortedItem.attr('title','');
    sortedItem.hide();
    worst--;
}


