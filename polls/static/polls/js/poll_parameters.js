 $(document).ready(function() {
  var today = new Date();
  $('.datepicker').datepicker( {
      format: 'yyyy-mm-dd',
      todayHighlight: true,
      startDate: today,
      orientation: "bottom auto",
      
  });
     $("[name='option_choice']").bootstrapSwitch();
         $("[name='option_modify']").bootstrapSwitch();
         $("[name='option_shuffle']").bootstrapSwitch();
         $("[name='option_blocking_poll']").bootstrapSwitch();
         $("[name='status_poll']").bootstrapSwitch();
         $("[name='close_now']").bootstrapSwitch();

});

