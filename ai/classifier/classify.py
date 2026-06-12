from ai.schemas.classifier import ClassifierRequest, ClassifierResponse


def classify_ticket(request: ClassifierRequest) -> ClassifierResponse:
    del request
    raise NotImplementedError(
        "Classifier logic is not implemented in the base architecture."
    )
