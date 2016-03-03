prefixes.RUCD = "PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#> ";

var domElements = {};
domElements.graph = 'graph';
domElements.paperList = 'papers';
endpoint = 'http://localhost:3030/ucdrr2/query';
var colours={};
colours.author = '#093';
colours.coauthor = '#f00';
colours.paper = '#00f';
colours.coauthorEdge = 'rgba(255,0,0,0.4)';
colours.opaque = "#ccc";
var pathQueryLen = 6;
var layoutRuntimeScale = 30;
var edgeType = 'curve';

sigma.classes.graph.addMethod('getIncident', function(nodeId) {
    return this.allNeighborsIndex[nodeId];
});

function createSigma() {
    $('#'+domElements.graph).html('');
    return new sigma({
        renderers: [{
            container: document.getElementById(domElements.graph),
            type: 'canvas'
        }],
        settings: {
            minEdgeSize: 1,
            labelThreshold: 6,
            maxEdgeSize: 2,
            minNodeSize: 4,
            maxNodeSize: 20,
            adjustSizes: true
        }
    });
}

function displayAuthor(uri) {
    hideSearch(true);
    var mySigma = createSigma();
    getPapersAuthored(uri, displayPapers);
    var graph = mySigma.graph;
    var authorSize = 2;
    graph.addNode({
        id: uri,
        x:0,
        y:0,
        color: colours.author,
        size: authorSize
    });
    getCoAuthorLinks();
    //setTimeout(getCoAuthors, 0);
    //setTimeout(getCoAuthors2, 0);
    getAuthorName(uri, graph);
    var mouseOverPapers = {};
    mySigma.bind('overNode', mouseNode);
    mySigma.bind('outNode', mouseNode);
    mySigma.bind('clickNode', function(e) {
        var nodeId = e.data.node.id;
        if(nodeId != uri) {
            displayAuthor(nodeId);
        }
    });
    function mouseNode(e) {
        var type = e.type;
        var coAuthUri = e.data.node.id;
        if(coAuthUri in mouseOverPapers) {
            toggle(mouseOverPapers[coAuthUri], type);
        } else {
            getCoauthoredPapers(coAuthUri,extractBindings);
        }
        function extractBindings(data) {
            var bindings = data.results.bindings;
            if(type == 'overNode') mouseOverPapers[coAuthUri] = bindings;
            toggle(bindings, type);
        }
        function toggle(uriArray, type) {
            var papers = $('#'+domElements.paperList);
            var paperElem = document.getElementById(uriArray[0].paper.value);
            if(paperElem != null) {
                if(type === 'overNode') {
                    papers.animate({
                        scrollTop: papers.scrollTop() + $(paperElem).position().top
                    }, 'slow');
                }
                for (var rowId in uriArray) {
                    var paper = uriArray[rowId].paper.value;
                    if(type === 'overNode') {
                        document.getElementById(paper).className += " active";
                    } else {
                        document.getElementById(paper).className = document.getElementById(paper).className.replace(/\bactive\b/,'');
                    }
                }
            }
        }
    }
    function getCoauthoredPapers(coAuthUri, callback) {
        var queryString = prefixes.RUCD + "SELECT ?paper WHERE {\n" +
            "<" + uri + "> rucd:publication ?paper .\n" +
            "<" + coAuthUri + "> rucd:publication ?paper .\n" +
            "}";
        query(queryString, callback);
    }
    function getCoAuthorLinks() {
        var directQuery = prefixes.RDF + prefixes.RUCD + "SELECT ?coauthor ?coauthor2  (COUNT (?paper) as ?weight) " +
            "WHERE { " +
            "<" + uri + "> rucd:cooperatesWith ?coauthor . " +
            "<" + uri + "> rucd:publication ?paper . " +
            "?coauthor rucd:publication ?paper . " +
            "?coauthor rucd:cooperatesWith ?coauthor2 . " +
            "?coauthor2 rucd:cooperatesWith <" + uri + "> . " +
            "} GROUP BY ?coauthor ?coauthor2 ";
        query(directQuery, addDirectCoAuthorLinks);
    }
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
        query(queryString, addCoAuthors);
    }
    //function getCoAuthors2() {
    //    var queryString = prefixes.RDF + prefixes.RUCD +
    //        "SELECT ?id (CONCAT(STR(?lastName), ', ', STR(?firstName)) AS ?label) (COUNT (?paper) AS ?weight) " +
    //        "WHERE { " +
    //        "<" + uri + "> rucd:cooperatesWith ?id . " +
    //        "<" + uri + "> rucd:publication ?paper . " +
    //        "?id rucd:publication ?paper . " +
    //        "?id rucd:firstName ?firstName . " +
    //        "?id rucd:lastName ?lastName . " +
    //        "} " +
    //        "GROUP BY ?id ?firstName ?lastName ?label";
    //    query(queryString, addCoAuthors2);
    //}
    //function addCoAuthors2(data) {
    //    addNodesCircle(uri, data, mySigma, 10, colours.coauthor);
    //    setTimeout(getCoAuthorLinks, 0);
    //}
    function addDirectCoAuthorLinks(data) {
        var bindings = data.results.bindings;
        if (bindings.length > 1 || bindings[0].weight.value != 0) {
            for(var rowId in bindings) {
                var row = bindings[rowId];
                var coauthor1 = row.coauthor.value;
                var coauthor2 = row.coauthor2.value;
                if(typeof graph.nodes(coauthor1) === 'undefined') {
                    graph.addNode({
                        id: coauthor1,
                        x: Math.random(),
                        y: Math.random(),
                        color: colours.coauthor
                    });
                }
                if(typeof graph.nodes(coauthor2) === 'undefined') {
                    graph.addNode({
                        id: coauthor2,
                        x: Math.random(),
                        y: Math.random(),
                        color: colours.coauthor
                    });
                }
                if((typeof graph.edges(coauthor1+coauthor2) === 'undefined') && typeof graph.edges(coauthor2+coauthor1) === 'undefined') {
                    graph.addEdge({
                        id: coauthor1 + coauthor2,
                        source: coauthor1,
                        target: coauthor2,
                        color: colours.coauthorEdge,
                        size: parseInt(row.weight.value),
                        type: edgeType,
                        priority: 1
                    });
                }
            }
        }
        getCoAuthors();
    }
    function addCoAuthors(data) {
        var bindings = data.results.bindings;
        if (bindings.length > 1 || bindings[0].weight.value != 0) {
            for (var rowId in bindings) {
                var row = bindings[rowId];
                var coauthor = row.coauthor.value;
                var size = parseInt(row.weight.value);
                if (size > authorSize) {
                    var authorNode = graph.nodes(uri);
                    //authorSize = size + (size * 0.2);
                    authorSize = size;
                    authorNode["size"] = authorSize;
                    mySigma.refresh();
                }
                var coauth = graph.nodes(coauthor);
                if (typeof coauth === 'undefined') {
                    graph.addNode({
                        id: coauthor,
                        x: Math.random(),
                        y: Math.random(),
                        size: size,
                        color: colours.coauthor,
                        label: row.lastName.value + ", " + row.firstName.value
                    });
                } else {
                    coauth.size = size;
                    coauth.label = row.lastName.value + ", " + row.firstName.value;
                }
                graph.addEdge({
                    id: uri + coauthor,
                    source: uri,
                    target: coauthor,
                    size: size,
                    type: edgeType,
                    priority: 2
                });
            }
        }
        finish(mySigma);
    }
    function displayPapers(data) {
        var container = $('#'+domElements.paperList);
        container.html('');
        var list = $("<div></div>");
        container.append(list);
        list.addClass("list-group");
        var bindings = data.results.bindings;
        for(var i in bindings) {
            var row = bindings[i];
            var item = $("<a></a>");
            item.addClass("list-group-item");
            item.attr("href", "#");
            item.attr("id", row.id.value);
            item.click(function(args){toggleNodesForPaper($(args.target).attr("id"), mySigma)});
            item.append(row.label.value);
            list.append(item);
        }
    }
    var previouspaper = null;
    function toggleNodesForPaper(paperId, sigmaInst) {
        console.log(previouspaper, " == ", paperId);
        if(paperId == previouspaper) {
            previouspaper = null;
            var nodes = graph.nodes();
            for(var rowId in nodes) {
                setColour(nodes[rowId].id);
            }
            var edges = graph.edges();
            for(var rowIdx in edges) {
                setEdgeColor(edges[rowIdx]);
            }
            sigmaInst.refresh();
        } else {
            previouspaper = paperId;
            var queryString = prefixes.RUCD + "SELECT ?author WHERE { " +
                "?author rucd:publication <" + paperId + "> . " +
                "}";
            query(queryString, toggleNodes);
        }
        function toggleNodes(data) {
            var bindings = data.results.bindings;
            var nodes = sigmaInst.graph.nodes();
            for (var rowIdx in nodes) {
                nodes[rowIdx].color = colours.opaque;
            }
            var edges = sigmaInst.graph.edges();
            for(var rowIdy in edges) {
                edges[rowIdy].color = colours.opaque;
            }
            var seenNodes = [];
            for (var rowId in bindings) {
                var nodeId = bindings[rowId].author.value;
                setColour(nodeId);
                var incidentEdges = graph.getIncident(nodeId);
                for(var neighbour in incidentEdges) {
                    if($.inArray(neighbour, seenNodes) > -1) {
                        var edgeArr = incidentEdges[neighbour];
                        //There should only ever be one node in here
                        for(var edge in edgeArr) {
                            setEdgeColor(edgeArr[edge]);
                        }
                    }
                }
                seenNodes.push(nodeId);
            }
            sigmaInst.refresh();
        }
        function setColour(node) {
            var color = colours.coauthor;
            if(node == uri) {
                color = colours.author;
            }
            sigmaInst.graph.nodes(node).color = color;
        }
        function setEdgeColor(edge) {
            if(edge.source == uri || edge.target == uri) {
                edge.color = colours.author;
            } else {
                edge.color = colours.coauthorEdge;
            }
        }
    }
}
function finish(mySigma) {
    mySigma.refresh();
    mySigma.startForceAtlas2({worker: true, barnesHutOptimize: false});
    //var fa = sigma.layouts.startForceLink(mySigma, {});
    setTimeout(stopForceAtlas, mySigma.graph.nodes().length * layoutRuntimeScale);
    //sigma.layouts.fruchtermanReingold.start(mySigma, {});

    mySigma.refresh();
    //s.stopForceAtlas2();

    function stopForceAtlas() {
        mySigma.stopForceAtlas2();
        console.log("Killed force atlas");
        //sigma.layouts.killForceLink();
    }

    //sigma.layouts.startForceLink(mySigma, {autoStop: true});
    //sigma.layouts.fruchtermanReingold.start(mySigma, {autoArea: true});
}

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
            if(bindings.length > 0) {
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
        getAuthorName(fromUri, graph);
        graph.addNode({
            id: toUri,
            x:paths[0].length,
            y:ypos,
            color: colours.author,
            size: 1
        });
        getAuthorName(toUri, graph);
        var previous = fromUri;
        for(var i in paths) {
            var path = paths[i];
            var j = 0;
            while(j < path.length) {
                var nodeId = path[j];
                if(typeof graph.nodes(nodeId) === 'undefined') {
                    graph.addNode({
                        id: nodeId,
                        x: j,
                        y: i,
                        color: colours.coauthor,
                        size: 1
                    });
                    getAuthorName(nodeId, graph);
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
        mySigma.refresh();
    }
}
function getAuthorName(uri, graph) {
    var queryString = prefixes.RDF + prefixes.RUCD + "SELECT ?firstName ?lastName " +
        "WHERE { " +
        "<" + uri + "> rucd:firstName ?firstName . " +
        "<" + uri + "> rucd:lastName ?lastName . " +
        "} ";
    query(queryString, addAuthor);
    function addAuthor(data) {
        var row = data.results.bindings[0];
        graph.nodes(uri)["label"] =  row.lastName.value + ", " + row.firstName.value;
    }
}
function findAuthorForm(formId, resultsId, authorClickFunction) {
    var firstName = $('#'+formId+' > div > .firstName');
    var lastName = $('#'+formId+' > div > .lastName');
    findAuthor(firstName.val(),lastName.val(),resultsId, authorClickFunction);
}
function findAuthor(firstName, lastname, resultsId, clickFunction) {
    var queryString = prefixes.RUCD + "SELECT ?author ?firstName ?lastName WHERE {\n";
    if(typeof firstName != 'undefined' && firstName != "") {
        queryString += '    ?author rucd:firstName ?firstName . \n' +
            '   FILTER(lcase(str(?firstName)) = "' + firstName.toLowerCase() + '") . \n';
    } else {
        queryString += "    ?author rucd:firstName ?firstName . \n";
    }
    if(typeof lastname != 'undefined' && lastname != "") {
        queryString += '    ?author rucd:lastName ?lastName . \n' +
            '   FILTER(lcase(str(?lastName)) = "' + lastname.toLowerCase() + '") . \n';
    } else {
        queryString += "   ?author rucd:lastName ?lastName . \n";
    }
    queryString += " }";
    query(queryString, displayAuthorResults);

    function displayAuthorResults(data) {
        var container = $("#" + resultsId);
        container.html('');
        container.append("Select an author to continue:");
        var list = $("<div></div>");
        container.append(list);
        list.addClass("list-group");
        var bindings = data.results.bindings;
        for(var i in bindings) {
            var row = bindings[i];
            var item = $("<a></a>");
            item.addClass("list-group-item");
            item.attr("href", "#");
            item.attr("id", row.author.value);
            item.click(function(args){clickFunction($(args.target).attr("id"), resultsId)});
            item.append(row.lastName.value + ", " + row.firstName.value);
            list.append(item);
        }
    }
}
function hideSearch(override) {
    var search = $("#searchArea");
    var hideButton = $("#hideSearch");
    if(override || search.is(":visible")) {
        search.slideUp();
        hideButton.html('<span class="glyphicon glyphicon-chevron-down"></span>Unhide Search');
    } else {
        search.slideDown();
        hideButton.html('<span class="glyphicon glyphicon-chevron-up"></span>Hide Search');
    }
}
function getPapersAuthored(authorUri, callback) {
    var queryString = prefixes.RUCD +
        "SELECT ?id ?label WHERE {\n" +
        "<" + authorUri + "> rucd:publication ?id . \n" +
        "?id rucd:title ?label" +
        "}";
    query(queryString, callback);
}
var pathAuthors={};
function pathClick(uri, authorNum) {
    pathAuthors[authorNum] = uri;
    if(Object.keys(pathAuthors).length > 1) {
        var authArr = [];
        var j = 0;
        for(var i in pathAuthors) {
            authArr[j] = pathAuthors[i];
            j++;
        }
        displayCoAuthorPath(authArr[0],authArr[1]);
        hideSearch();
    }
}
function displayBipartiteGraphAuthor(authorUri) {
    hideSearch(true);
    var mySigma = createSigma();
    var graph = mySigma.graph;
    graph.addNode({
        id: authorUri,
        x:0,
        y:0,
        color: colours.author,
        size: 1
    });
    mySigma.bind('clickNode', function(e) {
        var nodeId = e.data.node.id;
        if(nodeId != authorUri) {
            displayBipartiteGraphPaper(nodeId);
        }
    });
    getAuthorName(authorUri, graph);
    getPapersAuthored(authorUri, addPapers);
    function addPapers(data) {
        addNodesCircle(authorUri, data, mySigma, 10, colours.paper);
    }
}
function getPaperName(paperUri, graph) {
    var queryString = prefixes.RDF + prefixes.RUCD + "SELECT ?title " +
        "WHERE { " +
        "<" + paperUri + "> rucd:title ?title . " +
        "} ";
    query(queryString, addAuthor);
    function addAuthor(data) {
        var row = data.results.bindings[0];
        graph.nodes(paperUri)["label"] =  row.title.value;
    }
}
function getPaperAuthors(paperUri, callback) {
    var queryString = prefixes.RUCD +
        "SELECT ?id (CONCAT(STR(?lastName), ', ', STR(?firstName)) AS ?label) WHERE {\n" +
        "?id rucd:publication <" + paperUri + "> . \n" +
        "?id rucd:firstName ?firstName . " +
        "?id rucd:lastName ?lastName . " +
        "}";
    query(queryString, callback);
}
function displayBipartiteGraphPaper(paperUri) {
    hideSearch(true);
    var mySigma = createSigma();
    var graph = mySigma.graph;
    graph.addNode({
        id: paperUri,
        x:0,
        y:0,
        color: colours.paper,
        size: 1
    });
    mySigma.bind('clickNode', function(e) {
        var nodeId = e.data.node.id;
        if(nodeId != paperUri) {
            displayBipartiteGraphAuthor(nodeId);
        }
    });
    getPaperName(paperUri, graph);
    getPaperAuthors(paperUri, addAuthors);
    function addAuthors(data) {
        addNodesCircle(paperUri, data, mySigma, 10, colours.author);
    }
}
/**
 * This function takes the id of a node (from URI) and the result of a sparql query which
 * has id, label and an optional weight as it's headers and creates a new node for each of these ids,
 * connecting them to the original node (the edge and node size are set as the weight)
 * @param fromUri The id of an existing node to which all the nodes will be connected
 * @param toNodes the result of the sparql query which has id, label and an optional weight as it's headers
 * @param sigmaInstance The instance of sigma to which the nodes should be added
 * @param radius The radius of the circle to be displayed
 * @param nodeColour the colour to assign to the new nodes
 */
function addNodesCircle(fromUri, toNodes, sigmaInstance, radius, nodeColour) {
    var bindings = toNodes.results.bindings;
    var graph = sigmaInstance.graph;
    var fromNode = graph.nodes(fromUri);
    var x = fromNode.x;
    var y = fromNode.y;
    var len = bindings.length;
    for(var i = 0; i < len; i++) {
        var row = bindings[i];
        var weight = 1;
        if("weight" in row) {
            weight = row.weight.value;
        }
        graph.addNode({
            id: row.id.value,
            x: x + radius * Math.cos(2 * Math.PI * i / len),
            y: y + radius * Math.sin(2 * Math.PI * i / len),
            color: nodeColour,
            size: weight,
            label: row.label.value
        });
        graph.addEdge({
            id: fromUri+row.id.value,
            source: fromUri,
            target: row.id.value,
            size: weight,
            type: edgeType
        })
    }
    sigmaInstance.refresh();
}