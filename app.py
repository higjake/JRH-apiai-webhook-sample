#!/usr/bin/env python
from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json
import os
from flask import Flask
from flask import request
from flask import make_response
# Flask app should start in global layout
app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
def processRequest(req):
    baseurl = "https://www.expertise.com/api/v1.0/directories/"
    url_query = makeQuery(req)
    if url_query is None:
        return {}
    final_url = baseurl + url_query
    #final_url = baseurl + urlencode({url_query})
    #final_url = "https://www.expertise.com/api/v1.0/directories/ga/atlanta/flooring"
    result = urlopen(final_url).read()
    data = json.loads(result)
    return {
        "speech": "fail",
        "displayText": "fail",
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
def makeQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    state = parameters.get("state")
    city = parameters.get("city")
    vert = parameters.get("profession")
    if state is None:
        return None
    
    return state + "/" + city + "/" + vert

def makeWebhookResult(data):
    providers = data.get('providers')
    if providers is None:
        return {}
    
    # print(json.dumps(item, indent=4))
    speech = "The top three providers in your area are " + providers[0].get('business_name') + ", " + providers[1].get('business_name') + ", and " + providers[2].get('business_name') + "." 
    print("Response:")
    print(speech)
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
