from pydantic import BaseModel, Field


class CompleteOrEscalate(BaseModel):
    """
    Tool for an assistant to mark the current task as completed or to escalate
    control of the dialog to the primary assistant.
    """

    cancel: bool = Field(
        default=True, description="Whether to cancel the current assistant and return to the primary assistant."
    )
    reason: str = Field(description="The reason for completing or continuing the task.")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "cancel": True,
                    "reason": "User changed their mind about the current task.",
                },
                {
                    "cancel": True,
                    "reason": "I have fully completed the task.",
                },
                {
                    "cancel": False,
                    "reason": "I can try searching in another database.",
                },
            ]
        }


class ToSpendingAssistant(BaseModel):
    """
    Tool to transfer the conversation to the specialized spending assistant
    that handles billing inquiries.
    """

    request: str = Field(
        description="Any necessary followup questions the spending assistant should clarify before proceeding."
    )


class ToRecommendationAssistant(BaseModel):
    """
    Tool to transfer the conversation to the specialized recommendation assistant
    that helps users find the most suitable electricity plan.
    """

    request: str = Field(
        description="Any necessary followup questions the recommendation assistant should clarify before proceeding."
    )
