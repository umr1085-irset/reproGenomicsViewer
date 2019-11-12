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
    if (chkBox.checked)
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



  $("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
  });

  $("#display_selection_a").change(function() {

    var display_class = $("#display_selection_a").val()

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

});