from pydantic import BaseModel, Field, field_validator, validator
from typing import List, Literal

VALID_POST_TYPES = [
    "Welcome", # Probably used only on the first day
    "Inspirational Quote",
    "Engaging Question",
    "Simple Technical Tip",
    "Share Useful Resource",
    "Simple Poll",
    "Behind the Scenes/Dev Humor",
    "Promote External Content",
    "Product/Service Update",
    "Week Recap", # New potential type
    "Monday Motivation", # New potential type
    # Add other relevant types
]

TimeSlot = Literal["morning", "noon", "afternoon", "evening"]
DayOfWeek = Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
class PostDetail(BaseModel):
    """Defines the details of a SINGLE scheduled post."""
    suggested_time_slot: TimeSlot = Field(
        ...,
        description="Suggested time slot for this specific post (morning, noon, afternoon, evening)."
    )
    post_type: str = Field(
        ...,
        description=f"The type of content for this post. Choose from: {', '.join(VALID_POST_TYPES)}."
    )
    topic_suggestion: str = Field(
        ...,
        description="Suggestion for a specific and concise topic/angle for this post.",
        min_length=5
    )

    @field_validator('post_type')
    def check_valid_post_type(cls, value):
        """Validates that the post_type is in the allowed list."""
        if value not in VALID_POST_TYPES:
            raise ValueError(f"post_type '{value}' is not valid. Choose from: {', '.join(VALID_POST_TYPES)}")
        return value

class DailySchedule(BaseModel):
    """Defines the posting schedule for ONE day."""
    day: int = Field(..., description="The day number in the week (1 to 7).", ge=1, le=7)
    posts: List[PostDetail] = Field(
        ...,
        description="List of posts scheduled for this day. Must contain at least 3 posts.",
        min_length=3 
    )

    @field_validator('posts')
    def check_time_slots_are_reasonable(cls, posts):
        """Checks that there are not too many posts in the same time slot (optional but useful)."""
        time_slots = [post.suggested_time_slot for post in posts]
       
        if any(time_slots.count(slot) > 2 for slot in set(time_slots)):
            print(f"Warning: More than 2 posts suggested for the same time slot on day {getattr(cls, 'day', '?')}.") # cls.day is not easily accessible here
            # Could raise an error if strict: raise ValueError("Too many posts in the same time slot.")
        return posts


from pydantic import BaseModel, Field,ConfigDict 
from typing import List, Optional

# First, let's define a model for a single content item
class ContentItem(BaseModel):
    title: str = Field(description="Catchy title for the content")
    description: str = Field(description="Brief description of the content")
    hashtags: List[str] = Field(description="Relevant hashtags for this content")
    model_config = ConfigDict(extra='forbid')

# Now, let's define a model for a single day's schedule
class DaySchedule(BaseModel):
    # Remove the minimum constraint and use Field validation instead
    day: str = Field(description="Day of the week (Monday, Tuesday, etc.)")
    content_items: List[ContentItem] = Field(description="List of content to be published on this day")
    best_time: str = Field(description="Best time of day to post")
    model_config = ConfigDict(extra='forbid')

# Finally, the complete weekly schedule
class WeeklyScheduleOutput(BaseModel):
    week_theme: str = Field(description="General theme for the week")
    daily_schedule: List[DaySchedule] = Field(description="Daily schedule for each day of the week")
    notes: Optional[str] = Field(None, description="Additional notes or tips for this strategy")
    model_config = ConfigDict(extra='forbid')

    @field_validator('daily_schedule')
    def check_days_are_sequential_and_unique(cls, schedule):
        """Checks that all days of the week are present exactly once."""
        expected_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days = [item.day for item in schedule]
        if sorted(list(set(days))) != sorted(expected_days):
             raise ValueError("The schedule must contain exactly all days of the week, once each.")
        return schedule

class DailyStrategy(BaseModel):
    """Defines the content plan for ONE day."""
    day: DayOfWeek = Field(..., description="The day of the week (e.g., 'Monday', 'Tuesday', etc.).")
    content_items: List[ContentItem] = Field(
        ...,
        description="List of content items scheduled for this day. Must contain at least 3.",
        min_length=3 # Enforce at least 3 posts per day
    )
    # Made optional because the initial JSON example had it, but can be omitted if not used
    best_time: Optional[TimeSlot] = Field(None, description="Globally recommended time slot for this day (optional).")
    model_config = ConfigDict(extra='forbid')

class FullStrategyOutput(BaseModel):
    """Complete structure of the strategy.json file."""
    # Optional if the LLM does not always generate it
    week_theme: Optional[str] = Field(None, description="General theme for the week (optional).")
    daily_schedule: List[DailyStrategy] = Field(
        ...,
        description="List containing the schedules for each of the 7 days of the week.",
        min_length=7,
        max_length=7 # Ensures there are exactly 7 days
    )
    # Optional
    notes: Optional[str] = Field(None, description="Additional notes on the strategy (optional).")
    model_config = ConfigDict(extra='forbid')

    @field_validator('daily_schedule')
    def check_days_are_unique_and_present(cls, schedule):
        """Checks that all days of the week are present exactly once."""
        days_present = {item.day for item in schedule}
        all_days = set(DayOfWeek.__args__) # Gets all possible values from the Literal

        if len(days_present) != 7:
            raise ValueError(f"The schedule must contain exactly 7 unique days. Days found: {days_present}")
        if days_present != all_days:
             missing = all_days - days_present
             extra = days_present - all_days
             errors = []
             if missing: errors.append(f"Missing days: {missing}")
             if extra: errors.append(f"Invalid or duplicate days: {extra}")
             raise ValueError(f"Error in schedule days: {'; '.join(errors)}")
        return schedule

