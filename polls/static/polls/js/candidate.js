 $(document).ready(function() {
    var nbCandidates =$("#list_cand").children().length+1;
    // $("label[for='id_form-0-candidate']").append(" "+nbCandidates);
    $('#add_more').click(function() {
        var form_idx = $('#id_form-TOTAL_FORMS').val();
        $('#form_set').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
        $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);

    });
  update();

function update(){
    var formtotal=$('#id_form-TOTAL_FORMS').val();
    var i;
   for (i=0; i < parseInt(formtotal); i++) {
        var labelid= "id_form-0-candidate";
   }
}
new Clipboard('#copy-button');
$('ul.nav.nav-tabs > li > a').click(function(e) {
    e.preventDefault();
    $(this).tab('show');
});

});

