/**
 * Created by Diarmuid on 13/03/2016.
 */

colours.edges = {};


function displayAuthor(uri) {
    hideSearch(true);
    var mySigma = createSigma();
    getPapersAuthored(uri, displayPapers);
    var graph = mySigma.graph;
    var authorSize = 2;
    colours.authors[uri] = colours.author;
    graph.addNode({
        id: uri,
        x:0,
        y:0,
        color: colours.author,
        size: authorSize
    });
    getCoAuthorLinks();
    getAuthorName(uri, mySigma);
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
        var queryString = prefixes.RDF + prefixes.RUCD + prefixes.RDFS + "SELECT ?coauthor ?firstName ?lastName ?department (COUNT (?paper) AS ?weight) " +
            "WHERE { " +
            "<" + uri + "> rucd:cooperatesWith ?coauthor . " +
            "<" + uri + "> rucd:publication ?paper . " +
            "?coauthor rucd:publication ?paper . " +
            "?coauthor rucd:firstName ?firstName . " +
            "?coauthor rucd:lastName ?lastName . " +
            "OPTIONAL { ?coauthor rucd:affiliation ?affiliation . " +
            " ?affiliation rdfs:label ?department } . " +
            "} " +
            "GROUP BY ?coauthor ?firstName ?lastName ?department ";
        query(queryString, addCoAuthors);
    }
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
                        //color: colours.coauthorEdge,
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
                var colour = colours.coauthor;
                var department = "No Department";
                if ("department" in row) {
                    department = row["department"].value;
                }
                if(department in colours.departments) {
                    colour = colours.departments[department];
                } else {
                    var rgb = getRandomColour();
                    colour = 'rgb(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ')'
                    //colours.departments[department] = colour;
                    colours.departments.put(department, colour);
                }
                colours.authors[coauthor] = colour;
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
                        color: colour,
                        label: row.lastName.value + ", " + row.firstName.value
                    });
                } else {
                    coauth.size = size;
                    coauth.label = row.lastName.value + ", " + row.firstName.value;
                    coauth.color = colour
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
                var thisEdge = edges[rowIdy];
                colours.edges[thisEdge.id] = thisEdge.color;
                thisEdge.color = colours.opaque;
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
            var color = colours.authors[node];
            sigmaInst.graph.nodes(node).color = color;
        }
        function setEdgeColor(edge) {
            //if(edge.source == uri || edge.target == uri) {
            //    edge.color = colours.author;
            //} else {
            //    edge.color = colours.coauthorEdge;
            //}
            edge.color = colours.edges[edge.id];
        }
    }
}