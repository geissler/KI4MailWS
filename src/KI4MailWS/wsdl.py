#!/usr/bin/env python
# encoding: utf8
"""
Basic SOAP based web service offering the functionality of different ai modules
"""

from spyne import rpc, ServiceBase, Unicode
import base64
from email.parser import BytesParser
from email import policy
from html2text import html2text


class WSDLService(ServiceBase):
    ai_module = None
    extract_attachment = False
    do_pre_processing = False

    @rpc(Unicode, _returns=Unicode)
    def classify(self, eml):
        """base64 encoded eml to be classified by ai module, which returns target mail address

        @param eml the to be classified encoded as base64 string
        @return the target e-mail
        """
        subject, body = WSDLService.extract_eml(eml)
        attachments = []

        if WSDLService.extract_attachment:
            attachments = WSDLService.extract_attachments(eml)

        if WSDLService.do_pre_processing:
            subject, body, attachments = WSDLService.ai_module.preprocess(subject, body, attachments)

        return WSDLService.ai_module.classify(subject, body, attachments)

    @rpc(_returns=Unicode)
    def status(self):
        """Simple health check doing nothing

        @return simple string
        """
        return "Service is up and running"

    @staticmethod
    def extract_eml(eml):
        dec = base64.b64decode(eml)
        msg = BytesParser(policy=policy.default).parsebytes(dec)

        subject = msg.get("Subject").replace("\n", " ")
        text = msg.get_body(preferencelist=("html", "plain")).get_content()
        text = html2text(text)
        text = text.replace("\n", " ")

        return subject, text

    @staticmethod
    def extract_attachments(eml):
        return False


    @staticmethod
    def preprocessing(content):
        # one pre processing for all ai modules?
        return content
