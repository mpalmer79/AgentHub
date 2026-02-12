from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import re

from app.core.database import get_supabase


class ReputationTools:
    """Tools for online reputation management"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def monitor_reviews(
        self,
        platforms: Optional[List[str]] = None,
        days_back: int = 30,
        min_rating: Optional[int] = None
    ) -> Dict[str, Any]:
        """Monitor reviews across platforms (simulated data for demo)"""
        if platforms is None:
            platforms = ["google", "yelp", "facebook"]
        
        supabase = get_supabase()
        
        # Get stored reviews from database
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        query = supabase.table("monitored_reviews") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("review_date", cutoff.isoformat())
        
        if min_rating:
            query = query.lte("rating", min_rating)
        
        result = query.order("review_date", desc=True).execute()
        
        reviews = result.data or []
        
        # Calculate statistics
        total_reviews = len(reviews)
        if total_reviews > 0:
            avg_rating = sum(r.get("rating", 0) for r in reviews) / total_reviews
            positive = len([r for r in reviews if r.get("rating", 0) >= 4])
            neutral = len([r for r in reviews if r.get("rating", 0) == 3])
            negative = len([r for r in reviews if r.get("rating", 0) <= 2])
        else:
            avg_rating = 0
            positive = neutral = negative = 0
        
        # Identify reviews needing response
        needs_response = [r for r in reviews if not r.get("responded") and r.get("rating", 5) <= 3]
        
        return {
            "summary": {
                "total_reviews": total_reviews,
                "average_rating": round(avg_rating, 2),
                "positive_count": positive,
                "neutral_count": neutral,
                "negative_count": negative,
                "needs_response_count": len(needs_response)
            },
            "recent_reviews": reviews[:20],
            "needs_response": needs_response[:10],
            "platforms_monitored": platforms,
            "date_range": {
                "start": cutoff.isoformat(),
                "end": datetime.utcnow().isoformat()
            }
        }
    
    async def draft_response(
        self,
        review_id: str,
        review_text: str,
        rating: int,
        reviewer_name: str,
        response_tone: str = "professional"
    ) -> Dict[str, Any]:
        """Draft a response to a review"""
        supabase = get_supabase()
        
        # Generate appropriate response based on rating and tone
        if rating >= 4:
            response_type = "positive"
            if response_tone == "professional":
                response = f"""Thank you so much for your wonderful review, {reviewer_name}! We're thrilled to hear about your positive experience with us. Your feedback means a lot to our team, and we look forward to serving you again soon!"""
            else:  # casual
                response = f"""Wow, thank you {reviewer_name}! 🎉 We're so happy you had a great experience! Can't wait to see you again!"""
        elif rating == 3:
            response_type = "neutral"
            response = f"""Thank you for taking the time to share your feedback, {reviewer_name}. We appreciate your honest review and are always looking for ways to improve. If there's anything specific we could do better, please don't hesitate to reach out to us directly. We'd love the opportunity to exceed your expectations next time."""
        else:
            response_type = "negative"
            response = f"""Dear {reviewer_name}, thank you for bringing this to our attention. We sincerely apologize that your experience didn't meet your expectations. Your feedback is valuable to us, and we'd like to make this right. Please contact us directly at your earliest convenience so we can address your concerns personally. We're committed to improving and hope to have the opportunity to serve you better in the future."""
        
        # Store draft response
        draft = supabase.table("review_response_drafts").insert({
            "user_id": self.user_id,
            "review_id": review_id,
            "reviewer_name": reviewer_name,
            "rating": rating,
            "response_type": response_type,
            "response_tone": response_tone,
            "draft_response": response,
            "status": "pending_approval",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "draft_id": draft.data[0]["id"] if draft.data else None,
            "review_id": review_id,
            "reviewer_name": reviewer_name,
            "rating": rating,
            "response_type": response_type,
            "draft_response": response,
            "tone": response_tone,
            "status": "pending_approval",
            "message": "Response drafted. Please review before posting."
        }
    
    async def request_reviews(
        self,
        customer_emails: List[str],
        customer_names: List[str],
        platform: str = "google",
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate review request emails for happy customers"""
        supabase = get_supabase()
        
        if len(customer_emails) != len(customer_names):
            return {"error": "Email and name lists must be the same length"}
        
        platform_links = {
            "google": "[Your Google Business Review Link]",
            "yelp": "[Your Yelp Business Page Link]",
            "facebook": "[Your Facebook Business Page Link]"
        }
        
        review_link = platform_links.get(platform, "[Your Review Link]")
        
        requests_generated = []
        
        for email, name in zip(customer_emails, customer_names):
            if custom_message:
                message = custom_message.replace("{name}", name).replace("{platform}", platform.title())
            else:
                message = f"""Dear {name},

Thank you for choosing us! We hope you had a great experience.

Your feedback helps us improve and helps others discover our services. If you have a moment, we'd be incredibly grateful if you could share your experience on {platform.title()}.

{review_link}

It only takes a minute, and it makes a huge difference for our small business.

Thank you for your support!

Warm regards,
The Team"""
            
            # Store request
            request = supabase.table("review_requests").insert({
                "user_id": self.user_id,
                "customer_email": email,
                "customer_name": name,
                "platform": platform,
                "message": message,
                "status": "pending_send",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            requests_generated.append({
                "request_id": request.data[0]["id"] if request.data else None,
                "customer_name": name,
                "customer_email": email,
                "platform": platform
            })
        
        return {
            "requests_generated": len(requests_generated),
            "requests": requests_generated,
            "platform": platform,
            "status": "ready_to_send",
            "message": f"Generated {len(requests_generated)} review request emails for {platform.title()}"
        }
    
    async def analyze_sentiment(
        self,
        time_period_days: int = 90
    ) -> Dict[str, Any]:
        """Analyze sentiment trends in reviews"""
        supabase = get_supabase()
        
        cutoff = datetime.utcnow() - timedelta(days=time_period_days)
        
        reviews = supabase.table("monitored_reviews") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("review_date", cutoff.isoformat()) \
            .order("review_date") \
            .execute()
        
        reviews_data = reviews.data or []
        
        if not reviews_data:
            return {
                "message": "No reviews found in the specified time period",
                "time_period_days": time_period_days
            }
        
        # Group by month
        monthly_data = {}
        keywords_positive = {}
        keywords_negative = {}
        
        positive_words = ["great", "excellent", "amazing", "wonderful", "fantastic", "love", "best", "recommend", "friendly", "professional"]
        negative_words = ["bad", "terrible", "awful", "horrible", "worst", "never", "rude", "slow", "dirty", "disappointed"]
        
        for review in reviews_data:
            date_str = review.get("review_date", "")[:7]  # YYYY-MM
            
            if date_str not in monthly_data:
                monthly_data[date_str] = {"count": 0, "total_rating": 0, "positive": 0, "negative": 0}
            
            monthly_data[date_str]["count"] += 1
            monthly_data[date_str]["total_rating"] += review.get("rating", 0)
            
            rating = review.get("rating", 3)
            if rating >= 4:
                monthly_data[date_str]["positive"] += 1
            elif rating <= 2:
                monthly_data[date_str]["negative"] += 1
            
            # Keyword analysis
            text = (review.get("review_text", "") or "").lower()
            for word in positive_words:
                if word in text:
                    keywords_positive[word] = keywords_positive.get(word, 0) + 1
            for word in negative_words:
                if word in text:
                    keywords_negative[word] = keywords_negative.get(word, 0) + 1
        
        # Calculate monthly averages
        monthly_trends = []
        for month, data in sorted(monthly_data.items()):
            monthly_trends.append({
                "month": month,
                "review_count": data["count"],
                "average_rating": round(data["total_rating"] / data["count"], 2) if data["count"] > 0 else 0,
                "positive_pct": round(data["positive"] / data["count"] * 100, 1) if data["count"] > 0 else 0,
                "negative_pct": round(data["negative"] / data["count"] * 100, 1) if data["count"] > 0 else 0
            })
        
        # Overall sentiment
        total = len(reviews_data)
        overall_positive = len([r for r in reviews_data if r.get("rating", 0) >= 4])
        overall_negative = len([r for r in reviews_data if r.get("rating", 0) <= 2])
        overall_avg = sum(r.get("rating", 0) for r in reviews_data) / total if total > 0 else 0
        
        # Trend direction
        if len(monthly_trends) >= 2:
            recent_avg = monthly_trends[-1]["average_rating"]
            older_avg = monthly_trends[0]["average_rating"]
            if recent_avg > older_avg + 0.2:
                trend = "improving"
            elif recent_avg < older_avg - 0.2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "overall_sentiment": {
                "total_reviews": total,
                "average_rating": round(overall_avg, 2),
                "positive_percentage": round(overall_positive / total * 100, 1) if total > 0 else 0,
                "negative_percentage": round(overall_negative / total * 100, 1) if total > 0 else 0,
                "trend": trend
            },
            "monthly_trends": monthly_trends,
            "top_positive_keywords": sorted(keywords_positive.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_negative_keywords": sorted(keywords_negative.items(), key=lambda x: x[1], reverse=True)[:5],
            "time_period_days": time_period_days,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def track_competitors(
        self,
        competitor_names: List[str]
    ) -> Dict[str, Any]:
        """Track competitor ratings (simulated comparison)"""
        supabase = get_supabase()
        
        # Get our own ratings
        our_reviews = supabase.table("monitored_reviews") \
            .select("rating") \
            .eq("user_id", self.user_id) \
            .execute()
        
        our_data = our_reviews.data or []
        our_avg = sum(r.get("rating", 0) for r in our_data) / len(our_data) if our_data else 0
        our_count = len(our_data)
        
        # Simulate competitor data (in production, this would pull from APIs)
        competitors = []
        for name in competitor_names:
            # Store competitor tracking
            supabase.table("competitor_tracking").upsert({
                "user_id": self.user_id,
                "competitor_name": name,
                "last_checked": datetime.utcnow().isoformat()
            }, on_conflict="user_id,competitor_name").execute()
            
            competitors.append({
                "name": name,
                "status": "tracking_enabled",
                "message": f"Now tracking {name}. Competitor data will be available in future updates."
            })
        
        return {
            "your_metrics": {
                "average_rating": round(our_avg, 2),
                "total_reviews": our_count
            },
            "competitors": competitors,
            "recommendation": "Continue monitoring. Focus on responding to negative reviews promptly and encouraging satisfied customers to leave reviews.",
            "tracked_at": datetime.utcnow().isoformat()
        }
    
    async def get_crisis_alerts(self) -> Dict[str, Any]:
        """Check for reputation crisis indicators"""
        supabase = get_supabase()
        
        alerts = []
        
        # Check for recent negative reviews
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_negative = supabase.table("monitored_reviews") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .lte("rating", 2) \
            .gte("review_date", week_ago.isoformat()) \
            .execute()
        
        negative_count = len(recent_negative.data or [])
        
        if negative_count >= 5:
            alerts.append({
                "type": "critical",
                "category": "negative_surge",
                "message": f"{negative_count} negative reviews in the past week",
                "action": "Immediate attention required. Review and respond to all negative feedback."
            })
        elif negative_count >= 3:
            alerts.append({
                "type": "warning",
                "category": "negative_trend",
                "message": f"{negative_count} negative reviews in the past week",
                "action": "Monitor closely and ensure prompt responses."
            })
        
        # Check for unanswered reviews
        unanswered = supabase.table("monitored_reviews") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .eq("responded", False) \
            .lte("rating", 3) \
            .execute()
        
        unanswered_count = len(unanswered.data or [])
        
        if unanswered_count >= 10:
            alerts.append({
                "type": "warning",
                "category": "unanswered_reviews",
                "message": f"{unanswered_count} reviews awaiting response",
                "action": "Prioritize responding to negative and neutral reviews."
            })
        
        # Check overall rating trend
        month_ago = datetime.utcnow() - timedelta(days=30)
        recent_reviews = supabase.table("monitored_reviews") \
            .select("rating") \
            .eq("user_id", self.user_id) \
            .gte("review_date", month_ago.isoformat()) \
            .execute()
        
        recent_data = recent_reviews.data or []
        if len(recent_data) >= 5:
            recent_avg = sum(r.get("rating", 0) for r in recent_data) / len(recent_data)
            if recent_avg < 3.5:
                alerts.append({
                    "type": "warning",
                    "category": "low_average",
                    "message": f"Average rating is {recent_avg:.1f} over the past month",
                    "action": "Focus on service improvements and request reviews from satisfied customers."
                })
        
        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "critical_count": len([a for a in alerts if a["type"] == "critical"]),
            "status": "crisis" if any(a["type"] == "critical" for a in alerts) else "monitoring",
            "checked_at": datetime.utcnow().isoformat()
        }
