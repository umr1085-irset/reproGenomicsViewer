$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-group").modal("show");
      },
      success: function (data) {
        $("#modal-group .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    var data = form.serialize();
    $.ajax({
      url: form.attr("action"),
      data: data,
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
            window.location.href = data.redirect
        }
        else {
          $("#modal-group .modal-content").html(data.html_form);
          if (data.error){
            $("#modal-group .modal-content #error").html(data.error);
          }
        }
      }
    });
    return false;
  };

  var saveFormFile = function (e) {
    e.preventDefault();
    var form = $(this);
    //var data = form.serialize();
    var data = new FormData(this)
    console.log(data);
    $.ajax({
      xhr: function(){
        var xhr = new window.XMLHttpRequest();
        xhr.upload.addEventListener('progress', function(e){
            if(e.lengthComputable){
                var percent = Math.round((e.loaded/e.total) * 100);
                console.log(percent);
                $('#progress_bar').attr('aria-valuenow', percent).css('width', percent + '%');
            }
        })

        return xhr;
      },
      url: form.attr("action"),
      data: data,
      type: form.attr("method"),
      dataType: 'json',
      processData: false,
      contentType: false,
      beforeSend: function () {
        $("#progress_div").show();
      },
      success: function (return_data) {
        if (return_data.form_is_valid) {
            window.location.href = return_data.redirect
        }
        else {
          $("#modal-group .modal-content").html(return_data.html_form);
          if (return_data.error){
            $("#modal-group .modal-content #error").html(return_data.error);
          }
        }
      }
    });
    return false;
  };

  /* Binding */
    $(".js-create").on("click", loadForm);
    $("#modal-group").on("submit", ".js-create-file", saveFormFile);
    $("#modal-group").on("submit", ".js-create", saveForm);
    $(".file").on("click", ".js-delete", loadForm);
    $("#modal-group").on("submit", ".js-delete", saveForm);
});
