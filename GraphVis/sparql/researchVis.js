prefixes.RUCD = "PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#> ";

var domElement = 'graph';

function displayAuthor(uri) {
    //var mySigma = new sigma('graph');
    var mySigma = new sigma({
        renderers: [{
            container: document.getElementById(domElement),
            type: 'canvas',
            settings: {
                labelThreshold: 1.2
            }
        }]
    });
    var graph = mySigma.graph;
    var authorSize = 2;
    setTimeout(getAuthorName, 0);
    setTimeout(getCoAuthors, 0);
    mySigma.bind('clickNode', function(e) {
        var div = document.getElementById(domElement);
        var parent = div.parentNode;
        parent.removeChild(div);
        var newDiv = document.createElement('div');
        newDiv.setAttribute('id',domElement);
        parent.appendChild(newDiv);
        var nodeId = e.data.node.id;
        displayAuthor(nodeId);
    });

    function getCoAuthors() {
        var queryString = prefixes.RDF + prefixes.RUCD + "SELECT ?coauthor ?firstName ?lastName (COUNT (?paper) AS ?weight) " +
            "WHERE { " +
            "<" + uri + "> rucd:cooperatesWith ?coauthor . " +
            "<" + uri + "> rucd:publication ?paper . " +
            "?coauthor rucd:publication ?paper . " +
            "?coauthor rucd:firstName ?firstName . " +
            "?coauthor rucd:lastName ?lastName . " +
            "} " +
            "GROUP BY ?coauthor ?firstName ?lastName ";
        query('http://localhost:3030/ucdrr/query', queryString, "JSON", addCoAuthors);
    }
    function getAuthorName() {
        var queryString = prefixes.RDF + prefixes.RUCD + "SELECT ?firstName ?lastName " +
            "WHERE { " +
            "<" + uri + "> rucd:firstName ?firstName . " +
            "<" + uri + "> rucd:lastName ?lastName . " +
            "} ";
        query('http://localhost:3030/ucdrr/query', queryString, "JSON", addAuthor);
    }
    function addAuthor(data) {
        var row = data.results.bindings[0];
        var fname = row.firstName.value;
        var lname = row.lastName.value;
        graph.addNode({
            id: uri,
            x:0,
            y:0,
            color: '#0f0',
            label: lname + ", " + fname,
            size: authorSize
        });
    }
    function addCoAuthors(data) {
        var bindings = data.results.bindings;
        for(var rowId in bindings) {
            var row = bindings[rowId];
            var coauthor = row.coauthor.value;
            var size = row.weight.value;
            if(size > authorSize) {
                var authorNode = graph.nodes(uri);
                authorSize = size + (size * 0.2);
                authorNode["size"] = authorSize;
                mySigma.refresh();
            }
            graph.addNode({
                id: coauthor,
                x: Math.random(),
                y: Math.random(),
                size: size,
                color: '#f00',
                label: row.lastName.value + ", " + row.firstName.value
            });
            graph.addEdge({
                id: uri+coauthor,
                source: uri,
                target: coauthor,
                size: size
            });
        }
        mySigma.startForceAtlas2({worker: true, barnesHutOptimize: false});
        setTimeout(stopForceAtlas, 600);
        //s.stopForceAtlas2();

        function stopForceAtlas() {
            mySigma.stopForceAtlas2();
        }
    }
}