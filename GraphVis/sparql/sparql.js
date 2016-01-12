/**
 * Created by diarmuid on 06/01/16.
 */

var prefixes = [];
prefixes.RDF = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ";

function query(endpoint, query, format, successFunction) {
    var encodedQuery = encodeURI(query);
    //console.log("Query");
    //console.log(encodedQuery);
    encodedQuery = encodedQuery.replace(/#/g,'%23');
    //console.log(encodedQuery);
    var url = endpoint + '?query=' + encodedQuery + '&output=' + format;
    //console.log("URL");
    //console.log(url);
    //console.log(decodeURI(url));
    $.ajax({
        dataType: "jsonp",
        url: url,
        success: successFunction
    });
}

//function update(endpoint, query) {
//    var encodedQuery = encodeURI(query);
//    var url = endpoint + "?update=" + encodedQuery;
//    $.ajax({
//        url: url
//    });
//}

function displayTable(data) {
    var table = $("#results");
    var headerVars = data.head.vars;
    var trHeaders = getTableHeaders(headerVars);
    table.append(trHeaders);
    var bindings = data.results.bindings;
    for(rowIdx in bindings){
        table.append(getTableRow(headerVars, bindings[rowIdx]));
    }

    function getTableHeaders(headerVars) {
        var trHeaders = $("<tr></tr>");
        for(var i in headerVars) {
            trHeaders.append("<th>" + headerVars[i] + "</th>");
        }
        return trHeaders;
    }

    function getTableRow(headerVars, rowData) {
        var tr = $("<tr></tr>");
        for(var i in headerVars) {
            tr.append(getTableCell(headerVars[i], rowData));
        }
        return tr;
    }

    function getTableCell(fieldName, rowData) {
        var td = $("<td></td>");
        var fieldData = rowData[fieldName];
        td.html(fieldData["value"]);
        return td;
    }
}

function displayTypeCentricGraph(typeUri, linkUri, endpoint) {
    var s;

    var queryString = prefixes + "SELECT ?sub ?obj " +
        "WHERE { ?sub rdf:type <" + typeUri + "> . ?obj rdf:type <" + typeUri + "> . " +
        "?sub <" + linkUri + "> ?obj . " +
        "}";
    query(endpoint, queryString, "JSON", visualise);

    function visualise(data) {
        //var sigma = new sigma({
        //    renderer: {
        //        container: document.getElementById('graph   '),
        //        type: 'canvas'
        //    }
        //});
        s = new sigma('graph');
        var graph = s.graph;
        console.log(graph);
        var bindings = data.results.bindings;
        console.log(bindings);
        for(var rowId in bindings) {
            var row = bindings[rowId];
            console.log(row);
            var sub = row["sub"].value;
            var obj = row["obj"].value;
            addANode(sub, graph);
            addANode(obj, graph);
            s.refresh();
            graph.addEdge({
                id: rowId,
                source: sub.value,
                target: obj.value
            });
        }
        s.startForceAtlas2({worker: true, barnesHutOptimize: false});

        function addANode(cell, graph) {
            console.log(cell);
            try {
                graph.addNode({
                    id: cell,
                    x:0,
                    y:0,
                    size: 1
                });
            } catch (e) {
                console.log(e);
            }
        }
    }
}