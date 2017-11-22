import csv
import sys
import simplejson as json
from fuzzywuzzy import fuzz
from flask import Flask, request, jsonify
from collections import OrderedDict
from operator import itemgetter

app = Flask(__name__)


# Matching threshold.
match_threshold = 70

# Basic service metadata. There are a number of other documented options
# but this is all we need for a simple service.
metadata = {
    "name": "GODOT (Graph of Dated Objects and Texts) Reconciliation Service - Roman Consulates",
    "defaultTypes": [{"id": "/people/person", "name" : "Person"}],
    "view": {"url": "https://godot.date/id/{{id}}"},
    "preview": {"url": "https://godot.date/reconcile/preview={{id}}"}
    }

# Read in person records from csv file.
reader = csv.DictReader(open('Consulate_URIs.tsv', 'rt'), delimiter='\t')
records = [r for r in reader]



def search(query):

    # Initialize matches.
    matches = []
    # Search person records for matches.
    for r in records:
        score = fuzz.partial_ratio(query, r['consul_names'])
        if score > match_threshold:
            if int(r['not_before']) < 0:
                not_before = str(int(r['not_before']) * - 1) + " BC"
            else:
                not_before = r['not_before'] + " AD"
            if int(r['not_after']) < 0:
                not_after = str(int(r['not_after']) * - 1) + " BC"
            else:
                not_after = r['not_after'] + " AD"
            matches.append({
                "id": r['godot_uri'],
                "name": r['consul_names'] + " (" + not_before + " - " + not_after  + ")",
                "score": score,
                "match": query == r['consul_names'],
                "type": [{"id": "/people/person", "name": "Person"}]
                })
    # sort matches by score & return orderedDict
    ordered_matches = OrderedDict()
    ordered_matches = sorted(matches, key=itemgetter('score'), reverse=True)
    return ordered_matches


def jsonpify(obj):
    """
    Like jsonify but wraps result in a JSONP callback if a 'callback'
    query param is supplied.
    """
    try:
        callback = request.args['callback']
        response = app.make_response("%s(%s)" % (callback, json.dumps(obj)))
        response.mimetype = "text/javascript"
        return response
    except KeyError:
        return jsonify(obj)


@app.route("/reconcile/preview", methods=['POST', 'GET'])
def preview():
    id = request.args.get('id')
    if id:
        for r in records:
            uri_query = "https://godot.date/id/" + id
            if r['godot_uri'] == uri_query:
                if int(r['not_before']) < 0:
                    not_before = str(int(r['not_before']) * - 1) + " BC"
                else:
                    not_before = r['not_before'] + " AD"
                if int(r['not_after']) < 0:
                    not_after = str(int(r['not_after']) * - 1) + " BC"
                else:
                    not_after = r['not_after'] + " AD"
                wikidata_uri = ""
                if r['wikidata_uri_1'] != "":
                    wikidata_uri = "<a href=\"r['wikidata_uri_1']\">" + r['wikidata_uri_1'] + "</a> "
                if r['wikidata_uri_2'] != "":
                    wikidata_uri += "<a href=\"r['wikidata_uri_2']\">" + r['wikidata_uri_2'] + "</a>"
                if wikidata_uri != "":
                    wikidata_uri = "<p><b>Wikidata URI(s)</b>: " + wikidata_uri + "</p>"
                htmlBuffer = """
                <html><body><h1>""" + id + """</h1>
                <p><b>names</b>: """ + r['consul_names'] + """</p>
                <p><b>date</b>: """ + not_before + " &ndash; " + not_after + """</p>
                """ + wikidata_uri + """
                </body></html>
                """
                return htmlBuffer
        return "<html><body><p>Error: ID " + uri_query + " not found.</p></body></html>"



@app.route("/reconcile", methods=['POST', 'GET'])
def reconcile():
    # If a single 'query' is provided do a straightforward search.
    query = request.args.get('query')
    results = OrderedDict()
    if query:
        # If the 'query' param starts with a "{" then it is a JSON object
        # with the search string as the 'query' member. Otherwise,
        # the 'query' param is the search string itself.
        if query.startswith("{"):
            query = json.loads(query)['query']
        results = search(query)
        return jsonpify({"result": results})

    # If a 'queries' parameter is supplied then it is a dictionary
    # of (key, query) pairs representing a batch of queries. We
    # should return a dictionary of (key, results) pairs.
    queries = request.form.get('queries')
    if queries:
        queries = json.loads(queries)
        results = {}
        for (key, query) in queries.items():
            results[key] = {"result": search(query['query'])}
        return jsonpify(results)

    # If neither a 'query' nor 'queries' parameter is supplied then
    # we should return the service metadata.
    return jsonpify(metadata)



