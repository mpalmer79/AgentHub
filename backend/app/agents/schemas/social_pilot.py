from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, boolean_prop, array_string_prop


def get_social_pilot_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for SocialPilotAI"""
    return [
        create_tool_schema(
            name="create_post",
            description="Create a social media post draft",
            properties={
                "content": string_prop("The post content/caption"),
                "platform": string_prop("Platform: facebook, instagram, linkedin, twitter"),
                "media_url": string_prop("Optional URL to image/video"),
                "link": string_prop("Optional link to include"),
                "hashtags": array_string_prop("List of hashtags to add"),
            },
            required=["content", "platform"]
        ),
        create_tool_schema(
            name="schedule_content",
            description="Schedule a post for future publishing",
            properties={
                "content": string_prop("The post content"),
                "platform": string_prop("Platform: facebook, instagram, linkedin, twitter"),
                "scheduled_time": string_prop("ISO format datetime for publishing"),
                "media_url": string_prop("Optional media URL"),
                "hashtags": array_string_prop("Hashtags to include"),
            },
            required=["content", "platform", "scheduled_time"]
        ),
        create_tool_schema(
            name="get_scheduled_posts",
            description="Get all scheduled posts",
            properties={
                "platform": string_prop("Filter by platform"),
                "status": string_prop("Filter by status (default: scheduled)"),
            }
        ),
        create_tool_schema(
            name="respond_to_comment",
            description="Respond to a comment on a post",
            properties={
                "post_id": string_prop("The post ID"),
                "comment_id": string_prop("The comment ID to respond to"),
                "response": string_prop("The response text"),
                "platform": string_prop("Platform (default: facebook)"),
            },
            required=["post_id", "comment_id", "response"]
        ),
        create_tool_schema(
            name="get_comments",
            description="Get comments on posts",
            properties={
                "post_id": string_prop("Specific post ID (optional)"),
                "platform": string_prop("Platform (default: facebook)"),
                "unanswered_only": boolean_prop("Only show unanswered comments"),
            }
        ),
        create_tool_schema(
            name="generate_content_ideas",
            description="Generate content ideas based on topic and platform",
            properties={
                "topic": string_prop("Topic or theme for content"),
                "platform": string_prop("Target platform"),
                "tone": string_prop("Tone: professional, casual, humorous, inspirational"),
                "count": integer_prop("Number of ideas to generate (default: 5)"),
            },
            required=["topic"]
        ),
        create_tool_schema(
            name="generate_report",
            description="Generate social media performance report",
            properties={
                "platform": string_prop("Platform or 'all' (default: all)"),
                "days_back": integer_prop("Days to analyze (default: 30)"),
            }
        ),
        create_tool_schema(
            name="get_analytics",
            description="Get detailed analytics for a platform",
            properties={
                "platform": string_prop("Platform to analyze"),
                "metric_type": string_prop("Type: engagement, reach, followers"),
            },
            required=["platform"]
        ),
    ]
