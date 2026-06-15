from ai.classifier.classify import classify_ticket
from ai.schemas.classifier import ClassifierRequest, ClassifierResponse


class ClassifierService:
    def classify(self, request: ClassifierRequest) -> ClassifierResponse:
        return classify_ticket(request)
