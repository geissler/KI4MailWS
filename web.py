import logging
import os
from src.KI4MailWS.setup import Setup

current_dir = os.path.realpath(__file__).replace(os.path.basename(__file__), '')
web, debug = Setup(base_path=current_dir, web_config="/conf/web.ini", log_config="/conf/log.ini").web_service()

# start simple local web-server for debugging purposes
if debug:
    if __name__ == '__main__':
        from wsgiref.simple_server import make_server

        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

        logging.info("listening to http://127.0.0.1:8000")
        logging.info("wsdl is at: http://localhost:8000/?wsdl")

        server = make_server('127.0.0.1', 8000, web)
        server.serve_forever()
