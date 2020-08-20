function ThreeContainer(container) {
    // NOTE: this assumes only one entry in container
    this.container = container[0];
    this.width = this.container.clientWidth;
    this.height = this.container.clientHeight;
    this.scene = new THREE.Scene();
    this.pickingScene = new THREE.Scene();
    this.pickingScene.background = new THREE.Color(0);
    this.pickingTexture = new THREE.WebGLRenderTarget(this.width, this.height, {format: THREE.RGBFormat});

    this.camera = new THREE.PerspectiveCamera(60, this.width / this.height, .01, 10000); //OrthographicCamera(this.width / -2, this.width / 2, this.height / -2, this.height / 2, 1, 1000) // 
    this.camera.position.set(0, 0, 500);

    this.renderer = new THREE.WebGLRenderer({antialias: true, alpha: true});
    this.renderer.setSize(this.width, this.height);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.container.appendChild(this.renderer.domElement);

    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);

    this.points = [];
    this.lines = [];
    this.linecolors = [];
    this.pickinglinecolors = [];
    this.triangle_pts = [0,3,7,7,0,4,1,0,4,4,1,5,2,1,5,5,2,6,3,2,6,6,3,7];
    this.endface_pts = [0,2,1,0,2,3];
    this.mesh= new THREE.Mesh();

    container.resize(this.onContainerResize);
    console.log('ThreeContainer', this);
    this.init();
    return this;
}


ThreeContainer.prototype.onContainerResize = function() {
    var w = this.container.clientWidth;
    var h = this.container.clientHeight;

    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();

    this.renderer.setSize(w, h);
    this.pickingTexture.setSize(w, h);
    this.width = w;
    this.height = h;
}


ThreeContainer.prototype.addLine = function (geo, diams) {
    var n = new THREE.Vector3();
    var v2 = new THREE.Vector3();
    var index = this.points.length;
    var start_pts, end_pts, start_JoinPoints;

    var geolength = geo.length;
    var endflag = false;
    var startflag = true;
    for (g=0; g < (geolength-1); g++) {
        var x0=geo[g][0], y0=geo[g][1], z0=geo[g][2], x1=geo[g+1][0], y1=geo[g+1][1], z1=geo[g+1][2];
        var r0=diams[g], r1=diams[g+1];

        if (g==geolength-2) {   // catch if it's last line in segment
            endflag = true;
        }
        
        // find the normal vector to the base of the prism (n) and a random perpendicular (v2)
        n.set(x1-x0,y1-y0,z1-z0);
        if (n.z==0) {
            if (n.y==0) {v2.set(0,1,0);}
            else {v2.set(1,-1*(n.x/n.y), 0);}
        }
        else {v2.set(1, 0, -1*(n.x/n.z));}

        n.cross(v2);   
        n.normalize();
        v2.normalize();
        
        vertex0 = [x0+(r0*v2.x), y0+(r0*v2.y), z0+(r0*v2.z)];
        vertex1 = [x0+(r0*n.x), y0+(r0*n.y), z0+(r0*n.z)];
        vertex4 = [x1+(r1*v2.x), y1+(r1*v2.y), z1+(r1*v2.z)];
        vertex5 = [x1+(r1*n.x), y1+(r1*n.y), z1+(r1*n.z)];

        n.negate();
        v2.negate();

        vertex2 = [x0+(r0*v2.x), y0+(r0*v2.y), z0+(r0*v2.z)];
        vertex3 = [x0+(r0*n.x), y0+(r0*n.y), z0+(r0*n.z)];
        vertex6 = [x1+(r1*v2.x), y1+(r1*v2.y), z1+(r1*v2.z)];
        vertex7 = [x1+(r1*n.x), y1+(r1*n.y), z1+(r1*n.z)];
        start_pts = [vertex0,vertex1,vertex2,vertex3];
        end_pts = [vertex4,vertex5,vertex6,vertex7];

        if (startflag) {        // add starting end face to points
            for (var a=0; a < 6; a++) {
                this.points.push(...start_pts[this.endface_pts[a]]);
            }
            startflag=false;
        }
        else {   // add the previous join's points except if it's the first segment
            //start_JoinPoints.push(...start_pts);
            start_JoinPoints.push(...[vertex0,vertex1,vertex2,vertex3]);
            //start_JoinPoints.push(...[[10,10,10],[8,8,8],[10,9,9],[9,9,10]]);
            for (var k=0; k < this.triangle_pts.length; k++) {
                this.points.push(...start_JoinPoints[this.triangle_pts[k]]);
            }
        }
        start_pts.push(...end_pts);
        for (var j=0; j < this.triangle_pts.length; j++) {  // add this segment's regular points
            this.points.push(...start_pts[this.triangle_pts[j]]);
        }
        
        if (endflag) {      // add ending end face to points
            for (var b=0; b < 6; b++) {
                this.points.push(...end_pts[this.endface_pts[b]]);
            }
        }
        else {start_JoinPoints = end_pts;}
        
    }
    // virtual buffer id as color
    const id = this.lines.length + 1;
    id_map[id] = index;
    var idcolor = new THREE.Color(id);
    var r=idcolor.r, g=idcolor.g, b=idcolor.b;
    this.pickinglinecolors.push([r,g,b,r,g,b,r,g,b]);   //keeps track of vertex colors (picking mesh) for triangles in this line

    this.lines.push(index); // keeps track of starting point in each line
    this.linecolors.push([0,0,0,0,0,0,0,0,0])   //keeps track of vertex colors for triangles in this line
}

