# core/signals.py
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PersonalInfo, Experience, Project, Skill, Education, Certification
from .pipeline import generate_portfolio_dataset

logger = logging.getLogger(__name__)

TRACKED_MODELS = [PersonalInfo, Experience, Project, Skill, Education, Certification]

def trigger_dataset_rebuild(sender, **kwargs):
    try:
        count, path = generate_portfolio_dataset()
        logger.info(f"[Ash Pipeline] Auto-regenerated {count} instruction pairs -> {path}")
    except Exception as e:
        logger.error(f"[Ash Pipeline] Failed to rebuild dataset: {e}")

# Register signals for all portfolio models
for model in TRACKED_MODELS:
    post_save.connect(trigger_dataset_rebuild, sender=model)
    post_delete.connect(trigger_dataset_rebuild, sender=model)