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
            componentState: { text: ' Drag the right-side <i class="fas fa-plus"></i> button here to create a new graph, or use the cog button to select a graph.', modal_id: current_container_id }
        }]
    }]
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
        }
    });
});

$(window).resize(function () {
    myLayout.updateSize();
});

var addMenuItem = function( title) {
    var element = $( '<button class="btn btn-default"><i class="fas fa-plus fa-2x"></i></button>' );
    $( '#menuContainer' ).append( element );

   var newItemConfig = {
        title: title,
        type: 'component',
        componentName: 'testComponent',
        componentState: { text: ' Drag the right-side <i class="fas fa-plus"></i> here to create a new graph'}
    };

    myLayout.createDragSource( element, newItemConfig );
};

addMenuItem( 'New graph');


$(function () {

    var selector = ".autocomplete-gene";
    var autocomplete_url = $("#wrapper").attr("autocomplete-url")

    var generate_row = function(gene_label, gene_id){
        html =  "<tr class='align-middle'>";
        html += "<td class='align-middle'><input type='checkbox' class='gene_checkbox' name='gene' value='" + gene_id  + "'></td>";
        html += "<td class='align-middle'>" + gene_label + "</td>";
        html += "<td class='align-middle'><a class='btn btn-danger gene-remove' value='"+ gene_id + "'> <i class='far fa-trash-alt'></i></a></td>"
        html += "</tr></form>"
        return html
    }

    var set_graph = function(){
        var url = $("#wrapper").attr("data-url");
        var current_form = $("#modal-" + current_container.getState().modal_id).find(".visu-form");
        var gene_form = $("#modal-" + current_container.getState().modal_id).find(".gene-form");
        console.log(gene_form.serialize());
        var selected_type = current_form.find(".visu-type").val();
        var selected_class = current_form.find(".visu-class").val();
        $.ajax({
            url: url + "&mode="+ selected_type + "&selected_class=" + selected_class,
            type: 'get',
            dataType: 'json',
            success: function (data) {
                var chart = data.chart;
                data = chart.data
                var myelem = current_container.getElement()[0];
                var clientWidth = myelem.offsetWidth;
                chart.layout.width = myelem.offsetWidth;
                chart.layout.height = myelem.offsetHeight;
                current_container.setTitle("testtitle");
                Plotly.newPlot(myelem, chart.data, chart.layout, chart.config);
            }
        });
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

    $("#modal-wrapper").on('click', ".gene-add", function(e) {

        var current_modal_id = current_container.getState().modal_id;
        var current_modal = "#modal-" + current_modal_id;

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

        $(this).attr("disabled", true);

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

    $("#modal-wrapper").on('click', '.test', set_graph);
});
