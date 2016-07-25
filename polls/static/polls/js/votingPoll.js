 $(document).ready(function() {
  var today = new Date();
  $('.datepicker').datepicker( {
      format: 'yyyy-mm-dd',
      todayHighlight: true,
      startDate: today,
      autoclose: true,
      orientation: "bottom auto",
      
  });
     $("[name='option_choice']").bootstrapSwitch();
         $("[name='option_modify']").bootstrapSwitch();

});