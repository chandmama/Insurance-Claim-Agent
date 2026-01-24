from pydantic import BaseModel, Field
from typing import List

class SupportOutput(BaseModel):
    """
    Defines the structured output format for the insurance support assistant.
    """

    answer: str = Field(..., description="The main response to the user's query.")
    sources: List[str] = Field(default_factory=list, description="Relevant knowledge base sources or articles.")
    action_taken: str = Field(default="", description="Description of any actions performed (e.g., ticket creation).")

    def _str_(self):
        parts = [f"Answer: {self.answer}"]
        if self.sources:
            parts.append(f"Sources: {', '.join(self.sources)}")
        if self.action_taken:
            parts.append(f"Action Taken: {self.action_taken}")
        return "\n".join(parts)
