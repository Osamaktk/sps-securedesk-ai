from ai.schemas.summariser import SummariserRequest, SummariserResponse


def summarise_text(request: SummariserRequest) -> SummariserResponse:
    del request
    raise NotImplementedError(
        "Summariser logic is not implemented in the base architecture."
    )
