import pytest
import os
import base64
import logging
from src.KI4MailWS.wsdl import WSDLService
from src.KI4MailWS.mock import MockAI

success_msg = "Please implement classify method"
error_msg = "error-target-mail"
test_dir = os.path.join(os.path.realpath(__file__).replace(os.path.basename(__file__), ''), "data")
success_files = "success_"


@pytest.fixture
def wsdl_mock():
    WSDLService.ai_module = MockAI()
    WSDLService.logger = logging.getLogger()
    WSDLService.log_path = "log/"
    return WSDLService


def test_error_simple(wsdl_mock):
    assert wsdl_mock.classify("", "test") == "error-target-mail"


def test_success_files(wsdl_mock):
    directory = os.fsencode(test_dir)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith(success_files):
            file_object = open(test_dir + "/" + filename, "r")
            content = base64.b64encode(file_object.read().encode())

            assert wsdl_mock.classify("", content) == success_msg, "Error within test file {}".format(filename)


def test_extract_eml(wsdl_mock):
    file_object = open(test_dir + "/success_small_01.eml", "r")
    content = base64.b64encode(file_object.read().encode())
    status, message = wsdl_mock.get_message(content)
    assert status is True
    status, subject, body = wsdl_mock.extract_eml(message)
    assert status is True
    assert subject == "Test EML"
    assert body.strip() == "Diese ist der Body"


def test_error_while_extracting(wsdl_mock):
    file_object = open(test_dir + "/success_small_01.eml", "r")
    content = base64.b64encode(file_object.read().encode())
    status, message = wsdl_mock.get_message(content[:-1])
    assert status is False
    assert message == ""


def test_extract_attachment(wsdl_mock):
    file_object = open(test_dir + "/success_medium_01.eml", "r")
    content = base64.b64encode(file_object.read().encode())
    status, message = wsdl_mock.get_message(content)
    assert status is True
    status, attachments = wsdl_mock.extract_attachments(message)
    assert status is True


def test_stats_via_log(wsdl_mock):
    generator = wsdl_mock.stats(wsdl_mock)
    # generator needs to be converted to dict for testing
    stats = {}
    for key in generator:
        stats.update(key)

    assert '2019-06-20' in stats
    assert 'schaden@gothaer.de' in stats['2019-06-20']
    assert 'gkc-koeln@gothaer.de' in stats['2019-06-20']
    assert 'info@gothaer.de' in stats['2019-06-20']
    assert stats['2019-06-20']['schaden@gothaer.de'] == 1
    assert stats['2019-06-20']['gkc-koeln@gothaer.de'] == 3
    assert stats['2019-06-20']['info@gothaer.de'] == 1
    assert '2019-06-21' in stats
    assert 'lv_service@gothaer.de' in stats['2019-06-21']
    assert 'info@gothaer.de' not in stats['2019-06-21']
    assert 'gkc-koeln@gothaer.de' not in stats['2019-06-21']
    assert 'schaden@gothaer.de' not in stats['2019-06-21']
    assert stats['2019-06-21']['lv_service@gothaer.de'] == 1


def test_no_stats(wsdl_mock):
    wsdl_mock.log_path = "data/"
    generator = wsdl_mock.stats(wsdl_mock)
    # generator needs to be converted to dict for testing
    stats = {}
    for key in generator:
        stats.update(key)

    assert len(stats) == 0


def test_extract_pdf(wsdl_mock):
    file_object = open(test_dir + "/attachment_pdfa.eml", "r")
    content = base64.b64encode(file_object.read().encode())
    status, message = wsdl_mock.get_message(content)
    assert status is True
    status, attachments = wsdl_mock.extract_attachments(message, True)
    assert status is True
    assert len(attachments) == 1
    assert attachments[0]["filename"] == "example_065.pdf"


def test_extract_multiple(wsdl_mock):
    file_object = open(test_dir + "/multiple_attachments.eml", "r")
    content = base64.b64encode(file_object.read().encode())
    status, message = wsdl_mock.get_message(content)
    assert status is True
    status, attachments = wsdl_mock.extract_attachments(message, True)
    assert status is True
    assert len(attachments) == 3
    assert attachments[0]["filename"] == "Mappe1.xlsx"
    assert attachments[1]["filename"] == "Dokument2.docx"
    assert attachments[2]["filename"] == "example_065.pdf"
