from pydantic import BaseModel, Field

class UserPromptResponse(BaseModel):
    """
    Response model for user prompt operations.
    """
    prompt: str = Field(..., description="The prompt text provided by the user.")
    response: str = Field(..., description="The response generated based on the user's prompt.")