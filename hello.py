from flask import Flask, render_template, request, jsonify
from ibmcloudant.cloudant_v1 import Document, CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import atexit
import os
import json

app = Flask(__name__, static_url_path='')

db_name = 'mydb'
service = None
 
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        apikey = creds['apikey']
        url = 'https://' + creds['host']
        authenticator = IAMAuthenticator(apikey)
        service = CloudantV1(authenticator=authenticator)
        service.set_service_url(url)
elif "CLOUDANT_URL" in os.environ:
    apikey = os.environ['CLOUDANT_APIKEY']
    url = os.environ['CLOUDANT_URL']
    authenticator = IAMAuthenticator(apikey)
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url(url)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        apikey = creds['apikey']
        url = 'https://' + creds['host']
        authenticator = IAMAuthenticator(apikey)
        service = CloudantV1(authenticator=authenticator)
        service.set_service_url(url)


# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def root():
    return app.send_static_file('index.html')

# /* Endpoint to greet and add a new visitor to database.
# * Send a POST request to localhost:8000/api/visitors with body
# * {
# *     "name": "Bob"
# * }
# */
@app.route('/api/visitors', methods=['GET'])
def get_visitor():
    if service:
        response = service.post_all_docs(db=db_name).get_result()
        print(response)
        return(response)
    else:
        print('No database')
        return jsonify([])

# /**
#  * Endpoint to get a JSON array of all the visitors in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */
@app.route('/api/visitors', methods=['POST'])
def put_visitor():
    user = request.json['name']
    data = {'name':user}
    if service:
        db_docs = Document(name=user)
        response = service.post_document(db=db_name, document=db_docs).get_result()
        print(response)
        return jsonify(data)
    else:
        print('No database')
        return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
