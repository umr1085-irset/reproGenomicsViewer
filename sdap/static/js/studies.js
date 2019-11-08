$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});

$(function () {

  /* Functions */
/* In case we want to limit character numbers
  var loadTableInput = function (){
    var input = $(this);
    console.log(input.val())
    if (input.val().length > 1){
        loadTable()
    }
  }
*/
  selectRows = []

  var loadTable = function () {
    var form = $("#study-form")
    $.ajax({
      url: form.attr("data-url"),
      type: 'get',
      dataType: 'json',
      data: form.serialize(),
      success: function (data) {
        $("#table").html(data['table']);
      }
    });
  };

  var selectMe = function () {
    var row = $(this);
    var study_id = row.attr("study_id");
    var index = selectRows.indexOf(study_id);
    if(index == -1){
        row.css("background-color", "pink");
        selectRows.push(study_id);
    } else {
        row.css("background-color", "white");
        selectRows.splice(index, 1);
        if (selectRows.length ==0 ){
          $("#table_analyse").html("Select one study");
        }
    }
    summarize()
  }

  var summarize = function(){
    var summary = $("#summary");
    if(selectRows.length == 0){
        summary.html("Please select one or more studies")
        $("#nextButton").prop('disabled', true);
    } else {
        summary.html(selectRows.length + " studies selected")
        $("#nextButton").prop('disabled', false);
    }

  }

  var goToDocuments = function () {
    var button = $("#nextButton");
    var url = button.attr("data-url");
    var query_string = "?"
    for (i = 0; i < selectRows.length; i++){
        query_string += "id=" + selectRows[i] + "&";
    }
    query_string = query_string.slice(0, -1)
    var url_ref = url + query_string;
    $.ajax({
        url: url_ref,
        type: 'GET',
        cache: false,
        dataType: 'json',
        success: function (data) {
          $("#table_analyse").html(data['table']);
          stepper.next();
        },
        error: function (err) {
            console.log(err);
        }
    });
  }

  var checkSelect = function(){
    if($('option[disabled]:selected').length == 0){
        $("#graphButton").prop('disabled', false);
    }
  }

  var graphMe = function () {
    var select = $("#document_select");
    var study_id = select.attr("study_id");
    var document_id = select.val();
    var url = $("#graphButton").attr("data-url");
    document.location.href = url + "?study_id=" + study_id + "&document_id=" + document_id;
  }

  /* Binding */
    $("#filter").on("change", "select", loadTable);
    $("#filter").on("keyup", "input", loadTable);
    $("#table").on("click", "tr", selectMe);
    $("#nextButton").on("click", goToDocuments);
    $("#table_analyse").on("change", "select", checkSelect);
    $("#graphButton").on("click", graphMe);
});