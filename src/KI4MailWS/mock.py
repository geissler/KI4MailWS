# Mock class to be replaced by real AI module with same methods
class MockAI:
    @staticmethod
    def preprocess(subject, body, attachments):
        return "Please implement preprocessing method"

    @staticmethod
    def classify(subject, body, attachments):
        return "Please implement classify method"
