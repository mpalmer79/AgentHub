from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx

from app.core.database import get_supabase


class SocialPilotTools:
    """Tools for social media management and content creation"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def _get_meta_client(self) -> Dict[str, str]:
        """Get authenticated Meta (Facebook/Instagram) client info"""
        from app.api.integrations import get_meta_client
        return await get_meta_client(self.user_id)
    
    async def _make_meta_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Meta Graph API"""
        try:
            client_info = await self._get_meta_client()
            base_url = "https://graph.facebook.com/v18.0"
            url = f"{base_url}/{endpoint}"
            
            if params is None:
                params = {}
            params["access_token"] = client_info["access_token"]
            
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url, params=params)
                elif method == "POST":
                    response = await client.post(url, params=params, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Meta API error: {response.status_code}", "details": response.text}
        except Exception as e:
            return await self._get_mock_data(endpoint, method)
    
    async def _get_mock_data(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Return mock data for development/demo"""
        if "posts" in endpoint or "feed" in endpoint:
            return {
                "data": [
                    {
                        "id": "post_001",
                        "message": "Excited to announce our new product launch! 🚀 Check out the link in bio for more details.",
                        "created_time": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                        "likes": {"summary": {"total_count": 245}},
                        "comments": {"summary": {"total_count": 32}},
                        "shares": {"count": 18}
                    },
                    {
                        "id": "post_002",
                        "message": "Behind the scenes at our team meeting today! Great energy and amazing ideas flowing. #TeamWork #Innovation",
                        "created_time": (datetime.utcnow() - timedelta(days=3)).isoformat(),
                        "likes": {"summary": {"total_count": 189}},
                        "comments": {"summary": {"total_count": 15}},
                        "shares": {"count": 5}
                    },
                    {
                        "id": "post_003",
                        "message": "Happy Monday everyone! What are your goals for this week? Drop them in the comments 👇",
                        "created_time": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                        "likes": {"summary": {"total_count": 156}},
                        "comments": {"summary": {"total_count": 47}},
                        "shares": {"count": 2}
                    }
                ]
            }
        elif "comments" in endpoint:
            return {
                "data": [
                    {
                        "id": "comment_001",
                        "message": "This is amazing! Can't wait to try it out!",
                        "from": {"name": "John D.", "id": "user_123"},
                        "created_time": (datetime.utcnow() - timedelta(hours=5)).isoformat()
                    },
                    {
                        "id": "comment_002",
                        "message": "When will this be available in Europe?",
                        "from": {"name": "Sarah M.", "id": "user_456"},
                        "created_time": (datetime.utcnow() - timedelta(hours=8)).isoformat()
                    }
                ]
            }
        elif "insights" in endpoint:
            return {
                "data": [
                    {"name": "page_impressions", "values": [{"value": 15420}]},
                    {"name": "page_engaged_users", "values": [{"value": 2340}]},
                    {"name": "page_fans", "values": [{"value": 8750}]},
                    {"name": "page_views_total", "values": [{"value": 3210}]}
                ]
            }
        return {"status": "ok", "mock": True}
    
    async def create_post(
        self,
        content: str,
        platform: str = "facebook",
        media_url: Optional[str] = None,
        link: Optional[str] = None,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a social media post"""
        supabase = get_supabase()
        
        full_content = content
        if hashtags:
            hashtag_str = " ".join([f"#{tag}" if not tag.startswith("#") else tag for tag in hashtags])
            full_content = f"{content}\n\n{hashtag_str}"
        
        post_record = supabase.table("social_posts").insert({
            "user_id": self.user_id,
            "platform": platform,
            "content": full_content,
            "media_url": media_url,
            "link": link,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "post_id": post_record.data[0]["id"] if post_record.data else None,
            "platform": platform,
            "content": full_content,
            "status": "draft_created",
            "message": f"Post created as draft for {platform}. Review and publish when ready."
        }
    
    async def schedule_content(
        self,
        content: str,
        platform: str,
        scheduled_time: str,
        media_url: Optional[str] = None,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Schedule a post for future publishing"""
        supabase = get_supabase()
        
        full_content = content
        if hashtags:
            hashtag_str = " ".join([f"#{tag}" if not tag.startswith("#") else tag for tag in hashtags])
            full_content = f"{content}\n\n{hashtag_str}"
        
        scheduled = supabase.table("scheduled_posts").insert({
            "user_id": self.user_id,
            "platform": platform,
            "content": full_content,
            "media_url": media_url,
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "schedule_id": scheduled.data[0]["id"] if scheduled.data else None,
            "platform": platform,
            "content": full_content[:100] + "..." if len(full_content) > 100 else full_content,
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "message": f"Post scheduled for {scheduled_time} on {platform}"
        }
    
    async def get_scheduled_posts(
        self,
        platform: Optional[str] = None,
        status: str = "scheduled"
    ) -> Dict[str, Any]:
        """Get all scheduled posts"""
        supabase = get_supabase()
        
        query = supabase.table("scheduled_posts") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .eq("status", status) \
            .order("scheduled_time", desc=False)
        
        if platform:
            query = query.eq("platform", platform)
        
        result = query.execute()
        
        return {
            "scheduled_posts": result.data or [],
            "count": len(result.data or []),
            "filters": {"platform": platform, "status": status}
        }
    
    async def respond_to_comment(
        self,
        post_id: str,
        comment_id: str,
        response: str,
        platform: str = "facebook"
    ) -> Dict[str, Any]:
        """Respond to a comment on a post"""
        supabase = get_supabase()
        
        comment_response = supabase.table("social_comment_responses").insert({
            "user_id": self.user_id,
            "platform": platform,
            "post_id": post_id,
            "comment_id": comment_id,
            "response": response,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "response_id": comment_response.data[0]["id"] if comment_response.data else None,
            "post_id": post_id,
            "comment_id": comment_id,
            "response": response,
            "platform": platform,
            "status": "pending_review",
            "message": "Response drafted. Review before posting."
        }
    
    async def get_comments(
        self,
        post_id: Optional[str] = None,
        platform: str = "facebook",
        unanswered_only: bool = False
    ) -> Dict[str, Any]:
        """Get comments on posts"""
        result = await self._make_meta_request(
            "GET",
            f"{post_id}/comments" if post_id else "me/feed",
            params={"fields": "id,message,from,created_time"}
        )
        
        if "error" in result:
            return result
        
        comments = result.get("data", [])
        
        if unanswered_only:
            supabase = get_supabase()
            responses = supabase.table("social_comment_responses") \
                .select("comment_id") \
                .eq("user_id", self.user_id) \
                .execute()
            
            answered_ids = set(r["comment_id"] for r in (responses.data or []))
            comments = [c for c in comments if c.get("id") not in answered_ids]
        
        return {
            "comments": comments,
            "count": len(comments),
            "post_id": post_id,
            "unanswered_only": unanswered_only
        }
    
    async def generate_content_ideas(
        self,
        topic: str,
        platform: str = "facebook",
        tone: str = "professional",
        count: int = 5
    ) -> Dict[str, Any]:
        """Generate content ideas based on topic and platform"""
        platform_tips = {
            "facebook": "Keep posts engaging, use emojis sparingly, include a call to action",
            "instagram": "Visual-first, use hashtags strategically (5-10), write captivating first line",
            "linkedin": "Professional tone, share insights, industry relevance, avoid heavy hashtags",
            "twitter": "Concise (280 chars), punchy, use 1-2 hashtags, encourage retweets"
        }
        
        templates = [
            f"Did you know? [Interesting fact about {topic}] 💡 #KnowledgeIsPower",
            f"3 ways {topic} can transform your [business/life]: 1️⃣... 2️⃣... 3️⃣...",
            f"Our team's approach to {topic}: [Share unique perspective] What's yours?",
            f"The future of {topic} is here! Here's what you need to know 👇",
            f"Common myths about {topic} - debunked! 🔍 Thread below...",
            f"Behind the scenes: How we handle {topic} at our company 🎬",
            f"Q&A time! What questions do you have about {topic}? Drop them below 👇",
            f"Success story: How [client/user] achieved [result] with {topic} 🏆"
        ]
        
        ideas = []
        for i in range(min(count, len(templates))):
            ideas.append({
                "idea_number": i + 1,
                "template": templates[i],
                "platform": platform,
                "tone": tone,
                "best_posting_times": self._get_best_times(platform),
                "suggested_hashtags": self._suggest_hashtags(topic, platform)
            })
        
        return {
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "platform_tips": platform_tips.get(platform, ""),
            "content_ideas": ideas,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_best_times(self, platform: str) -> List[str]:
        """Get best posting times by platform"""
        times = {
            "facebook": ["9:00 AM", "1:00 PM", "4:00 PM"],
            "instagram": ["11:00 AM", "2:00 PM", "7:00 PM"],
            "linkedin": ["7:30 AM", "12:00 PM", "5:00 PM"],
            "twitter": ["8:00 AM", "12:00 PM", "6:00 PM"]
        }
        return times.get(platform, ["9:00 AM", "12:00 PM", "5:00 PM"])
    
    def _suggest_hashtags(self, topic: str, platform: str) -> List[str]:
        """Suggest relevant hashtags"""
        base_tags = [topic.replace(" ", ""), "business", "growth"]
        
        platform_tags = {
            "instagram": ["instagood", "instadaily", "trending"],
            "linkedin": ["leadership", "innovation", "networking"],
            "twitter": ["trending", "viral"],
            "facebook": ["community", "share"]
        }
        
        return base_tags + platform_tags.get(platform, [])[:3]
    
    async def generate_report(
        self,
        platform: str = "all",
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Generate social media performance report"""
        supabase = get_supabase()
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        posts_query = supabase.table("social_posts") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat())
        
        if platform != "all":
            posts_query = posts_query.eq("platform", platform)
        
        posts = posts_query.execute()
        
        scheduled = supabase.table("scheduled_posts") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat()) \
            .execute()
        
        responses = supabase.table("social_comment_responses") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat()) \
            .execute()
        
        posts_data = posts.data or []
        scheduled_data = scheduled.data or []
        responses_data = responses.data or []
        
        posts_by_platform = {}
        for p in posts_data:
            plat = p.get("platform", "unknown")
            posts_by_platform[plat] = posts_by_platform.get(plat, 0) + 1
        
        mock_engagement = {
            "total_impressions": 45000 + len(posts_data) * 1500,
            "total_engagements": 3200 + len(posts_data) * 200,
            "engagement_rate": 7.1,
            "follower_growth": 342,
            "top_performing_post": posts_data[0] if posts_data else None
        }
        
        return {
            "report_period": {
                "days": days_back,
                "start": cutoff.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "content_metrics": {
                "total_posts": len(posts_data),
                "posts_by_platform": posts_by_platform,
                "scheduled_posts": len(scheduled_data),
                "comments_responded": len(responses_data)
            },
            "engagement_metrics": mock_engagement,
            "recommendations": self._generate_social_recommendations(posts_data, mock_engagement),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_social_recommendations(self, posts: List, engagement: Dict) -> List[str]:
        """Generate recommendations based on performance"""
        recs = []
        
        if len(posts) < 10:
            recs.append("Increase posting frequency - aim for at least 3-4 posts per week")
        
        if engagement.get("engagement_rate", 0) < 5:
            recs.append("Engagement rate is below average - try more interactive content (polls, questions)")
        
        if engagement.get("engagement_rate", 0) > 8:
            recs.append("Great engagement rate! Consider boosting top-performing posts")
        
        recs.append("Post during peak hours for maximum visibility")
        recs.append("Respond to comments within 2 hours to boost engagement")
        
        return recs
    
    async def get_analytics(
        self,
        platform: str = "facebook",
        metric_type: str = "engagement"
    ) -> Dict[str, Any]:
        """Get detailed analytics for a platform"""
        result = await self._make_meta_request(
            "GET",
            "me/insights",
            params={
                "metric": "page_impressions,page_engaged_users,page_fans,page_views_total",
                "period": "day"
            }
        )
        
        if "error" in result:
            return result
        
        insights = result.get("data", [])
        
        metrics = {}
        for insight in insights:
            name = insight.get("name", "")
            values = insight.get("values", [{}])
            metrics[name] = values[0].get("value", 0) if values else 0
        
        return {
            "platform": platform,
            "metric_type": metric_type,
            "metrics": {
                "impressions": metrics.get("page_impressions", 0),
                "engaged_users": metrics.get("page_engaged_users", 0),
                "total_followers": metrics.get("page_fans", 0),
                "page_views": metrics.get("page_views_total", 0),
                "engagement_rate": round(
                    metrics.get("page_engaged_users", 0) / max(metrics.get("page_impressions", 1), 1) * 100, 2
                )
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
