var neuron_section_data = undefined;
var _shape_plots_mapping = {};      // maps div ID to the ShapePlot object
var id_map = {};        // maps line ID to the index in tc.points that the line's points start
var mouse = new THREE.Vector2();

function set_neuron_section_data(new_data) {
    neuron_section_data = new_data;
    for(sp of _shape_plots) {
        sp.update(0);
    }
}

function ShapePlot(container) {
    this.diam_scale = 1;
    this.tc = new ThreeContainer(container);
    this.container = container;
    this.section_data = undefined;
    this.vmin = -100;
    this.vmax = 100;
    this.container.on( 'click', clickEvent);
    _shape_plots_mapping[this.container.attr('id')] = this;
}

function clickEvent(event) {
    //TODO: try only-one-pixel option again
    var plot = _shape_plots_mapping[$(this).attr('id')];
    mouse.x = event.clientX;
    mouse.y = plot.tc.height - event.clientY;

    // virtual buffer read 
    var pixelBuffer = new Uint8Array(3);
    render = plot.tc.renderer;
    render.render(plot.tc.pickingScene, plot.tc.camera, plot.tc.pickingTexture);
    render.readRenderTargetPixels(plot.tc.pickingTexture, mouse.x, mouse.y, 1, 1, pixelBuffer);

    const id = (pixelBuffer[0] << 16) | (pixelBuffer[1] << 8) | (pixelBuffer[2]);
    if (id != 0) {
        /*var index = id_map[id];
        var clicked_pts = [];
        for (var k=0; k < 144; k++) {
            if ((index+k) < plot.tc.points.length) {
            clicked_pts.push(plot.tc.points[index+k]);}
        }*/
        console.log('intersected!');
        _section_intersected(browser_id, id);
        //console.log(clicked_pts);
    } 

}

ShapePlot.prototype.update = function(diam_flag) {
    // TODO: is this check necessary? Can just check if undefined?
    if (this.section_data !== neuron_section_data[0]) {
        this.section_data = neuron_section_data[0];
        if (!diam_flag) {
            this.camera_dist = neuron_section_data[1]*2.5;
            this.tc.camera.position.set(0,0,this.camera_dist);
        }
        this.tc.onContainerResize();
        this.tc.clearLines();
        var my_mode = this.container.attr('data-mode');
        if (my_mode == undefined) {
            my_mode = 1;
        }
        for(var i = 0; i < this.section_data.length; i++) {
            var my_segment = this.section_data[i];
            var xs = my_segment[0];
            var ys = my_segment[1];
            var zs = my_segment[2];
            var ds = my_segment[3];
            var arcs = my_segment[4];
            var geo = [];
            for(var j = 0 ; j < xs.length; j++) {
                geo.push([xs[j], ys[j], zs[j]]);
            }
            var shown_diams = [];
            if (my_mode == 1) {
                for (var k=0; k < ds.length; k++){
                    shown_diams.push(0.5);
                }
            }
            else {shown_diams = ds;}
            this.tc.addLine(geo, shown_diams);
        }
        this.tc.renderLines();
    }
}

ShapePlot.prototype.force_update = function(diam_flag) {
    this.section_data = undefined;
    this.update(diam_flag);
}