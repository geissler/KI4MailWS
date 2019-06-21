#!/usr/bin/env python
# encoding: utf8
"""
Basic based web service offering the functionality of different ai modules via SOAP or JSON
"""

import base64
import logging
import os
from spyne import rpc, ServiceBase, Unicode, Iterable
from email.parser import BytesParser
from email import policy
from html2text import html2text


class WSDLService(ServiceBase):
    ai_module = None
    extract_attachment = None
    do_pre_processing = None
    logger = None
    log_path = None

    @rpc(Unicode, _returns=Unicode)
    def classify(ctx, eml):
        """base64 encoded eml to be classified by ai module, which returns target mail address

        @param eml the to be classified encoded as base64 string
        @return the target e-mail
        """
        success, message = WSDLService.get_message(eml)
        if not success:
            WSDLService.logger.error("Error while encoding *.eml")
            WSDLService.logger.info(WSDLService.ai_module.error_target())
            return WSDLService.ai_module.error_target()

        success, subject, body = WSDLService.extract_eml(message)
        if not success:
            WSDLService.logger.error("Error while parsing *.eml")
            WSDLService.logger.info(WSDLService.ai_module.error_target())
            return WSDLService.ai_module.error_target()

        attachments = []
        if WSDLService.extract_attachment is True:
            success, attachments = WSDLService.extract_attachments(message)

            if success is False:
                WSDLService.logger.error("Error while extracting attachments")
                WSDLService.logger.info(WSDLService.ai_module.error_target())
                return WSDLService.ai_module.error_target()

        if WSDLService.do_pre_processing is True:
            subject, body, attachments = WSDLService.ai_module.preprocess(subject, body, attachments)

        classification = WSDLService.ai_module.classify(subject, body, attachments)
        logging.info(classification)
        return classification

    @rpc(_returns=Unicode)
    def status(ctx):
        """Simple health check doing nothing

        @return simple string
        """
        return "Service is up and running"

    @rpc(_returns=Iterable(Unicode))
    def stats(ctx):
        """
        Return an overview of the classification results logged within the log files
        @return dictionary with dates and counts of mail addresses returned for each day
        :return:
        """
        if os.path.isdir(WSDLService.log_path) is False:
            WSDLService.logger.error("Path to log files not set correctly! Given folder {} does not exist".format(WSDLService.log_path))
            yield {}

        result = {}
        directory = os.fsencode(WSDLService.log_path)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".log"):
                file_content = open(os.path.join(WSDLService.log_path, filename), "r")
                for row in file_content:
                    if "INFO" in row and "@gothaer" in row:
                        date = row[0:10]
                        if date not in result:
                            result[date] = {}

                        mail = row.split(" - ")[2].replace("\n", "").replace("\r", "")
                        if mail not in result[date]:
                            result[date][mail] = 0

                        result[date][mail] = result[date][mail] + 1

        yield result

    @staticmethod
    def get_message(eml):
        try:
            return True, BytesParser(policy=policy.default).parsebytes(base64.b64decode(eml))
        # Todo: Define correct error to catch
        except:
            return False, ""

    @staticmethod
    def extract_eml(message):
        try:
            if "Subject" not in message:
                return False, "", ""

            subject = message.get("Subject").replace("\n", " ")
            text = message.get_body(preferencelist=("html", "plain")).get_content()
            text = html2text(text)
            text = text.replace("\n", " ")

            return True, subject, text
        # Todo: Define correct error to catch
        except:
            return False, "", ""

    @staticmethod
    def extract_attachments(message, filename_only=True):
        attachments = []
        supported_file_types = ["application/pdf"]

        for i in range(len(message.get_payload())):
            attachment = message.get_payload()[i]
            if attachment.get_filename() is not None:
                if attachment.get_content_type() not in supported_file_types or filename_only is True:
                    attachments.append({
                        "filename": attachment.get_filename(),
                        "content": ""
                    })
                else:
                    # Todo: parse attachment
                    attachments.append({
                        "filename": attachment.get_filename(),
                        "content": attachment.get_payload(decode=True)
                    })

        return True, attachments


    @staticmethod
    def preprocessing(subject, body, attachments):
        # Todo: check if one pre processing for all ai modules is required?
        return subject, body, attachments
