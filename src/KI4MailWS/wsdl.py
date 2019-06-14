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
        success, subject, body = WSDLService.extract_eml(eml)

        if not success:
            return WSDLService.ai_module.error_target()

        attachments = []

        if WSDLService.extract_attachment:
            success, attachments = WSDLService.extract_attachments(eml)

            if not success:
                return WSDLService.ai_module.error_target()

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
        try:
            dec = base64.b64decode(eml)
            msg = BytesParser(policy=policy.default).parsebytes(dec)

            if "Subject" not in msg:
                return False, "", ""

            subject = msg.get("Subject").replace("\n", " ")
            text = msg.get_body(preferencelist=("html", "plain")).get_content()
            text = html2text(text)
            text = text.replace("\n", " ")

            return True, subject, text
        # Todo: Define correct error to catch
        except:
            return False, "", ""

    @staticmethod
    def extract_attachments(eml):
        # Todo: Implement attachment extraction
        return False, []


    @staticmethod
    def preprocessing(content):
        # one pre processing for all ai modules?
        return content
