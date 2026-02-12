from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, number_prop, boolean_prop


def get_inventory_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for InventoryIQAI"""
    return [
        create_tool_schema(
            name="forecast_demand",
            description="Forecast demand for products based on historical patterns and seasonality",
            properties={
                "product_id": string_prop("Specific product ID to forecast (optional)"),
                "category": string_prop("Filter by product category"),
                "forecast_days": integer_prop("Number of days to forecast (default: 30)"),
                "include_seasonality": boolean_prop("Include seasonal adjustments (default: true)"),
            }
        ),
        create_tool_schema(
            name="generate_purchase_order",
            description="Generate purchase orders for inventory replenishment",
            properties={
                "product_id": string_prop("Specific product ID to order (optional, auto-detects if not specified)"),
                "supplier_id": string_prop("Preferred supplier ID"),
                "auto_calculate": boolean_prop("Automatically calculate quantities based on forecast (default: true)"),
            }
        ),
        create_tool_schema(
            name="optimize_inventory",
            description="Optimize inventory levels to reduce costs and prevent stockouts",
            properties={
                "optimization_type": string_prop("Type: all, overstock, understock, reorder_points, dead_stock"),
                "target_service_level": number_prop("Target service level 0-1 (default: 0.95)"),
            }
        ),
        create_tool_schema(
            name="track_supplier",
            description="Track supplier performance, reliability, and order history",
            properties={
                "supplier_id": string_prop("Specific supplier ID to track (optional)"),
                "include_performance": boolean_prop("Include performance metrics (default: true)"),
            }
        ),
        create_tool_schema(
            name="identify_slow_movers",
            description="Identify slow-moving and dead stock items that need attention",
            properties={
                "days_threshold": integer_prop("Days of stock threshold to consider slow-moving (default: 90)"),
                "include_recommendations": boolean_prop("Include action recommendations (default: true)"),
            }
        ),
    ]
