function ThreeContainer(container) {
    this.width = container.width();
    this.height = container.height();
    // NOTE: this assumes only one entry in container
    this.container = container[0];
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(60, this.width / this.height, .01, 10000); //OrthographicCamera(this.width / -2, this.width / 2, this.height / -2, this.height / 2, 1, 1000) // 
    this.camera.position.set(0, 0, 500);

    this.renderer = new THREE.WebGLRenderer({antialias: true, alpha: true});
    this.renderer.setSize(this.width, this.height);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.container.appendChild(this.renderer.domElement);

    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);

    this.lines = [];
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
    console.log('onContainerResize', w, h);
}


ThreeContainer.prototype.makeLine = function (geo, width_rule) {
    var g = new MeshLine();
    console.log('makeLine', width_rule);
    g.setGeometry(geo, width_rule);

    var material = new MeshLineMaterial({
        color: new THREE.Color(0x000000),
        lineWidth: 0.25,
        side: THREE.DoubleSide
    });
    var mesh = new THREE.Mesh(g.geometry, material);
    this.scene.add(mesh);
    this.lines.push(mesh);
}

ThreeContainer.prototype.init = function() {
    this.onContainerResize();
    this.render();
}

ThreeContainer.prototype.render = function() {
    requestAnimationFrame(this.render.bind(this));
    this.renderer.render(this.scene, this.camera);
}

ThreeContainer.prototype.clearLines = function() {
    console.log('clearLines');
    this.scene.remove.apply(this.scene, this.scene.children);
    this.lines = [];
}


function neuron_javascript_embedder(js) {
    try {
        eval(js);
    } catch (err) {
        console.log(err.message);
    }
}