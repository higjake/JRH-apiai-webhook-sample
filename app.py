#!/usr/bin/env python
from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json
import os
import time
from flask import Flask
from flask import request
from flask import make_response

actionMap = {
    'nextResult': {
        'speech1': 'Our top provider in your area is ',
        'speech2': 'Our second best provider in your area is ',
        'key': 'business_name',
        'count': 3
    },
    'getNumber': {
        'speech': 'The phone number for that business is ',
        'key': 'phone',
        'count': 1
    },
    'getWebsite': {
        'speech': '%s. Would you like to get the phone number?',
        'key': 'snippet',
        'count': 1
    }
}

# Flask app should start in global layout
app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def webhook():
    start = time.time()
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    end = time.time()
    print('Duration: {:10.4f} seconds'.format(end - start))
    return r
def processRequest(req):
    action = req.get("result").get("action")
    contexts = req.get("result").get("contexts")
    resultnumber = contexts[0].get("name")
    print(resultnumber)
    baseurl = "https://www.expertise.com/api/v1.0/directories/"
    url_query = makeQuery(req)
    if url_query is None:
        return {}
    final_url = baseurl + url_query
    print(final_url)
    #final_url = baseurl + urlencode({url_query})
    #final_url = "https://www.expertise.com/api/v1.0/directories/ga/atlanta/flooring"
    result = urlopen(final_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data, action, resultnumber)
    return res
def makeQuery(req):
    result = req.get("result")
    contexts = result.get("contexts")
    parameters = contexts[0].get("parameters")
    state = parameters.get("state")
    city = parameters.get("city")
    vert = parameters.get("vertical")
    if state is None:
        return None
    
    return state + "/" + city + "/" + vert

def makeWebhookResult(data, action, resultnumber):
    providers = data.get('providers')
    if providers is None:
        return {}
    
    # print(json.dumps(item, indent=4))
    providers = data.get('providers') # Adding this line as a sanity check
    speech = actionMap[action]['speech1'] + providers[0].get('business_name') + '. Would you like the phone number or website, or to hear our next result?';
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
