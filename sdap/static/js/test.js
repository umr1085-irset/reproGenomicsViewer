var current_container=""
var current_stack_id=1;
var current_container_id=1;

myLayout = new GoldenLayout({
    content:[{
        type: 'row',
        content:[{
            title: 'New graph',
            type: 'component',
            componentName: 'testComponent',
            componentState: { text: ' Drag a new graph here, or use the cog button to select a graph.', modal_id: current_container_id }
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

var addMenuItem = function( title ) {
    var element = $( '<li>' + title + '</li>' );
    $( '#menuContainer' ).append( element );

   var newItemConfig = {
        title: title,
        type: 'component',
        componentName: 'testComponent',
        componentState: { text: ' Drag a new graph here, or use the cog button to select a graph.'}
    };

    myLayout.createDragSource( element, newItemConfig );
};

addMenuItem( 'New graph');


$(function () {

    var set_graph = function(){
        var url = $("#wrapper").attr("data-url");
        console.log(current_container.getState().modal_id);
        var current_form = $("#modal-" + current_container.getState().modal_id).find("form");
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

    $("#modal-wrapper").on('click', '.test', set_graph);
});
