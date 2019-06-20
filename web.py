import configparser
import logging
import os
import importlib
from src.KI4MailWS.wsdl import WSDLService
from spyne import Application
from spyne.protocol.soap import Soap11
from spyne.protocol.json import JsonDocument
from spyne.util.wsgi_wrapper import WsgiMounter

# configure logger - if log level is set to INFO a classification statistic will be accessible
logging.config.fileConfig('conf/log.ini', disable_existing_loggers=False)
logger = logging.getLogger('KI4MailWS')

# check that config file exists
configFile = r'conf/web.ini'
if not os.path.isfile(configFile):
    logger.exception('Configuration file not found at ' + configFile)
    exit(1)

config = configparser.ConfigParser()
config.read(configFile)
if 'wsdl-config' not in config:
    logger.exception('Error within configuration file - wsdl-config section missing')
    exit(1)

requiredKeys = ['ImportClass', 'ImportFile', 'Debug', 'SoapName', 'ExtractAttachments', 'PreProcessing', 'LogPath']
for key in requiredKeys:
    if key not in config['wsdl-config'].keys():
        logger.exception('Configuration key ' + key + ' is missing')
        exit(1)

# dynamically import AI main class via file name and class name
try:
    ai_module = importlib.import_module(config['wsdl-config']['ImportFile'])
    ai_class = getattr(ai_module, config['wsdl-config']['ImportClass'])
    ai_instance = ai_class()
except ModuleNotFoundError:
    logger.exception('AI module not found - please check configuration for ImportPath, ImportFile, ImportClass')
    exit(1)

# inject ai instance and configuration parameter into web service
WSDLService.ai_module = ai_instance
WSDLService.logger = logger
WSDLService.extract_attachment = config['wsdl-config']['ExtractAttachments'] in ["True", "true"]
WSDLService.do_pre_processing = config['wsdl-config']['PreProcessing'] in ["True", "true"]
WSDLService.log_path = config['wsdl-config']['LogPath']

# prepare a SOAP web service
app_soap = Application([WSDLService], config['wsdl-config']['SoapName'],
                       in_protocol=Soap11(validator='lxml'),
                       out_protocol=Soap11())


# prepare a JSON returning web service
app_json = Application([WSDLService], config['wsdl-config']['SoapName'],
                       in_protocol=JsonDocument(validator='soft'),
                       out_protocol=JsonDocument())

# Prepare a SOAP and JSON returning web service to be started by a external wsgi implementation (gunicorn)
# key is prefix folder/ path in url (http://127.0.0.1:8000/soap/classifiy
web = WsgiMounter({
    'soap': app_soap,
    'json': app_json})

# start simple local web-server for debugging purposes
if config['wsdl-config']['Debug']:
    if __name__ == '__main__':
        from wsgiref.simple_server import make_server

        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

        logging.info("listening to http://127.0.0.1:8000")
        logging.info("wsdl is at: http://localhost:8000/?wsdl")

        server = make_server('127.0.0.1', 8000, web)
        server.serve_forever()
