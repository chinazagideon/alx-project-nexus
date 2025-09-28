"""
Celery tasks for skill matching operations
"""

from celery import shared_task
from django.core.cache import cache
from .services import SkillMatchingService
import logging

logger = logging.getLogger(__name__)


@shared_task
def precompute_user_recommendations(user_id: int, limit: int = 20, min_match: float = 50.0):
    """
    Precompute job recommendations for a user in the background
    """
    try:
        logger.info(f"Precomputing recommendations for user {user_id}")

        # Get recommendations
        recommendations = SkillMatchingService.get_job_recommendations(user_id=user_id, limit=limit, min_match=min_match)

        # Cache the results
        cache_key = f"job_recommendations_{user_id}_{limit}_{min_match}"
        result = {"recommendations": recommendations, "total_count": len(recommendations), "min_match_threshold": min_match}

        cache.set(cache_key, result, 300)  # 5 minutes

        logger.info(f"Successfully precomputed {len(recommendations)} recommendations for user {user_id}")
        return f"Precomputed {len(recommendations)} recommendations for user {user_id}"

    except Exception as e:
        logger.error(f"Failed to precompute recommendations for user {user_id}: {str(e)}")
        raise


@shared_task
def precompute_skill_profile(user_id: int):
    """
    Precompute skill profile for a user in the background
    """
    try:
        logger.info(f"Precomputing skill profile for user {user_id}")

        # Get profile
        profile = SkillMatchingService.get_user_skill_profile(user_id)

        # Cache the results
        cache_key = f"skill_profile_{user_id}"
        cache.set(cache_key, profile, 600)  # 10 minutes

        logger.info(f"Successfully precomputed skill profile for user {user_id}")
        return f"Precomputed skill profile for user {user_id}"

    except Exception as e:
        logger.error(f"Failed to precompute skill profile for user {user_id}: {str(e)}")
        raise


@shared_task
def bulk_precompute_recommendations(user_ids: list, limit: int = 20, min_match: float = 50.0):
    """
    Precompute job recommendations for multiple users in bulk
    """
    try:
        logger.info(f"Bulk precomputing recommendations for {len(user_ids)} users")

        results = []
        for user_id in user_ids:
            try:
                result = precompute_user_recommendations.delay(user_id, limit, min_match)
                results.append(f"Queued recommendations for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to queue recommendations for user {user_id}: {str(e)}")
                results.append(f"Failed to queue recommendations for user {user_id}: {str(e)}")

        logger.info(f"Bulk precomputation completed for {len(user_ids)} users")
        return results

    except Exception as e:
        logger.error(f"Failed to bulk precompute recommendations: {str(e)}")
        raise


@shared_task
def clear_user_skill_cache(user_id: int):
    """
    Clear all skill-related cache for a user
    """
    try:
        logger.info(f"Clearing skill cache for user {user_id}")

        # Clear different cache keys
        cache_patterns = [f"job_recommendations_{user_id}_*", f"skill_profile_{user_id}", f"job_match_{user_id}_*"]

        # Note: In production, you might want to use Redis pattern deletion
        # For now, we'll clear specific keys
        cache.delete(f"skill_profile_{user_id}")

        # Clear job recommendations with common parameters
        for limit in [10, 20, 50]:
            for min_match in [30, 50, 70]:
                cache.delete(f"job_recommendations_{user_id}_{limit}_{min_match}")

        logger.info(f"Successfully cleared skill cache for user {user_id}")
        return f"Cleared skill cache for user {user_id}"

    except Exception as e:
        logger.error(f"Failed to clear skill cache for user {user_id}: {str(e)}")
        raise
