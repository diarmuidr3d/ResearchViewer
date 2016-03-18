/**
 * Created by Diarmuid Ryan on 13/03/2016.
 */

function displayCoAuthorPath(fromUri, toUri) {
    var lastPathLength = 0;
    anyPath();
    function anyPath() {
        query(prefixes.RUCD + "SELECT ?mid WHERE {\n" +
            "	<" + fromUri + "> rucd:cooperatesWith+ ?mid .\n" +
            "	?mid rucd:cooperatesWith <" + toUri + "> .\n" +
            "}", resultFunc);
        function resultFunc(data) {
            var bindings = data.results.bindings;
                console.log(data);
            if(bindings.length > 0) {
                console.log("There is a path");
                pathQuery2(lastPathLength);
            }
        }
    }
    function pathQuery2(length) {
        var i = 0;
        var selectString = prefixes.RUCD + 'SELECT (CONCAT( ';
        var queryString = "WHERE {\n" +
            "	<" + fromUri + "> rucd:cooperatesWith ?coauthor" + i + " . \n";
        while(i < length) {
            var next = i + 1;
            selectString += 'STR(?coauthor' + i + '), ",",';
            queryString += "	?coauthor" + i + " rucd:cooperatesWith ?coauthor" + next + " . \n";
            //for (var k = i; k > 0; k--) {
            //    var prev = k - 1;
            //    queryString += "	FILTER (?coauthor" + k + " != ?coauthor" + prev + ") .\n"
            //}
            i++;
        }
        selectString += 'STR(?coauthor' + i + ')) AS ?link)\n';
        queryString += "	?coauthor" + i + " rucd:cooperatesWith <" + toUri + "> .\n" +
            "}";
        query(selectString + queryString, pathResult);

        function pathResult(data) {
            var bindings = data.results.bindings;
            console.log("Path query ran", bindings);
            if(bindings.length == 0 && length < pathQueryLen) {
                pathQuery2(length + 1);
            } else if (bindings.length > 0) {
                var paths = [];
                for(var i = 0; i < bindings.length; i++) {
                    var row = bindings[i].link.value;
                    paths.push(extractPath(row));
                }
                drawPathGraph(paths);
            }
        }
        function extractPath(pathString) {
            var nodes = [];
            while(pathString.indexOf(',') != -1) {
                nodes.push(pathString.substring(0,pathString.indexOf(',')));
                pathString = pathString.substring(pathString.indexOf(',') + 1, pathString.length);
            }
            nodes.push(pathString);
            return nodes
        }
    }
    function drawPathGraph(paths) {
        var mySigma = createSigma();
        var graph = mySigma.graph;
        var ypos = paths.length / 2;
        graph.addNode({
            id: fromUri,
            x:-1,
            y:ypos,
            color: colours.author,
            size: 1
        });
        getAuthorName(fromUri, mySigma);
        graph.addNode({
            id: toUri,
            x:paths[0].length,
            y:ypos,
            color: colours.author,
            size: 1
        });
        getAuthorName(toUri, mySigma);
        var previous = fromUri;
        for(var i in paths) {
            var path = paths[i];
            var j = 0;
            while(j < path.length) {
                var nodeId = path[j];
                if(typeof graph.nodes(nodeId) === 'undefined') {
                    console.log("adding node: ", nodeId);
                    graph.addNode({
                        id: nodeId,
                        x: j,
                        y: i,
                        color: colours.coauthor,
                        size: 1
                    });
                    getAuthorName(nodeId, mySigma);
                }
                var edgeId = previous + nodeId;
                if(typeof graph.edges(edgeId) === 'undefined') {
                    graph.addEdge({
                        id: edgeId,
                        source: previous,
                        target: nodeId,
                        //color: "rgba(255,0,0,0.05)",
                        size: 1,
                        type: edgeType
                    });
                }
                previous = nodeId;
                j++;
            }
            var edgeId2 = toUri + previous;
            if(typeof graph.edges(edgeId2) === 'undefined') {
                graph.addEdge({
                    id: edgeId2,
                    source: toUri,
                    target: previous,
                    //color: "rgba(255,0,0,0.05)",
                    size: 1,
                    type: edgeType
                });
            }
            previous = fromUri;
        }
        //finish(mySigma);
        //mySigma.refresh();
        console.log(mySigma.graph);
        console.log(mySigma.graph.nodes());
    }
}