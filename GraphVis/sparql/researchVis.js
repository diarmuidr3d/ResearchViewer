prefixes.RUCD = "PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#> ";

var domElement = 'graph';

function createSigma() {
    $('#'+domElement).html('');
    return new sigma({
        renderers: [{
            container: document.getElementById(domElement),
            type: 'canvas'
        }],
        settings: {
            labelThreshold: 5,
            minEdgeSize: 1,
            maxEdgeSize: 2,
            minNodeSize: 4,
            maxNodeSize: 20,
            adjustSizes: true
        }
    });
}

function displayAuthor(uri) {
    hideSearch(true);
    getPapersAuthored(uri, displayPapers);
    var mySigma = createSigma();
    var graph = mySigma.graph;
    var authorSize = 2;
    graph.addNode({
        id: uri,
        x:0,
        y:0,
        color: '#0f0',
        size: authorSize
    });
    //setTimeout(getAuthorName, 0);
    setTimeout(getCoAuthors, 0);
    getAuthorName(uri, graph);
    var mouseOverPapers = {};
    mySigma.bind('overNode', function(e) {
        var coAuthUri = e.data.node.id;
        if(coAuthUri in mouseOverPapers) {
            setAsActive(mouseOverPapers[coAuthUri]);
        } else {
            getCoauthoredPapers(coAuthUri,highlightSharedPapers);
        }
        function highlightSharedPapers(data) {
            var bindings = data.results.bindings;
            mouseOverPapers[coAuthUri] = bindings;
            setAsActive(bindings);
        }
        function setAsActive(uriArray) {
            var papers = $('#papers');
            papers.animate({scrollTop: papers.scrollTop() + $(document.getElementById(uriArray[0].paper.value)).position().top}, 'slow');
            for (var rowId in uriArray) {
                var paper = uriArray[rowId].paper.value;
                document.getElementById(paper).className += " active";
            }
        }
    });
    mySigma.bind('outNode', function(e) {
        var coAuthUri = e.data.node.id;
        if(coAuthUri in mouseOverPapers) {
            setAsInactive(mouseOverPapers[coAuthUri]);
        } else {
            getCoauthoredPapers(coAuthUri,unHighlightSharedPapers);
        }
        function unHighlightSharedPapers(data) {
            var bindings = data.results.bindings;
            setAsInactive(bindings);
        }
        function setAsInactive(uriArray){
            for (var rowId in uriArray) {
                var paper = uriArray[rowId].paper.value;
                document.getElementById(paper).className = document.getElementById(paper).className.replace(/\bactive\b/,'');
            }
        }
    });
    mySigma.bind('clickNode', function(e) {
        var nodeId = e.data.node.id;
        if(nodeId != uri) {
            displayAuthor(nodeId);
        }
    });
    function getCoauthoredPapers(coAuthUri, callback) {
        var queryString = prefixes.RUCD + "SELECT ?paper WHERE {\n" +
            "<" + uri + "> rucd:publication ?paper .\n" +
            "<" + coAuthUri + "> rucd:publication ?paper .\n" +
            "}";
        query('http://localhost:3030/ucdrr/query', queryString, "JSON", callback);
    }
    function getCoAuthorLinks() {
        var directQuery = prefixes.RDF + prefixes.RUCD + "SELECT ?coauthor ?coauthor2  " +
            "WHERE { " +
            "<" + uri + "> rucd:cooperatesWith ?coauthor . " +
            "?coauthor rucd:cooperatesWith ?coauthor2 . " +
            "?coauthor2 rucd:cooperatesWith <" + uri + "> . " +
            "} ";
        query('http://localhost:3030/ucdrr/query', directQuery, "JSON", addDirectCoAuthorLinks);
        //var inDirectQuery = prefixes.RDF + prefixes.RUCD + "SELECT ?coauthor ?link ?coauthor2 ?firstName ?lastName " +
        //    "WHERE { " +
        //    "<" + uri + "> rucd:cooperatesWith ?coauthor . " +
        //    "?coauthor rucd:cooperatesWith ?link . " +
        //    "?link rucd:cooperatesWith ?coauthor2 . " +
        //    "FILTER( ?coauthor != ?coauthor2 ) . " +
        //    "BIND( EXISTS{ ?link rucd:cooperatesWith  <" + uri + "> } as ?isLinked ) . " +
        //    "FILTER( ?isLinked != true ) . " +
        //    "?coauthor2 rucd:cooperatesWith <" + uri + "> . " +
        //    "?link rucd:firstName ?firstName . " +
        //    "?link rucd:lastName ?lastName . " +
        //    "} ";
        //console.log(inDirectQuery);
        //query('http://localhost:3030/ucdrr/query', inDirectQuery, "JSON", addInDirectCoAuthorLinks);
        finish(mySigma);
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
        query('http://localhost:3030/ucdrr/query', queryString, "JSON", addCoAuthors);
    }
    function addDirectCoAuthorLinks(data) {
        var bindings = data.results.bindings;
        for(var rowId in bindings) {
            var row = bindings[rowId];
            var coauthor1 = row.coauthor.value;
            var coauthor2 = row.coauthor2.value;
            graph.addEdge({
                id: coauthor1+coauthor2,
                source: coauthor1,
                target: coauthor2,
                color: "rgba(255,0,0,0.09)",
                size: 1,
                type:'curve'
            });
        }
    }
    //function addInDirectCoAuthorLinks(data) {
    //    console.log(data);
    //    var bindings = data.results.bindings;
    //    for(var rowId in bindings) {
    //        var row = bindings[rowId];
    //        //console.log(row);
    //        var coauthor1 = row.coauthor.value;
    //        var coauthor2 = row.coauthor2.value;
    //        var link = row.link.value;
    //        var existingLink = graph.nodes(link);
    //        //console.log(existingLink);
    //        if(typeof existingLink === 'undefined') {
    //            graph.addNode({
    //                id: link,
    //                x: Math.random(),
    //                y: Math.random(),
    //                size: 1,
    //                color: 'rgba(0,0,255,0.05)',
    //                label: row.lastName.value + ", " + row.firstName.value
    //            });
    //        }
    //        var edge1 = coauthor1 + link;
    //        if(typeof graph.edges(edge1) === 'undefined') {
    //            graph.addEdge({
    //                id: edge1,
    //                source: coauthor1,
    //                target: link,
    //                color: 'rgba(0,0,255,0.05)',
    //                size: 1
    //            });
    //        }
    //        var edge2 = coauthor2 + link;
    //        if(typeof graph.edges(edge2) === 'undefined') {
    //            graph.addEdge({
    //                id: coauthor2 + link,
    //                source: coauthor2,
    //                target: link,
    //                color: 'rgba(0,0,255,0.05)',
    //                size: 1
    //            });
    //        }
    //    }
    //    finish(mySigma);
    //}
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
                size: size,
                type:'curve'
            });
        }
        setTimeout(getCoAuthorLinks, 0);
    }
}
function finish(mySigma) {
    console.log("Running finish loop");
    mySigma.refresh();
    mySigma.startForceAtlas2({worker: true, barnesHutOptimize: false});
    setTimeout(stopForceAtlas, 500);
    //s.stopForceAtlas2();

    function stopForceAtlas() {
        mySigma.stopForceAtlas2();
    }

    //sigma.layouts.startForceLink(mySigma, {autoStop: true});
    //sigma.layouts.fruchtermanReingold.start(mySigma, {autoArea: true});
}

