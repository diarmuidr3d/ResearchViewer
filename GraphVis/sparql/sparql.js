/**
 * Created by Diarmuid.
 */

/**
 * An object that can be used to store the prefixes to be used in SPARQL queries
 * @type {Array}
 */
var prefixes = [];
prefixes.RDF = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ";
prefixes.RDFS = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ";

/**
 * The endpoint to which the SPARQL queries will be sent
 * @type {string}
 */
var endpoint;

/**
 * The format in which results of the sparql query will be sent
 * @type {string}
 */
var returnFormat = "JSON";

/**
 * Run a query on the sparql endpoint
 * @param query {string} - the query to be run
 * @param successFunction - the function that will be performed if the query returns
 */
function query(query, successFunction) {
    if(typeof endpoint === 'undefined' || endpoint == "" || typeof returnFormat === 'undefined' || returnFormat == "") {
        console.log("Query could not be completed because endpoint or return format are not defined");
    } else {
        var encodedQuery = encodeURI(query);
        encodedQuery = encodedQuery.replace(/#/g, '%23');
        encodedQuery = encodedQuery.replace(/\+/g, '%2B');
        var url = endpoint + '?query=' + encodedQuery + '&output=' + returnFormat;
        $.ajax({
            dataType: "jsonp",
            url: url,
            success: successFunction
        });
    }
}

//function update(endpoint, query) {
//    var encodedQuery = encodeURI(query);
//    var url = endpoint + "?update=" + encodedQuery;
//    $.ajax({
//        url: url
//    });
//}

/**
 * Display a table of the results in a #results DOM Element (used for testing purposes).
 * @param data - the data returned from a SPARQL Query
 */
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