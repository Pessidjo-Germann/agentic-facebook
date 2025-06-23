# models/persona_models.py
from pydantic import BaseModel, Field

class PagePersona(BaseModel):
    """Defines the inferred persona for the Facebook page."""
    target_audience: str = Field(
        ...,
        description="Detailed and specific description of the page's primary and secondary target audience (e.g., demographics, interests, needs, level of knowledge on the subject)."
    )
    desired_tone: str = Field(
        ...,
        description="Description of the tone and communication style to adopt. Include keywords (e.g., Inspiring, Technical, Accessible, Humorous, Empathetic, Formal, Informal)."
    )
    page_subject: str = Field(
        ...,
        description="Detailed description of the page's main subject, its specific mission, and the type of value it intends to bring to its audience."
    )