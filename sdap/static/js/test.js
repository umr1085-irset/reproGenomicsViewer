var current_container=""
var current_stack_id=1;
var current_container_id=1;
var selected_gene_list_to_display = [];

myLayout = new GoldenLayout({
    content:[{
        type: 'row',
        content:[{
            title: 'New graph',
            type: 'component',
            componentName: 'testComponent',
            componentState: { text: '<img class="img-fluid" alt="" src="'+url_img_drag+'">' , modal_id: current_container_id }
        }]
    }],
    settings:{
        showPopoutIcon: false
    }
}, $('#layoutContainer'));

myLayout.registerComponent( 'testComponent', function( container, state ){
    container.getElement().html('<p> ' + state.text + '</p>');
});

/// Callback for every created stack
myLayout.on( 'stackCreated', function( stack ){
    // Clone the default modal and append it with correct id, associated to graph
    var clone = $($("#default_modal").html()).clone().prop('id', 'modal-' + current_stack_id );
    $("#modal-wrapper").append(clone);

    // Edit the attr to the new modal id
    var cogMenu = $( $( 'template' ).html() );
    cogMenu.find("a").attr('data-target', "#modal-" + current_stack_id);

    // Add the menu to the header
    stack.header.controlsContainer.prepend( cogMenu );
    current_stack_id += 1;

    var setActiveContainer = function(){
        current_container = stack.getActiveContentItem().container;
        // Update the state
    };

    cogMenu.click(function(){
        setActiveContainer();
    });

});

myLayout.init();

myLayout.on('componentCreated',function(component) {

    component.container.extendState({ modal_id: current_container_id });
    current_container_id += 1;
    component.container.on('resize',function() {
        if (component.container.getElement()[0].data){
            Plotly.relayout(component.container.getElement()[0], {
                width: component.container.getElement()[0].offsetWidth,
                height: component.container.getElement()[0].offsetHeight
            })
        } else if (component.container.getElement().find("iframe").length > 0) {
            component.container.getElement().find("iframe").attr("height", component.container.getElement()[0].offsetHeight);
            component.container.getElement().find("iframe").attr("width", component.container.getElement()[0].offsetWidth);
        }
    });
});

$(window).resize(function () {
    myLayout.updateSize();
});

var addMenuItem = function( title) {
    var element = $( '<button class="btn btn-light"><i class="fas fa-plus fa-2x"></i></button>' );
    $( '#menuContainer' ).append( element );

   var newItemConfig = {
        title: title,
        type: 'component',
        componentName: 'testComponent',
        componentState: { text: '<img class="img-fluid" alt="" src="'+url_img_drag+'">'}
    };

    myLayout.createDragSource( element, newItemConfig );
};

addMenuItem( 'New graph');


