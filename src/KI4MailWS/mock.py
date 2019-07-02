# Mock class to be replaced by real AI module with same methods
class MockAI:
    loaded = False

    def __init__(self, config) -> None:
        super().__init__()
        MockAI.loaded = True
        print("load mock init")
        print(config['ModelPath'])

    @staticmethod
    def preprocess(subject, body, attachments):
        return "Please implement preprocessing method"

    @staticmethod
    def classify(subject, body, attachments):
        """
        Classify the given email and return the correct target for this email
        :param subject: string
        :param body: string
        :param attachments: list of dictionaries with filename and optional content as keys
        :return: target email
        """
        return "Please implement classify method"

    @staticmethod
    def error_target():
        """
        Return the default email in case an error occurs
        :return: default email
        """
        return "error-target-mail"
