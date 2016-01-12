prefixes.RUCD = "PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#> ";

function displayAuthor(uri) {
    var queryString = prefixes.RDF + prefixes.RUCD + "SELECT ?coauthor (COUNT (?paper) AS ?weight) " +
        "WHERE { " +
        "<" + uri + "> rucd:cooperatesWith ?coauthor . " +
        "<" + uri + "> rucd:publication ?paper . " +
        "?coauthor rucd:publication ?paper . " +
        "} " +
        "GROUP BY ?coauthor ";
    query('http://localhost:3030/ucdrr/query', queryString, "JSON", display);
    var s = new sigma('graph');
    var graph = s.graph;
    graph.addNode({
        id: uri,
        x:0,
        y:0,
        size: 2
    });

    function display(data) {
        var bindings = data.results.bindings;
        for(var rowId in bindings) {
            var row = bindings[rowId];
            var coauthor = row.coauthor.value;
            console.log(coauthor);
            graph.addNode({
                id: coauthor,
                x: Math.random(),
                y: Math.random(),
                size: row.weight.value
            });
            graph.addEdge({
                id: uri+coauthor,
                source: uri,
                target: coauthor
            })
        }
        s.startForceAtlas2({worker: true, barnesHutOptimize: false});
        setTimeout(stopForceAtlas, 600);
        //s.stopForceAtlas2();

        function stopForceAtlas() {
            s.stopForceAtlas2();
        }
    }
}