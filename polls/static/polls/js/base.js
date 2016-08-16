$(document).ready(function() {

    $('.dropdown-toggle').dropdown();
    var url = window.location.pathname;
    $('ul.nav a[href="'+ url +'"]').parent().addClass('active');
    $('ul.nav a').filter(function() {
        return this.href == url;
    }).parent().addClass('active');

});