function displayCoAuthorPath(fromUri, toUri) {
    var lastPathLength = 0;
    anyPath();
    function anyPath() {
        query('http://localhost:3030/ucdrr/query',
            prefixes.RUCD + "SELECT ?mid WHERE {\n" +
            "	<" + fromUri + "> rucd:cooperatesWith+ ?mid .\n" +
            "	?mid rucd:cooperatesWith <" + toUri + "> .\n" +
            "}",
            "JSON", resultFunc);
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
            for (var k = i; k > 0; k--) {
                var prev = k - 1;
                queryString += "	FILTER (?coauthor" + k + " != ?coauthor" + prev + ") .\n"
            }
            i++;
        }
        selectString += 'STR(?coauthor' + i + ')) AS ?link)\n';
        queryString += "	?coauthor" + i + " rucd:cooperatesWith <" + toUri + "> .\n" +
            "}";
        query('http://localhost:3030/ucdrr/query', selectString + queryString, "JSON", pathResult);

        function pathResult(data) {
            var bindings = data.results.bindings;
            if(bindings.length == 0 && length < 6) {
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
        console.log(paths);
        var mySigma = createSigma();
        var graph = mySigma.graph;
        graph.addNode({
            id: fromUri,
            x:-1,
            y:0,
            color: '#0f0',
            size: 1
        });
        getAuthorName(fromUri, graph);
        graph.addNode({
            id: toUri,
            x:paths[0].length,
            y:0,
            color: '#0f0',
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
                        color: '#f00',
                        size: 1
                    });
                    getAuthorName(nodeId, graph);
                }
                var edgeId = previous + nodeId;
                //console.log(graph.edges(edgeId));
                if(typeof graph.edges(edgeId) === 'undefined') {
                    graph.addEdge({
                        id: edgeId,
                        source: previous,
                        target: nodeId,
                        //color: "rgba(255,0,0,0.05)",
                        size: 1,
                        type:'curve'
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
                    type:'curve'
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
    query('http://localhost:3030/ucdrr/query', queryString, "JSON", addAuthor);
    function addAuthor(data) {
        var row = data.results.bindings[0];
        graph.nodes(uri)["label"] =  row.lastName.value + ", " + row.firstName.value;
    }
}
function findAuthorForm(formId, resultsId, displayId, authorClickFunction) {
    var firstName = $('#'+formId+' > div > .firstName');
    var lastName = $('#'+formId+' > div > .lastName');
    findAuthor(firstName.val(),lastName.val(),resultsId,displayId, authorClickFunction);
}
function findAuthor(firstName, lastname, resultsId, displayId, clickFunction) {
    var queryString = prefixes.RUCD + "SELECT ?author ?firstName ?lastName WHERE {\n";
    if(typeof firstName != 'undefined' && firstName != "") {
        queryString += '    ?author rucd:firstName "' + firstName + '" . \n';
    }
    if(typeof lastname != 'undefined' && lastname != "") {
        queryString += '    ?author rucd:lastName "' + lastname + '" . \n';
    }
    queryString += "    ?author rucd:firstName ?firstName . \n" +
        "   ?author rucd:lastName ?lastName . \n" +
        "}";
    query('http://localhost:3030/ucdrr/query', queryString, "JSON", displayAuthorResults);

    function displayAuthorResults(data) {
        var container = $("#" + resultsId);
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
        "SELECT ?paper ?title WHERE {\n" +
        "<" + authorUri + "> rucd:publication ?paper . \n" +
        "?paper rucd:title ?title" +
        "}";
    query('http://localhost:3030/ucdrr/query', queryString, "JSON", callback);
    function displayPapers(data) {
        var container = $('#papers');
        container.html('');
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
            item.attr("id", row.paper.value);
            //item.click(function(args){clickFunction($(args.target).attr("id"))});
            item.append(row.title.value);
            list.append(item);
        }
    }
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
        color: '#0f0',
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
        var bindings = data.results.bindings;
        var len = bindings.length;
        var circleRadius = 10;
        for(var i = 0; i < len; i++) {
            var row = bindings[i];
            graph.addNode({
                id: row.paper.value,
                x: circleRadius * Math.cos(2 * Math.PI * i / len),
                y: circleRadius * Math.sin(2 * Math.PI * i / len),
                color: '#00f',
                size: 1,
                label: row.title.value
            });
            graph.addEdge({
                id: authorUri+row.paper.value,
                source: authorUri,
                target: row.paper.value,
                size: 1,
                type:'curve'
            })
        }
        mySigma.refresh();
    }
}
function getPaperName(paperUri, graph) {
    var queryString = prefixes.RDF + prefixes.RUCD + "SELECT ?title " +
        "WHERE { " +
        "<" + paperUri + "> rucd:title ?title . " +
        "} ";
    query('http://localhost:3030/ucdrr/query', queryString, "JSON", addAuthor);
    function addAuthor(data) {
        var row = data.results.bindings[0];
        graph.nodes(paperUri)["label"] =  row.title.value;
    }
}
function getPaperAuthors(paperUri, callback) {
    var queryString = prefixes.RUCD +
        "SELECT ?author ?firstName ?lastName WHERE {\n" +
        "?author rucd:publication <" + paperUri + "> . \n" +
        "?author rucd:firstName ?firstName . " +
        "?author rucd:lastName ?lastName . " +
        "}";
    query('http://localhost:3030/ucdrr/query', queryString, "JSON", callback);
}
function displayBipartiteGraphPaper(paperUri) {
    hideSearch(true);
    var mySigma = createSigma();
    var graph = mySigma.graph;
    graph.addNode({
        id: paperUri,
        x:0,
        y:0,
        color: '#00f',
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
        var bindings = data.results.bindings;
        var len = bindings.length;
        var circleRadius = 10;
        for(var i = 0; i < len; i++) {
            var row = bindings[i];
            graph.addNode({
                id: row.author.value,
                x: circleRadius * Math.cos(2 * Math.PI * i / len),
                y: circleRadius * Math.sin(2 * Math.PI * i / len),
                color: '#0f0',
                size: 1,
                label: row.lastName.value + ", " + row.firstName.value
            });
            graph.addEdge({
                id: paperUri+row.author.value,
                source: paperUri,
                target: row.author.value,
                size: 1,
                type:'curve'
            })
        }
        mySigma.refresh();
    }
}