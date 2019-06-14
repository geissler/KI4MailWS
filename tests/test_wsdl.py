import pytest
from src.KI4MailWS.wsdl import WSDLService
from src.KI4MailWS.mock import MockAI

@pytest.fixture
def wsdl_mock():
    #service = WSDLService
    WSDLService.ai_module = MockAI()
    return WSDLService


def test_simple(wsdl_mock):
    assert wsdl_mock.classify("", "test") == "error-target-mail"

