from .models import ProductChangeHistory
import logging

logger = logging.getLogger(__name__)

def log_product_change(product, user, change_type, old_value=None, new_value=None):
    """Helper to log and persist product changes in history."""
    ProductChangeHistory.objects.create(
        product=product,
        user=user,
        change_type=change_type,
        old_value=old_value,
        new_value=new_value,
    )
    logger.info(f'[{change_type.upper()}] Product "{product.name}" by {user.username} '
                f'(old: {old_value}, new: {new_value})')
