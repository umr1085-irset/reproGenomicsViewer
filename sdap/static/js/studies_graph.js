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


  var loadGraph = function () {
    var div = $("#graph")
    var selected_class = $("#class_select").val();
    $.ajax({
      url: div.attr("data-url") + "&selected_class=" + selected_class,
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
    loadSummaryClass();
  });

  $("#graph-form").on("change", "select", loadGraph);


  $("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
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


function poolColors (a) {
var pool = [];
  for(i=0;i<a;i++){
      pool.push(dynamicColors());
  }
  return pool;
}

function dynamicColors() {
  var r = Math.floor(Math.random() * 255);
  var g = Math.floor(Math.random() * 255);
  var b = Math.floor(Math.random() * 255);
  return "rgba(" + r + "," + g + "," + b + ",0.2)";
}


var colors = poolColors(summary_data["class_cluster"].length)

Chart.Bar('summary_cluster_classification', {
  data: {
      labels: summary_data["class_name"],
          datasets: [{
              label: "# of Cluster",
              data: summary_data["class_cluster"],
              backgroundColor: colors,
              borderWidth: 2,
          }]
  },
  options: {
    animation: false,
    responsiveAnimationDuration: 0,
      scales: {
          yAxes: [{
              ticks: {
                  beginAtZero: true
              }
          }]
      }
  }
});

Chart.Bar('summary_cell_cluster_classification', {
  data: {
      labels: summary_data["class_name"],
          datasets: [{
              label : "Median cell / cluster",
              data: summary_data["mean_cell_cluster"],
              backgroundColor: colors,
              borderWidth: 2,
          }]
  },
  options: {
    animation: false,
    responsiveAnimationDuration: 0,
      scales: {
          yAxes: [{
              ticks: {
                  beginAtZero: true
              }
          }]
      }
  }
});