ThreeContainer.prototype.renderLines = function() {
    var full_geometry = new THREE.BufferGeometry();
    var pick_geometry = new THREE.BufferGeometry();
    var positions = [];
    var normals = [];
    var colors = [];
    var pickingcolors = [];
    var current_lineindex = 0; // keeps track of current line while looping to assign colors etc
    var current_linecolor = this.linecolors[current_lineindex];
    var current_pickcolor = this.pickinglinecolors[current_lineindex];

    var p1 = new THREE.Vector3();
    var p2 = new THREE.Vector3();
    var p3 = new THREE.Vector3();
    var cross1 = new THREE.Vector3();
    var cross2 = new THREE.Vector3();
    var color = new THREE.Color();

    for (var i=0; i<this.points.length; i += 9) {
        var x1=this.points[i], y1=this.points[i+1], z1=this.points[i+2],
            x2=this.points[i+3], y2=this.points[i+4], z2=this.points[i+5],
            x3=this.points[i+6], y3=this.points[i+7], z3=this.points[i+8];
    
        positions.push(x1,y1,z1);
        positions.push(x2,y2,z2);
        positions.push(x3,y3,z3);
        p1.set(x1,y1,z1);
        p2.set(x2,y2,z2);
        p3.set(x3,y3,z3);
    
        cross1.subVectors(p3,p2);
        cross2.subVectors(p1,p2);
        cross1.cross(cross2);
      
        cross1.normalize();
    
        var nx=cross1.x, ny=cross1.y, nz=cross1.z;
    
        normals.push( nx, ny, nz );
        normals.push( nx, ny, nz );
        normals.push( nx, ny, nz );
    
        if (i==this.lines[current_lineindex]) {
            // assign the colors and picking colors for this line and then increment index
            current_linecolor = this.linecolors[current_lineindex];
            current_pickcolor = this.pickinglinecolors[current_lineindex];
            colors.push(...current_linecolor);
            pickingcolors.push(...current_pickcolor);
            current_lineindex++;
        }
        else {
            colors.push(...current_linecolor);
            pickingcolors.push(...current_pickcolor);
        }        
    }
    full_geometry.addAttribute( 'position', new THREE.Float32BufferAttribute( positions, 3 ));
    full_geometry.addAttribute( 'normal', new THREE.Float32BufferAttribute( normals, 3 ));
    full_geometry.addAttribute( 'color', new THREE.Float32BufferAttribute( colors, 3 ));

    pick_geometry.addAttribute( 'position', new THREE.Float32BufferAttribute( positions, 3 ));
    pick_geometry.addAttribute( 'normal', new THREE.Float32BufferAttribute( normals, 3 ));
    pick_geometry.addAttribute( 'color', new THREE.Float32BufferAttribute( pickingcolors, 3 ));

    var material = new THREE.MeshBasicMaterial( {
        side: THREE.DoubleSide, vertexColors: THREE.VertexColors
    });
    
    this.mesh = new THREE.Mesh( full_geometry, material );
    this.scene.add( this.mesh );
    var pickmesh = new THREE.Mesh( pick_geometry, material );
    this.pickingScene.add(pickmesh);
}

ThreeContainer.prototype.ReColor = function() {
    var colors = [];
    var current_lineindex = 0; 
    var current_linecolor = this.linecolors[current_lineindex];

    for (var i=0; i<this.points.length; i += 9) {
        if (i==this.lines[current_lineindex]) {
            // assign the colors and picking colors for this line and then increment index
            current_linecolor = this.linecolors[current_lineindex];
            colors.push(...current_linecolor);
            current_lineindex++;
        }
        else {
            colors.push(...current_linecolor);
        } 
    }
    var meshcolors = this.mesh.geometry.attributes.color.array;
    for (var i=0; i<colors.length; i++) {
        meshcolors[i] = colors[i];
    }
    this.mesh.geometry.attributes.color.needsUpdate = true;
}

ThreeContainer.prototype.init = function() {
    this.onContainerResize();
    this.render();
}

ThreeContainer.prototype.render = function() {
    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(this.render.bind(this));
}

ThreeContainer.prototype.clearLines = function() {
    this.scene.remove.apply(this.scene, this.scene.children);
    this.pickingScene.remove.apply(this.pickingScene, this.pickingScene.children);
    this.lines = [];
    this.points = [];
}


function neuron_javascript_embedder(js) {
    try {
        eval(js);
    } catch (err) {
        console.log(err.message);
    }
}
