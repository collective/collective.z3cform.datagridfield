require([
    'jquery',
    '++resource++collective.z3cform.datagridfield/datagridfield',
], function ($) {
    $(document).ready(function() {
      if ($("body").attr("class").indexOf("datagridfield-initialized") === -1) {
        $("body").addClass("datagridfield-initialized");
        window.dataGridField2Functions.init();
      };
    });
})
