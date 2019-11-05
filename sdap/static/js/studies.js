function ValidationFunction(){
  console.log("Validation");
  if($('.step').find('input[type="checkbox"]:checked').length)
    return true;
  return false;
}

function get_db_studies(destroyFeedback) {
    var checkedValues = $('input:checkbox:checked.checkItems').map(function() { return this.value; }).get();
    $.ajax({
      url: url_getdb_studies,
      type: 'get',
      data: {
        'db_ids': checkedValues
      },
      dataType: 'json',
      success: function (data) {
        $("#table_studies").html(data['table_list']);
        destroyFeedback(true);
      }
    });
}

function get_db_datasets(destroyFeedback) {
  var checkedValues = $('input:checkbox:checked.study').map(function() { return this.value; }).get();
  $.ajax({
    url: url_get_datasets,
    type: 'get',
    data: {
      'db_ids': checkedValues
    },
    dataType: 'json',
    success: function (data) {
      $("#table_analyse").html(data['table_list']);
      destroyFeedback(true);
    }
  });
}

function displayDatasets(study) {
  var checkedValues = $('input:checkbox:checked.dataset').map(function() { return this.value; }).get();
  var checkedStudy = $('input:checkbox:checked.dataset').map(function() { return this.name; }).get();
  document.location.href = url_display_data + "?study_id=" + checkedStudy[0] + "&document_id=" + checkedValues[0];
}


$(function() {

$("#step1").click( function()
    {
      var checkedValues = $('input:checkbox:checked.checkItems').map(function() { return this.value; }).get();
      $.ajax({
        url: url_getdb_studies,
        type: 'get',
        data: {
          'db_ids': checkedValues
        },
        dataType: 'json',
        success: function (data) {
          $("#table_studies").html(data['table_list']);
          stepper.next();
        }
      });
    }
  );

  $("#step2").click( function()
    {
      var checkedValues = $('input:checkbox:checked.study').map(function() { return this.value; }).get();
      $.ajax({
        url: url_get_datasets,
        type: 'get',
        data: {
          'db_ids': checkedValues
        },
        dataType: 'json',
        success: function (data) {
          $("#table_analyse").html(data['table_list']);
          stepper.next();
        }
      });
    }
  );

  $("#step3").click( function()
    {
      var checkedValues = $('input:checkbox:checked.dataset').map(function() { return this.value; }).get();
      var checkedStudy = $('input:checkbox:checked.dataset').map(function() { return this.name; }).get();
      document.location.href = url_display_data + "?study_id=" + checkedStudy[0] + "&document_id=" + checkedValues[0];
    }
  );

});