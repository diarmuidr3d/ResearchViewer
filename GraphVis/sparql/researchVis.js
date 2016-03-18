prefixes.RUCD = "PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#> ";

var domElements = {};
domElements.graph = 'graph';
domElements.paperList = 'papers';
//endpoint = 'http://localhost:3030/ucdrr2/query';
endpoint = 'http://localhost:3030/rucd2/query';
var colours={};
colours.author = '#093';
colours.authors = {};
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



function finish(mySigma) {
    mySigma.refresh();
    sigma.layouts.fruchtermanReingold.start(mySigma, {autoArea: true});
    mySigma.refresh();
    console.log("Layout finished");
}


function getAuthorName(uri, mySigma) {
    var queryString = prefixes.RDF + prefixes.RUCD + prefixes.RDFS + "SELECT ?firstName ?lastName ?department " +
        "WHERE { " +
        "<" + uri + "> rucd:firstName ?firstName . " +
        "<" + uri + "> rucd:lastName ?lastName . " +
        "OPTIONAL { <" + uri + "> rucd:affiliation ?affiliation . " +
        " ?affiliation rdfs:label ?department } . " +
        "} ";
    console.log(queryString);
    query(queryString, addAuthor);
    function addAuthor(data) {
        var graph = mySigma.graph;
        var row = data.results.bindings[0];
        console.log(row);
        graph.nodes(uri)["label"] =  row.lastName.value + ", " + row.firstName.value;
        var colour = colours.author;
        var department = "No Department";
        if ("department" in row) {
            department = row["department"].value;
        }
        if (!(colours.departments == undefined)) {
            if (department in colours.departments) {
                colour = colours.departments[department];
            } else {
                var rgb = getRandomColour();
                colour = 'rgb(' + rgb[0] + "," + rgb[1] + "," + rgb[2] + ")";
                //colours.departments[department] = colour;
                colours.departments.put(department, colour);
            }
        }
        colours.authors[uri] = colour;
        graph.nodes(uri).color = colour;
        mySigma.refresh();
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


function getRandomColour() {
    var r = getRandomInt(0, 255);
    var g = getRandomInt(0, 255);
    var b = getRandomInt(0, 255);
    return [r,g,b];
}

// From Mozilla Developer Network: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random
// Returns a random integer between min (included) and max (excluded)
// Using Math.round() will give you a non-uniform distribution!
function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min)) + min;
}