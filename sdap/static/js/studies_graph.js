var selected_gene_list_to_display = [];

$(function () {

  /* Functions */
    $("#autocomplete-input").on("input change", function () {
        $.ajax({
            url: url_autocomplete,
            type: 'GET',
            cache: false,
            dataType: 'json',
            success: function (data) {
              $('input.autocomplete').autocomplete({
                data: data,
              });
            },
            error: function (err) {
                console.log(err);
            }
        });
    });
    var divauto = $("#autogene")
    
    $("#formBg1").autocomplete({
      appendTo : "#autogeneresponse",
      source: divauto.attr("data-url"),
      minLength: 2,
    });

    $("#formBg2").autocomplete({
      appendTo : "#autogeneresponse2",
      source: divauto.attr("data-url"),
      minLength: 2,
    });

    var loadGraphGeneMultiple = function() {
      var selected_class = $("#class_select").val();
      var selected_gene_list = selected_gene_list_to_display;
      var gene_id_list = []

      for (var i=0; i<selected_gene_list.length;i++){
        var gene_id = selected_gene_list[i].split("(")[1].replace(")","")
        gene_id_list.push(gene_id);
        
      }
      


      var div = $("#graph")
      var display_mode = $("#display_selection_a").val();
      
      $.ajax({
        url: div.attr("data-url")+ "&mode=" + display_mode + "&selected_class=" + selected_class + "&gene_id=" + gene_id_list.join('|'),
        type: 'get',
        dataType: 'json',
        success: function (data) {

          if(display_mode =="density"){
            var chart = data.chart;
            data = chart.data
    
            var clientWidth = document.getElementById('graph_div').offsetWidth;
            chart.layout.width = (clientWidth - 50);
            chart.layout.height = 800;
            Plotly.newPlot('graph', chart.data, chart.layout, chart.config);
            if (typeof myNewChart != 'undefined') {
              myNewChart.destroy();
            }
          }

          if(display_mode =="violin"){
            var charts = data.charts
            for(var i=0; i< charts.length;i++ ){
              var chart = charts[i];
              var div_id = 'chart_violin_'+i
              var clientWidth = document.getElementById(div_id).offsetWidth;
              chart.layout.width = (clientWidth - 50);
              chart.layout.height = 800;
              Plotly.newPlot(div_id, chart.data, chart.layout, chart.config);
              if (typeof myNewChart != 'undefined') {
                myNewChart.destroy();
              }
            }
          }
          

        }
      });
  };

    
    

  var loadGraphGene = function() {
      var selected_gene = $("#formBg1").val();
      var gene_id = selected_gene.split("(")[1].replace(")","")
      var name_gene = selected_gene.split(" ")[0]
      var div = $("#graph")
      var selected_class = $("#class_select").val();
      var chkBox = document.getElementById('densitycheck');

      var display_mode = "scatter"
      if (chkBox.checked)
      {
        display_mode = "density"
      }

      $.ajax({
        url: div.attr("data-url")+ "&mode=" + display_mode + "&selected_class=" + selected_class + "&gene_id=" + gene_id,
        type: 'get',
        dataType: 'json',
        success: function (data) {
          var chart = data.chart;
          data = chart.data
  
          var clientWidth = document.getElementById('graph_div').offsetWidth;
          chart.layout.width = (clientWidth - 50);
          chart.layout.height = 800;
          Plotly.newPlot('graph', chart.data, chart.layout, chart.config);

          var myplot = document.getElementById('graph');

          if (typeof myNewChart != 'undefined') {
            myNewChart.destroy();
          }
          $("#table_info").html('');
          $("#info_title").html('');
          $("#genemessage").html('');
          var geneChart = Chart.Bar('summary_gene_distribution')

          geneChart.destroy();
          
          var myNewChart = Chart.Bar('summary_gene_distribution', {
            data: {
                labels: chart.distribution_labels,
                    datasets: [{
                        label: name_gene + " expression (mean)",
                        data: chart.distribution_values,
                        backgroundColor: chart.colors,
                        borderWidth: 2,
                    }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
          });
          
          myplot.on('plotly_click', function(data){
            var pts = '';
            for(var i=0; i < data.points.length; i++){
                var group = data.points[i].data.name
                var sample = data.points[i].text
                var selected_class = $("#class_select").val();
            }
            $.ajax({
              beforeSend: function() {
                $('#ajax-loader').css('visibility',"visible");
            },
            complete: function(){
                $('#ajax-loader').css('visibility',"hidden");
            },
              url: url_group_info,
              type: 'get',
              dataType: 'json',
              data: {
                'group':group,
                'selected_class':selected_class,
                'sample':sample,
                'document':doc_data,
              },
              success: function (data) {
                //$("#table_info").html(data['table_list']);

                var table;
                if ($.fn.dataTable.isDataTable('#example')) {
                    table = $('#example').DataTable();
                    table.clear();
                    table.rows.add(data.list).draw();
                }
                else {
                  table = $('#example').DataTable( {
                  data: data.list,
                  columns: [
                      { title: "Gene" },
                      { title: "Expression value" },
                  ]
                  } );
                }
                $("#info_title").html(data.group);
                
              }
            });
          });
        }
      });
  };

  var loadGraph = function () {
    var div = $("#graph")
    var selected_class = $("#class_select").val();
    var chkBox = document.getElementById('densitycheck');
    $("#formBg1").val('');

    var display_mode = "scatter"
    if (chkBox != null && chkBox.checked)
    {
      display_mode = "density"
    }
    $.ajax({
      url: div.attr("data-url") + "&mode=" + display_mode + "&selected_class=" + selected_class,
      type: 'get',
      dataType: 'json',
      success: function (data) {
        var chart = data.chart;
        data = chart.data

        var clientWidth = document.getElementById('graph_div').offsetWidth;
        chart.layout.width = (clientWidth - 50);
        chart.layout.height = 800;
        Plotly.newPlot('graph', chart.data, chart.layout, chart.config);

        var myplot = document.getElementById('graph');

        if (typeof myNewChart != 'undefined') {
          myNewChart.destroy();
        }
        $("#table_info").html('');
        $("#info_title").html('');
        $("#genemessage").html('Please select a gene');
        var geneChart = Chart.Bar('summary_gene_distribution')

        geneChart.destroy();
        var geneChart = Chart.Bar('summary_cluster_distribution')

        geneChart.destroy();

        var myNewChart = Chart.Bar('summary_cluster_distribution', {
          data: {
              labels: chart.distribution_labels,
                  datasets: [{
                      label: "Cells distribution",
                      data: chart.distribution_values,
                      backgroundColor: chart.colors,
                      borderWidth: 2,
                  }]
          },
          options: {
              scales: {
                  yAxes: [{
                      ticks: {
                          beginAtZero: true
                      }
                  }]
              }
          }
        });
        
        myplot.on('plotly_click', function(data){
          var pts = '';
          for(var i=0; i < data.points.length; i++){
              var group = data.points[i].data.name
              var sample = data.points[i].text
              var selected_class = $("#class_select").val();
          }
          $.ajax({
            beforeSend: function() {
              $('#ajax-loader').css('visibility',"visible");
           },
           complete: function(){
              $('#ajax-loader').css('visibility',"hidden");
           },
            url: url_group_info,
            type: 'get',
            dataType: 'json',
            data: {
              'group':group,
              'selected_class':selected_class,
              'sample':sample,
              'document':doc_data,
            },
            success: function (data) {
              //$("#table_info").html(data['table_list']);

              var table;
              if ($.fn.dataTable.isDataTable('#example')) {
                  table = $('#example').DataTable();
                  table.clear();
                  table.rows.add(data.list).draw();
              }
              else {
                table = $('#example').DataTable( {
                data: data.list,
                columns: [
                    { title: "Gene" },
                    { title: "Expression value" },
                ]
                } );
              }
              $("#info_title").html(data.group);
              
            }
          });
        });
      }
    });
  };

  $(document).ready(function() {
    loadGraph();
  });

  $("#class_select").change(function() {
    var selected_gene = $("#formBg1").val();
    if(selected_gene == null || selected_gene == ""){
      loadGraph();
    } else {
      loadGraphGene();
    }
  });
  
  $("#select_gene_unselect").on("click", loadGraph);
  $("#densitycheck").click(function() {
    var selected_gene = $("#formBg1").val();
    if(selected_gene == null || selected_gene == ""){
      console.log("COUCOU")
      loadGraph();
    } else {
      loadGraphGene();
    }
  });
  $("#select_gene_").on("click", loadGraphGene);
  $("#select_gene_a_display").on("click", loadGraphGeneMultiple);



  $("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
  });

  
  $("#select_gene_a").click(function(e) {
    var selected_gene = $("#formBg2").val();
    if (selected_gene_list_to_display.indexOf(selected_gene) == -1 && selected_gene_list_to_display.length <= 4) {
      selected_gene_list_to_display.push(selected_gene);
    } else {
      $("#messagegene").html('<div class="alert alert-warning alert-dismissible fade show" role="alert">Your gene is already selected or selection is too long (5 genes max)<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>')
    }
    $('#select_gene_a_display').prop("disabled", false);
    var html = "<table class='table align-middle'><tbody>"
    
    $("#graphviolin").html('');
    var htmlviolin = '';
    for(var i=0; i<selected_gene_list_to_display.length; i++){
      html = html + "<tr class='align-middle'><td class='align-middle'>"+selected_gene_list_to_display[i]+"</td><td class='align-middle'><a class='btn btn-danger'  onclick='removegeneoflist(\""+selected_gene_list_to_display[i]+"\")'><i class='far fa-trash-alt'></i></a></td></tr>"
      htmlviolin = htmlviolin + "<div class='col-md-6 center-align' id='chart_violin_"+i+"'></div>";
    }
    html = html +'</tbody></table>'
    
    $("#selectedgeneslist").html(html);
    $("#graphviolin").html(htmlviolin); 
   
  });

  $("#removegeneoflist").click(function(e) {
   var index = selected_gene_list_to_display.indexOf(selected_gene)
  });



  $("#display_selection_a").change(function() {

    var display_class = $("#display_selection_a").val()
    
    if (display_class == "density" || display_class == "violin"){
        $("#div_table_select").hide();
        $("#div_gene_select").show();
    }
    if (display_class =="table"){
      $("#div_gene_select").hide();
      $("#div_table_select").show();
    }
  });

  

  $(window).resize(function(e) {
    if($(window).width()<=768){
      $("#wrapper").removeClass("toggled");
    }else{
      $("#wrapper").addClass("toggled");
    }
    var clientWidth = document.getElementById('graph_div').offsetWidth;
    Plotly.relayout('graph', {
      
      width: 0.9 * (clientWidth - 50),
      height: 0.9 * 800
    })
  });

  $("#select_table").click(function(e){
    $("#table-graph-warning").html("");
    $("#table-graph-div").html("");
    var genes = $("#gene_select_table").val();
    if (! genes){
        $("#table-graph-warning").html("Please select at least one gene");
        return;
    }

    var selected_class = $("#class_select_table").val();
    var query_type = $("#gene_query_type_table").val();
    var data = {
        'csrfmiddlewaretoken': token,
        'genes': genes,
        'query': query_type,
        'class': selected_class
    }
    var url = $(this).attr("data-url");
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function (data) {
            if (data['is_ok']){
                $("#table-graph-div").html(data['base_table']);
                $("#dt-select-table-gene").DataTable({
                    data: data['dataset'],
                    columns: data['columns'],
                    scrollX: true,
                    dom: 'Bfrtip',
                    buttons: [{ extend: 'csv', text: 'Export' }]
                });
            } else {
                $("#table-graph-warning").html(data['warning']);
            }
        },
        error: function (err) {
            console.log(err);
        }
    });
  });
});

function removegeneoflist(gene){
  var index = selected_gene_list_to_display.indexOf(gene)
  if(index >=0){
    selected_gene_list_to_display.splice(index,1)
  }

  if(selected_gene_list_to_display.length == 0){
    $('#select_gene_a_display').prop("disabled", true);
  }

  $("#selectedgeneslist").html('');
  $("#graphviolin").html('');
  var htmlviolin = '';
  var html = "<table class='table align-middle'><tbody>"
  for(var i=0; i<selected_gene_list_to_display.length; i++){
    html = html + "<tr class='align-middle'><td class='align-middle'>"+selected_gene_list_to_display[i]+"</td><td class='align-middle'><a class='btn btn-danger'  onclick='removegeneoflist(\""+selected_gene_list_to_display[i]+"\")'><i class='far fa-trash-alt'></i></a></td></tr>"
    htmlviolin = htmlviolin + "<div class='col-md-6 center-align' id='chart_violin_"+i+"'></div>";
  }
  html = html +'</tbody></table>'
  $("#selectedgeneslist").html(html);
  $("#graphviolin").html(htmlviolin); 
}
