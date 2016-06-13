
 $(function() {
             var LI_POSITION = 'li_position';

    $( "#sortable" ).sortable({

            update: function(event, ui) {

              var order = [];
               $('#sortable li').each( function(e) {

              order.push( $(this).attr('id')  + '=' + ( $(this).index() + 1 ) );
              });
              var positions = order.join(';')
             alert(positions);

            }
        });

    $( "#sortable" ).disableSelection();




  });