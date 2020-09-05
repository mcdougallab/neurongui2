ShapePlot.prototype.set_diam_scale = function(diam) {
    this.diam_scale = diam;
    this.force_update(0);
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