$(function () {

    var selector = ".autocomplete-gene";
    var autocomplete_url = $("#wrapper").attr("autocomplete-url")

    var generate_row = function(gene_label, gene_id){
        html =  "<tr class='align-middle'>";
        html += "<td class='align-middle'><input type='checkbox' class='gene_checkbox' name='gene_id' value='" + gene_id  + "'></td>";
        html += "<td class='align-middle'>" + gene_label + "</td>";
        html += "<td class='align-middle'><a class='btn btn-danger gene-remove' value='"+ gene_id + "'> <i class='far fa-trash-alt'></i></a></td>"
        html += "</tr></form>"
        return html
    }

    var set_graph = function(){
        var url = $("#wrapper").attr("data-url");
        var current_form = $("#modal-" + current_container.getState().modal_id).find(".visu-form");
        var gene_form = $("#modal-" + current_container.getState().modal_id).find(".gene-form");
        var tracks_form = $("#modal-" + current_container.getState().modal_id).find(".jbrowse_track_form");
        var selected_type = current_form.find(".visu-type").val();
        var display = current_form.find(".visu-type option:selected").text()
        var selected_class = current_form.find(".visu-class").val();
        var gene_data = gene_form.serialize();
        if (selected_type == "jbrowse"){
            url = url + "&mode="+ selected_type
            if (tracks_form.length > 0){
                url = url + "&" + tracks_form.serialize();
            }
        } else {
            url = url + "&mode="+ selected_type + "&selected_class=" + selected_class + "&" + gene_data
        }
        $.ajax({
            url: url,
            type: 'get',
            dataType: 'json',
            success: function (data) {

                current_container.getElement().html("");

                if (selected_type == "jbrowse"){
                    var content = data.iframe
                    var myelem = current_container.getElement()[0];
                    content = content.replace("iframe_width", myelem.offsetWidth)
                    content = content.replace("iframe_height",myelem.offsetHeight)
                    current_container.getElement().eq(0).html(content);
                } else {
                    var chart = data.chart;
                    if (! chart.msg == "") {
                        current_container.getElement().html(chart.msg);
                        return;
                    }
                    data = chart.data
                    var myelem = current_container.getElement()[0];
                    var clientWidth = myelem.offsetWidth;
                    chart.layout.width = myelem.offsetWidth;
                    chart.layout.height = myelem.offsetHeight;
                    current_container.setTitle(display + " " + selected_class);
                    Plotly.newPlot(myelem, chart.data, chart.layout, chart.config);
                }
            }
        });
    }

    var clear_all_genes = function(){
        $(".gene-table tbody").find('input').each(function(){
            $(this).parents("tr").remove();
        });
        selected_gene_list_to_display = []
    }

    $("#modal-wrapper").on('keydown.autocomplete', selector, function() {

        autocomplete_div = "#modal-" + current_container.getState().modal_id + " .autogeneresponse";

        $(this).autocomplete({
            source: autocomplete_url,
            minLength: 2,
            appendTo: autocomplete_div,
            focus: function( event, ui ) {
                event.preventDefault();
                $(this).val(ui.item.label);
            },
            select: function( event, ui ) {
                event.preventDefault();
                $(this).attr("value", ui.item.value);
                $(this).val(ui.item.label);
                $("#modal-wrapper .gene-add").attr("disabled", false);
            }
        });
    });

    $("#modal-wrapper").on('click', 'input:checkbox', function(e){
        var current_modal = "#modal-" + current_container.getState().modal_id;
        var current_form = $("#modal-" + current_container.getState().modal_id).find(".visu-form");
        var selected_type = current_form.find(".visu-type").val();
        var gene_form = $("#modal-" + current_container.getState().modal_id).find(".gene-form");
        if ($(this).prop("checked")){
            if (selected_type == "scatter"){
                $(this).parents('tr').siblings().find('input:checkbox').prop("checked", false);
            } else if (selected_type == "violin"){
                $(this).parents('tr').siblings().find('input:checkbox').prop("checked", false);
                $(current_modal + " .test").attr("disabled", false);
            }
        } else {
            if (selected_type == "violin"){
                $(current_modal + " .test").attr("disabled", true);
            }
        }
    });

    $("#modal-wrapper").on('change', ".visu-type", function(e) {

        var current_modal_id = current_container.getState().modal_id;
        var current_modal = "#modal-" + current_modal_id;
        var current_form = $("#modal-" + current_container.getState().modal_id).find(".visu-form");
        var selected_type = current_form.find(".visu-type").val();

        $(current_modal).find("." + selected_type + "_info").show()

        $(current_modal).find(".visu-type option:selected").siblings().each( function() {
            var val = $(this).val();
            $(current_modal).find("." + val + "_info").hide()
        });

        $(current_modal + ' input:checkbox').prop('checked', false);
        if (selected_type == "violin"){
            $(current_modal + " .test").attr("disabled", true);
            $(current_modal + " .gene_selector").show();
            $(current_modal + " .class_selector").show();
            if ($(current_modal + " .jbrowse_selector").length > 0){
                $(current_modal + " .jbrowse_selector").hide()
            }
        } else if (selected_type == "jbrowse"){
            $(current_modal + " .test").attr("disabled", false);
            $(current_modal + " .gene_selector").hide();
            $(current_modal + " .class_selector").hide();
            if ($(current_modal + " .jbrowse_selector").length > 0){
                $(current_modal + " .jbrowse_selector").show()
            }

        } else {
            $(current_modal + " .test").attr("disabled", false);
            $(current_modal + " .gene_selector").show();
            $(current_modal + " .class_selector").show();
            if ($(current_modal + " .jbrowse_selector").length > 0){
                $(current_modal + " .jbrowse_selector").hide()
            }
        }
    }),

    $("#modal-wrapper").on('click', ".gene-add", function(e) {
        var current_modal_id = current_container.getState().modal_id;
        var current_modal = "#modal-" + current_modal_id;
        $(current_modal).find('.gene_info').html("");

        var selected_gene_label = $(current_modal).find(".autocomplete-gene").val();
        var selected_gene = $(current_modal).find(".autocomplete-gene").attr('value');
        if (selected_gene_list_to_display.indexOf(selected_gene) == -1) {
            selected_gene_list_to_display.push(selected_gene)
            $(".gene-table tbody").append(generate_row(selected_gene_label, selected_gene))
            $(current_modal).find(".autocomplete-gene").val("");
            $(current_modal).find(".autocomplete-gene").attr('value', "");

        } else {
            $(current_modal).find(".messagegene").html('<div class="alert alert-warning alert-dismissible fade show" role="alert">Your gene is already selected <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>')
        }

        if (selected_gene_list_to_display.length == 0){
            $("#modal-wrapper").find(".clear_genes").hide()
        } else {
            $("#modal-wrapper").find(".clear_genes").show()
        }
        $(this).attr("disabled", true);
    });

    $("#modal-wrapper").on('click', ".gene-list-load", function(e) {
        var selected_gene_list = $("#modal-" + current_container.getState().modal_id + " .gene-list").val();
        var url = $(this).attr('data-url');
        $.ajax({
            url: url + "?id="+ selected_gene_list,
            type: 'get',
            dataType: 'json',
            success: function (data) {
                if (data.data.length > 0){
                    clear_all_genes();
                    $.each(data.data, function(index, value){
                        selected_gene_list_to_display.push(value['id'])
                        $(".gene-table tbody").append(generate_row(value['display'], value['id']))
                        $("#modal-wrapper").find(".clear_genes").show()
                    })
                }
            }
        });
    });

    $("#modal-wrapper").on('click', ".gene-remove", function(e) {
        var gene_value = $(this).attr('value');
        $(".gene-table tbody").find('input[value="' + gene_value +'"]').each(function(){
            $(this).parents("tr").remove();
        });
        var index = selected_gene_list_to_display.indexOf(gene_value)
        if(index >=0){
            selected_gene_list_to_display.splice(index,1)
        }

    });

    $("#modal-wrapper").on('click', ".clear_genes", function(e) {
        var current_modal = "#modal-" + current_container.getState().modal_id;
        var gene_table = $(current_modal).find(".gene-table");
        gene_table.find('tbody tr td input:checkbox').prop("checked", false)
        var selected_type = $(current_modal).find(".visu-type").val();
        if(selected_type == "violin"){
            $(current_modal + " .test").attr("disabled", true);
        }
    });


    $("#select_table").click(function(e){
      $("#table-graph-warning").html("");
      $("#table-graph-div").html("");
      var genes = $("#gene_select_table").val().replace(/\n/g, ',');
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

    $("#modal-wrapper").on('click', '.test', set_graph);
});

var loadGraph = function () {
    var div = $("#class_layout")
    $.ajax({
      url: div.attr("data-url") + "?document_id=" + div.attr("document-id") + "&study_id=" + div.attr("study-id"),
      type: 'get',
      dataType: 'json',
      success: function (data) {
          charts = data.data
          for(var i=0; i<charts.length; i++){
            var myNewChart = Chart.Bar('class_info_'+i, {
                data: {
                    labels: charts[i].distribution_labels,
                        datasets: [{
                            label: "Samples/Cells distribution -"+charts[i].class_name,
                            data: charts[i].distribution_values,
                            backgroundColor: charts[i].colors,
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
          }

      }
    });
  };

$(document).ready(function() {
    loadGraph();
  });
