$(function () {

  var transposed = false;
  /* Functions */
  var get_params = function(transpose=false) {
        $("#visu_results").html("");
        var visu_type = $("#visu_type_select").val();
        var url = $("#visu_type").attr("data-url") + "?type=" + visu_type;
        if(transpose && !transposed){
            transposed = true;
            url += "&transpose=True";
        } else {
            transposed = false;
        };
        $.ajax({
            url : url,
            type: 'GET',
            success: function(response){
                if(visu_type != "Raw" && visu_type !="Table"){
                    $("#transpose").show()
                } else {
                    $("#transpose").hide()
                    transposed = false;
                }
                $("#visu_params").show();
                $("#data_table").html(response.data_table);
                $("#params").html(response.form);
            }
        });
  };

  var visualize = function() {
    var url = $("#visualize_button").attr("data-url");
    var visu_type = $("#visu_type_select").val();
    var data = "type=" +visu_type +"&"
    if (transposed){
        data += "transposed=True&"
    }
    var form = $("#visualization_form");
    data = data + form.serialize();
    $.ajax({
      url: url,
      type: 'POST',
      data: data,
      dataType: 'json',
      success: function (data) {
        if( visu_type == "Raw" || visu_type == "Table"){
            $("#visu_results").html(data.content);
        } else {
            Plotly.newPlot('visu_results', [data.content.data], data.content.layout);
        }
      }
    });
    return false
  };

  /* Binding */
    $("#visu_type_select").on("change", function(){
        get_params();
    });

    $("#visu_params").on("click", "#transpose" ,function(){
        get_params(transpose=true);
    });

    $("#params").on("submit", "#visualization_form", function(e){
        e.preventDefault();
        visualize();
    });

    $("#visualize_button").on("click", function(e){
        e.preventDefault();
        visualize();
    });

});

