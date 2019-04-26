import json
import logging
import os
from pathlib import Path

from flasgger import Swagger
from flasgger.utils import swag_from
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS

from dgds_backend import error_handler
from dgds_backend.dgds_pi_service_ddl import PiServiceDDL

app = Flask(__name__)
Swagger(app)
CORS(app)

# Configuration load
app.register_blueprint(error_handler.error_handler)
app.config.from_object('dgds_backend.default_settings')
try:
    app.config.from_envvar('DGDS_BACKEND_SETTINGS')
except Exception as e:
    print('Could not load config from environment variables')  # logging not set yet [could not read config]

# Logging setup
if not app.debug:
    from logging.handlers import TimedRotatingFileHandler

    # https://docs.python.org/3.6/library/logging.handlers.html#timedrotatingfilehandler
    file_handler = TimedRotatingFileHandler(os.path.join(app.config['LOG_DIR'], 'dgds_backend.log'), 'midnight')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter('<%(asctime)s> <%(levelname)s> %(message)s'))
    app.logger.addHandler(file_handler)

# Load general settings
APP_DIR = Path(os.path.dirname(os.path.realpath(__file__)))

# Dataset settings
try:
    DATASETS = {}
    fnameDatasets = Path(APP_DIR / 'config_data' / 'datasets.json')
    fnameAccess = Path(APP_DIR / 'config_data' / 'datasets_access.json')
    with open(str(fnameDatasets), 'r') as fd:
        DATASETS['info'] = json.load(fd)  # str for python 3.4, works without on 3.6+
    with open(str(fnameAccess), 'r') as fa:
        DATASETS['access'] = json.load(fa)  # str for python 3.4, works without on 3.6+
except Exception as e:
    logging.error('Missing datasets.json %s /datasets_access.json %s, please check your deployment settings',
                  (fnameDatasets, fnameAccess))
    exit(-1)  # vital config needed


# Get the associated service url to a dataset inside the params dict
def get_service_url(params):
    """
    Get dataset identification
    :param params:
    :return:
    """
    service_url = None
    protocol = None
    status = 200
    msg = {}
    try:
        if 'datasetId' in params:
            service_url = DATASETS['access'][params['datasetId']]['urlData']
            protocol = DATASETS['access'][params['datasetId']]['protocolData']
        else:
            msg = 'No datasetId specified in the request'
            raise error_handler.InvalidUsage(msg)
    except Exception as e:
        msg = 'The provided datasetId does not exist'
        raise error_handler.InvalidUsage(msg)

    return msg, status, service_url, protocol


@app.route('/locations', methods=['GET'])
@swag_from('locations.yaml')
def locations():
    """
    Query locations
    :return:
    """
    # Read input [JSON] - Parameters from url
    input = request.args.to_dict(flat=True)

    # Get dataset identification
    msg, status, pi_service_url, protocol = get_service_url(input)
    if status > 200:
        return jsonify(msg)

    # Query PiService
    pi = PiServiceDDL(pi_service_url, request.url_root)
    content = {}
    try:
        content = pi.get_locations(input)
    except Exception as e:
        content = {'error': 'The PiService-DDL failed to serve the response. Please try again later'}
        logging.error('The PiService-DDL failed to serve the response. Please try again later')

    return jsonify(content)


# Dummy locations - /dummylocations
@app.route('/dummylocations', methods=['GET'])
def dummyLocations():
    """
    Dummy locations
    :return:
    """
    # Return dummy file contents
    with open(os.path.join(APP_DIR, 'dummy_data/dummyLocations.json')) as f:
        content = json.load(f)
    return jsonify(content)


@app.route('/timeseries', methods=['GET'])
def timeseries():
    """
    Timeseries query
    :return:
    """
    # Read input [JSON] - Parameters from url
    input = request.args.to_dict(flat=True)

    # Get dataset identification
    msg, status, pi_service_url, protocol = get_service_url(input)
    if status > 200:
        return jsonify(msg)

    # Query PiService
    pi = PiServiceDDL(pi_service_url, request.url_root)
    content = {}
    try:
        content = pi.get_timeseries(input)
    except Exception as e:
        content = {'error': 'The PiService-DDL failed to serve the response. Please try again later'}
        logging.error('The PiService-DDL failed to serve the response. Please try again later')

    return jsonify(content)


@app.route('/dummytimeseries', methods=['GET'])
def dummyTimeseries():
    """
    Dummy timeseries
    :return:
    """
    # Return dummy file contents
    with open(os.path.join(APP_DIR, 'dummy_data/dummyTseries.json')) as f:
        content = json.load(f)
    return jsonify(content)


# Datasets query / all
@app.route('/datasets', methods=['GET'])
def datasets():
    """
    Datasets
    :return:
    """
    # Return dummy file contents
    input = request.args.to_dict(flat=True)
    return jsonify(DATASETS['info'])


@app.route('/', methods=['GET'])
def root():
    """
    Redirect default page to API docs.
    :return:
    """
    msg = 'Welcome to DGDS'
    # print('redirecting ...')
    # return redirect(request.url + 'apidocs')
    return msg


def main():
    # initialize_app(app)
    # log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(debug=True)


if __name__ == "__main__":
    main()