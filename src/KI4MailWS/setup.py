import configparser
import logging
import os
import importlib
from src.KI4MailWS.wsdl import WSDLService
from spyne import Application
from spyne.protocol.soap import Soap11
from spyne.protocol.json import JsonDocument
from spyne.protocol.http import HttpRpc
from spyne.util.wsgi_wrapper import WsgiMounter


class Setup:

    def __init__(self, base_path, web_config, log_config) -> None:
        super().__init__()
        self.base_path = base_path.rstrip("/")
        if not web_config.startswith("/"):
            web_config = "/" + web_config

        if not log_config.startswith("/"):
            log_config = "/" + log_config

        self.web_config = self.base_path + web_config
        self.log_config = self.base_path + log_config
        self.log_name = "KI4MailWS"

    def web_service(self):
        # configure logger - if log level is set to INFO a classification statistic will be accessible
        if not os.path.isfile(self.log_config):
            logging.exception("Configuration file for logger not found at {}".format(self.log_config))
            exit(1)

        logging.config.fileConfig(self.log_config, disable_existing_loggers=False)
        logger = logging.getLogger(self.log_name)

        # check that config file exists
        if not os.path.isfile(self.web_config):
            logger.exception('Configuration file not found at ' + self.web_config)
            exit(1)

        config = configparser.ConfigParser()
        config.read(self.web_config)
        if 'wsdl-config' not in config:
            logger.exception('Error within configuration file - wsdl-config section missing')
            exit(1)

        required_keys = ['ImportClass', 'ImportFile', 'Debug', 'SoapName', 'ExtractAttachments', 'PreProcessing',
                         'LogPath', 'InitAI']
        for key in required_keys:
            if key not in config['wsdl-config'].keys():
                logger.exception('Configuration key ' + key + ' is missing')
                exit(1)

        if config['wsdl-config']['InitAi'] in ["True", "true"]:
            if "ai-config" not in config.keys():
                logger.exception("Configuration key 'ai-config' to configure parameters for AI is missing")
                exit(1)
            else:
                # add base path to all key ending on path to have full path
                for key in config["ai-config"].keys():
                    print(key)
                    if key.endswith("path"):
                        if config["ai-config"][key].startswith("/"):
                            config["ai-config"][key] = self.base_path + config["ai-config"][key]
                        else:
                            config["ai-config"][key] = self.base_path + "/" + config["ai-config"][key]

        # dynamically import AI main class via file name and class name
        try:
            ai_module = importlib.import_module(config['wsdl-config']['ImportFile'])
            ai_class = getattr(ai_module, config['wsdl-config']['ImportClass'])

            if config['wsdl-config']['InitAi'] in ["True", "true"]:
                ai_instance = ai_class(config['ai-config'])
            else:
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
                               in_protocol=HttpRpc(validator='soft'),
                               out_protocol=JsonDocument())

        # Prepare a SOAP and JSON returning web service to be started by a external wsgi implementation (gunicorn)
        # key is prefix folder/ path in url (http://127.0.0.1:8000/soap/classifiy
        return WsgiMounter({'soap': app_soap, 'json': app_json}), config['wsdl-config']['Debug'] in ["True", "true"]