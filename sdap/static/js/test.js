var current_container=""

myLayout = new GoldenLayout({
    content:[{
        type: 'row',
        content:[{
            type: 'component',
            componentName: 'testComponent',
            componentState: { color: '#1D84BD' }
        }]
    }]
}, $('#layoutContainer'));

myLayout.registerComponent( 'testComponent', function( container, state ){
    container.getElement().css('background-color', state.color);
});

/// Callback for every created stack
myLayout.on( 'stackCreated', function( stack ){

    //HTML for the colorDropdown is stored in a template tag
    var colorDropdown = $( $( 'template' ).html() );

    // Add the colorDropdown to the header
    stack.header.controlsContainer.prepend( colorDropdown );

    var setActiveContainer = function(){
        current_container = stack.getActiveContentItem().container;
        // Update the state
    };

    colorDropdown.click(function(){
        setActiveContainer();
    });

});

myLayout.init();

myLayout.on('componentCreated',function(component) {
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

var addMenuItem = function( title, color ) {
    var element = $( '<li>' + title + '</li>' );
    $( '#menuContainer' ).append( element );

   var newItemConfig = {
        title: title,
        type: 'component',
        componentName: 'testComponent',
        componentState: { color: color }
    };

    myLayout.createDragSource( element, newItemConfig );
};

addMenuItem( 'New graph', 'blue' );


$(function () {

    var set_graph = function(){
        $.ajax({
            url: "http://openstack-192-168-100-69.genouest.org/studies/graph_data?document_id=152&mode=scatter&selected_class=Class:cluster",
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

    $(".test").on('click', set_graph);
});
