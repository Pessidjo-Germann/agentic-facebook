from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Persona(BaseModel):
    name: str
    age: str
    characteristics: str


class TargetAudience(BaseModel):
    personas: List[Persona]


class VisualRecommendations(BaseModel):
    color_palette: List[str]  # E.g.: ["#FF5733", "#3498DB"]
    typography: str
    image_style: str


class MarketingPlan(BaseModel):
    plan_id: str = Field(..., description="Unique plan identifier (e.g.: plan_april_2025)")
    objectives: List[str]
    target_audience: TargetAudience
    content_pillars: List[str]
    recommended_formats: List[str]
    frequency: str
    optimal_days: List[str]
    tone: str
    visual_recommendations: VisualRecommendations
    KPIs: List[str]
