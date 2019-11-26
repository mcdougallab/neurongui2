var neuron_section_data = undefined;

function set_neuron_section_data(new_data) {
    neuron_section_data = new_data;
    for(sp of _shape_plots) {
        sp.update();
    }
}

function ShapePlot(container) {
    this.diam_scale = 1;
    this.mode = 1;
    this.tc = new ThreeContainer(container);
    this.container = container;
    this.section_data = undefined;
    this.vmin = -100;
    this.vmax = 100;
}

ShapePlot.prototype.update = function() {
    if (this.section_data !== neuron_section_data) {
        this.section_data = neuron_section_data;
        this.tc.clearLines();
        var my_mode = this.mode;
        function const_function(val) {
            return function(p) {return val};
        }
        function sp_interpolater(arc3d, ys, diam_scale) {
            var my_arc3d = [];
            var lo = arc3d[0];
            var hi = arc3d[arc3d.length - 1];
            var delta = hi - lo;
            for (var i = 0; i < arc3d.length; i++) {
                my_arc3d.push((arc3d[i] - lo) / delta);
            }
            return function(p) {
                for(var i = 1; i < my_arc3d.length; i++) {
                    var me = my_arc3d[i];
                    if (p < me) {
                        var last = my_arc3d[i - 1];
                        var x = (p - last) / (me - last);
                        return diam_scale * (x * ys[i] + (1 - x) * ys[i - 1]);
                    }
                }
                return ys[my_arc3d.length - 1] * diam_scale;
            }
        }
        var const_diam_f = const_function(4 * this.diam_scale);
        var my_width_rule;
        for(var i = 0; i < this.section_data.length; i++) {
            var my_segment = this.section_data[i];
            var xs = my_segment[0];
            var ys = my_segment[1];
            var zs = my_segment[2];
            var ds = my_segment[3];
            var arcs = my_segment[4];
            var geo = new THREE.Geometry();
            for(var j = 0 ; j < xs.length; j++) {
                geo.vertices.push(new THREE.Vector3(xs[j], ys[j], zs[j]));
            }
            if (this.mode == 0) {
                my_width_rule = sp_interpolater(arcs, ds, 4 * this.diam_scale);
            } else {
                my_width_rule = const_diam_f;
            }
            this.tc.makeLine(geo, my_width_rule);
        }
    }
}

ShapePlot.prototype.force_update = function() {
    this.section_data = undefined;
    this.update();
}


ShapePlot.prototype.set_diam_scale = function(diam) {
    this.diam_scale = diam;
    this.force_update();
}

ShapePlot.prototype.update_colors = function(data) {
    var vmin = this.vmin;
    var vmax = this.vmax;
    var vdelta = vmax - vmin;
    for (var i = 0; i < this.section_data.length; i++) {
        var v = data[i];
        var r, g, b;
        if (v == null) {
            r = 0;
            g = 0;
            b = 0;
        } else {
            v = (data[i] - vmin) / vdelta;
            if (v < 0) {v = 0;}
            if (v > 1) {v = 1;}
            r = v;
            b = 1 - v;
            g = 0;
        }
        var cv = this.tc.lines[i].material.uniforms.color.value;
        cv.r = r;
        cv.g = g;
        cv.b = b;
    }
}