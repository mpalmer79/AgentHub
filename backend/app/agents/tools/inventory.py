from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random

from app.core.database import get_supabase


class InventoryTools:
    """Tools for inventory management and optimization"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def forecast_demand(
        self,
        product_id: Optional[str] = None,
        category: Optional[str] = None,
        forecast_days: int = 30,
        include_seasonality: bool = True
    ) -> Dict[str, Any]:
        """Forecast demand for products based on historical patterns"""
        supabase = get_supabase()
        
        # Get products
        query = supabase.table("inventory_products") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .eq("status", "active")
        
        if product_id:
            query = query.eq("id", product_id)
        if category:
            query = query.eq("category", category)
        
        result = query.execute()
        products = result.data or []
        
        # Add mock products if none exist
        if not products:
            products = [
                {
                    "id": "prod_001",
                    "sku": "WDG-001",
                    "name": "Premium Widget",
                    "category": "widgets",
                    "current_stock": 150,
                    "reorder_point": 50,
                    "reorder_quantity": 100,
                    "unit_cost": 12.50,
                    "lead_time_days": 7,
                    "avg_daily_sales": 8
                },
                {
                    "id": "prod_002",
                    "sku": "GDG-001",
                    "name": "Standard Gadget",
                    "category": "gadgets",
                    "current_stock": 75,
                    "reorder_point": 30,
                    "reorder_quantity": 50,
                    "unit_cost": 25.00,
                    "lead_time_days": 10,
                    "avg_daily_sales": 5
                },
                {
                    "id": "prod_003",
                    "sku": "ACC-001",
                    "name": "Basic Accessory",
                    "category": "accessories",
                    "current_stock": 200,
                    "reorder_point": 75,
                    "reorder_quantity": 150,
                    "unit_cost": 5.00,
                    "lead_time_days": 5,
                    "avg_daily_sales": 12
                },
                {
                    "id": "prod_004",
                    "sku": "WDG-002",
                    "name": "Economy Widget",
                    "category": "widgets",
                    "current_stock": 25,
                    "reorder_point": 40,
                    "reorder_quantity": 80,
                    "unit_cost": 8.00,
                    "lead_time_days": 7,
                    "avg_daily_sales": 6
                },
                {
                    "id": "prod_005",
                    "sku": "GDG-002",
                    "name": "Premium Gadget",
                    "category": "gadgets",
                    "current_stock": 45,
                    "reorder_point": 20,
                    "reorder_quantity": 40,
                    "unit_cost": 45.00,
                    "lead_time_days": 14,
                    "avg_daily_sales": 3
                }
            ]
        
        # Generate forecasts
        forecasts = []
        total_forecasted_demand = 0
        stockout_risks = []
        
        for product in products:
            avg_daily = product.get("avg_daily_sales", 5)
            current_stock = product.get("current_stock", 0)
            lead_time = product.get("lead_time_days", 7)
            reorder_point = product.get("reorder_point", 0)
            
            # Apply seasonality factor
            seasonality_factor = 1.0
            if include_seasonality:
                month = datetime.utcnow().month
                if month in [11, 12]:  # Holiday season
                    seasonality_factor = 1.35
                elif month in [1, 2]:  # Post-holiday
                    seasonality_factor = 0.85
                elif month in [6, 7, 8]:  # Summer
                    seasonality_factor = 1.1
            
            # Calculate forecast
            daily_forecast = round(avg_daily * seasonality_factor, 1)
            period_forecast = round(daily_forecast * forecast_days)
            total_forecasted_demand += period_forecast
            
            # Calculate days until stockout
            days_of_stock = round(current_stock / daily_forecast) if daily_forecast > 0 else 999
            
            # Determine stockout risk
            if days_of_stock <= lead_time:
                risk_level = "critical"
                stockout_risks.append(product)
            elif days_of_stock <= lead_time + 7:
                risk_level = "high"
                stockout_risks.append(product)
            elif days_of_stock <= lead_time + 14:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Generate daily forecast breakdown
            daily_breakdown = []
            for day in range(min(forecast_days, 14)):
                date = datetime.utcnow() + timedelta(days=day)
                # Add some variance
                variance = random.uniform(0.85, 1.15)
                daily_breakdown.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "forecasted_units": round(daily_forecast * variance)
                })
            
            forecasts.append({
                "product_id": product.get("id"),
                "sku": product.get("sku"),
                "name": product.get("name"),
                "category": product.get("category"),
                "current_stock": current_stock,
                "avg_daily_sales": avg_daily,
                "forecasted_daily_demand": daily_forecast,
                "forecasted_period_demand": period_forecast,
                "seasonality_factor": seasonality_factor,
                "days_of_stock_remaining": days_of_stock,
                "stockout_risk": risk_level,
                "recommended_action": self._get_forecast_recommendation(risk_level, product),
                "daily_breakdown": daily_breakdown
            })
        
        # Log forecast
        supabase.table("demand_forecasts").insert({
            "user_id": self.user_id,
            "forecast_days": forecast_days,
            "products_forecasted": len(forecasts),
            "total_demand": total_forecasted_demand,
            "stockout_risks": len(stockout_risks),
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "forecast_period_days": forecast_days,
            "include_seasonality": include_seasonality,
            "forecasts": forecasts,
            "summary": {
                "products_analyzed": len(forecasts),
                "total_forecasted_demand": total_forecasted_demand,
                "critical_stockout_risk": sum(1 for f in forecasts if f["stockout_risk"] == "critical"),
                "high_stockout_risk": sum(1 for f in forecasts if f["stockout_risk"] == "high"),
                "products_needing_reorder": sum(1 for f in forecasts if f["stockout_risk"] in ["critical", "high"])
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_forecast_recommendation(self, risk_level: str, product: Dict) -> str:
        """Get recommendation based on stockout risk"""
        name = product.get("name", "Product")
        reorder_qty = product.get("reorder_quantity", 0)
        
        recommendations = {
            "critical": f"URGENT: Place order for {reorder_qty} units of {name} immediately",
            "high": f"Order {reorder_qty} units of {name} within 2-3 days",
            "medium": f"Plan to reorder {name} within the next week",
            "low": f"Stock levels adequate for {name}"
        }
        return recommendations.get(risk_level, "Monitor stock levels")
    
    async def generate_purchase_order(
        self,
        product_id: Optional[str] = None,
        supplier_id: Optional[str] = None,
        auto_calculate: bool = True,
        custom_quantities: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Generate purchase orders for inventory replenishment"""
        supabase = get_supabase()
        
        # Get products needing reorder
        if auto_calculate:
            forecast_result = await self.forecast_demand(product_id=product_id)
            products_to_order = [
                f for f in forecast_result.get("forecasts", [])
                if f["stockout_risk"] in ["critical", "high"]
            ]
        else:
            products_to_order = []
        
        # Add mock products if none found
        if not products_to_order:
            products_to_order = [
                {
                    "product_id": "prod_004",
                    "sku": "WDG-002",
                    "name": "Economy Widget",
                    "current_stock": 25,
                    "stockout_risk": "critical"
                }
            ]
        
        # Get supplier info
        suppliers = {
            "sup_001": {"name": "Primary Supplier Co", "lead_time": 7, "discount_percent": 5},
            "sup_002": {"name": "Backup Supplies Inc", "lead_time": 10, "discount_percent": 0},
            "sup_003": {"name": "Express Parts Ltd", "lead_time": 3, "discount_percent": 0, "rush_fee": 15}
        }
        
        selected_supplier = suppliers.get(supplier_id, suppliers["sup_001"])
        
        # Build purchase order
        po_number = f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        line_items = []
        subtotal = 0
        
        for product in products_to_order:
            # Determine quantity
            if custom_quantities and product.get("product_id") in custom_quantities:
                quantity = custom_quantities[product["product_id"]]
            else:
                # Use default reorder quantity or calculate based on forecast
                quantity = 100  # Default, would come from product data
            
            unit_cost = 10.00  # Would come from product/supplier data
            line_total = quantity * unit_cost
            subtotal += line_total
            
            line_items.append({
                "product_id": product.get("product_id"),
                "sku": product.get("sku"),
                "name": product.get("name"),
                "quantity": quantity,
                "unit_cost": unit_cost,
                "line_total": line_total,
                "current_stock": product.get("current_stock"),
                "urgency": product.get("stockout_risk")
            })
        
        # Calculate totals
        discount = subtotal * (selected_supplier.get("discount_percent", 0) / 100)
        rush_fee = selected_supplier.get("rush_fee", 0) if supplier_id == "sup_003" else 0
        total = subtotal - discount + rush_fee
        
        # Calculate expected delivery
        expected_delivery = datetime.utcnow() + timedelta(days=selected_supplier.get("lead_time", 7))
        
        # Save PO
        supabase.table("purchase_orders").insert({
            "id": po_number,
            "user_id": self.user_id,
            "supplier_name": selected_supplier["name"],
            "line_items_count": len(line_items),
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "status": "draft",
            "expected_delivery": expected_delivery.strftime("%Y-%m-%d"),
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "purchase_order": {
                "po_number": po_number,
                "status": "draft",
                "supplier": selected_supplier["name"],
                "created_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "expected_delivery": expected_delivery.strftime("%Y-%m-%d"),
                "lead_time_days": selected_supplier.get("lead_time")
            },
            "line_items": line_items,
            "financial_summary": {
                "subtotal": subtotal,
                "discount": discount,
                "discount_percent": selected_supplier.get("discount_percent", 0),
                "rush_fee": rush_fee,
                "total": round(total, 2)
            },
            "next_steps": [
                "Review line items and quantities",
                "Approve purchase order to send to supplier",
                "Track delivery status upon confirmation"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def optimize_inventory(
        self,
        optimization_type: str = "all",
        target_service_level: float = 0.95
    ) -> Dict[str, Any]:
        """Optimize inventory levels across products"""
        supabase = get_supabase()
        
        # Get current inventory
        forecast_result = await self.forecast_demand()
        products = forecast_result.get("forecasts", [])
        
        optimizations = []
        total_current_value = 0
        total_optimized_value = 0
        potential_savings = 0
        
        for product in products:
            current_stock = product.get("current_stock", 0)
            avg_daily = product.get("forecasted_daily_demand", 5)
            days_of_stock = product.get("days_of_stock_remaining", 0)
            
            # Assume unit cost (would come from product data)
            unit_cost = 15.00
            current_value = current_stock * unit_cost
            total_current_value += current_value
            
            optimization = {
                "product_id": product.get("product_id"),
                "sku": product.get("sku"),
                "name": product.get("name"),
                "current_stock": current_stock,
                "current_value": current_value,
                "avg_daily_demand": avg_daily,
                "days_of_stock": days_of_stock,
                "recommendations": []
            }
            
            # Calculate optimal stock level (safety stock + lead time demand)
            lead_time = 7  # Would come from product/supplier data
            safety_stock = round(avg_daily * 7)  # 7 days safety stock
            optimal_stock = round(safety_stock + (avg_daily * lead_time))
            optimal_value = optimal_stock * unit_cost
            total_optimized_value += optimal_value
            
            optimization["optimal_stock"] = optimal_stock
            optimization["optimal_value"] = optimal_value
            
            # Overstock analysis
            if optimization_type in ["all", "overstock"]:
                if current_stock > optimal_stock * 1.5:
                    excess = current_stock - optimal_stock
                    excess_value = excess * unit_cost
                    potential_savings += excess_value
                    optimization["recommendations"].append({
                        "type": "overstock",
                        "severity": "high" if current_stock > optimal_stock * 2 else "medium",
                        "message": f"Overstock detected: {excess} excess units (${excess_value:.2f})",
                        "action": "Consider promotional pricing or redistributing to other locations"
                    })
            
            # Understock analysis
            if optimization_type in ["all", "understock"]:
                if current_stock < safety_stock:
                    shortage = safety_stock - current_stock
                    optimization["recommendations"].append({
                        "type": "understock",
                        "severity": "critical" if current_stock < safety_stock * 0.5 else "high",
                        "message": f"Below safety stock: need {shortage} more units",
                        "action": "Place urgent reorder to avoid stockout"
                    })
            
            # Reorder point analysis
            if optimization_type in ["all", "reorder_points"]:
                current_reorder_point = product.get("reorder_point", 50)
                optimal_reorder_point = round(safety_stock + (avg_daily * lead_time * 0.5))
                
                if abs(current_reorder_point - optimal_reorder_point) > optimal_reorder_point * 0.2:
                    optimization["recommendations"].append({
                        "type": "reorder_point",
                        "severity": "medium",
                        "message": f"Reorder point adjustment suggested: {current_reorder_point} → {optimal_reorder_point}",
                        "action": "Update reorder point to optimize stock levels"
                    })
                    optimization["suggested_reorder_point"] = optimal_reorder_point
            
            # Dead stock analysis
            if optimization_type in ["all", "dead_stock"]:
                if days_of_stock > 180:
                    optimization["recommendations"].append({
                        "type": "dead_stock",
                        "severity": "high",
                        "message": f"Slow-moving inventory: {days_of_stock} days of stock",
                        "action": "Consider clearance sale, bundling, or discontinuation"
                    })
            
            optimizations.append(optimization)
        
        # Calculate metrics
        inventory_turns = round(365 / (total_current_value / (sum(p.get("forecasted_daily_demand", 0) * 15 for p in products) * 365)) if total_current_value > 0 else 0, 2)
        
        # Log optimization
        supabase.table("inventory_optimizations").insert({
            "user_id": self.user_id,
            "optimization_type": optimization_type,
            "products_analyzed": len(optimizations),
            "potential_savings": potential_savings,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "optimization_type": optimization_type,
            "target_service_level": target_service_level,
            "products": optimizations,
            "summary": {
                "products_analyzed": len(optimizations),
                "total_current_inventory_value": round(total_current_value, 2),
                "total_optimal_inventory_value": round(total_optimized_value, 2),
                "potential_savings": round(potential_savings, 2),
                "products_overstocked": sum(1 for o in optimizations if any(r["type"] == "overstock" for r in o["recommendations"])),
                "products_understocked": sum(1 for o in optimizations if any(r["type"] == "understock" for r in o["recommendations"])),
                "estimated_inventory_turns": inventory_turns
            },
            "top_actions": self._get_top_optimization_actions(optimizations),
            "optimized_at": datetime.utcnow().isoformat()
        }
    
    def _get_top_optimization_actions(self, optimizations: List[Dict]) -> List[str]:
        """Extract top priority actions from optimizations"""
        actions = []
        
        # Critical understocks first
        for opt in optimizations:
            for rec in opt.get("recommendations", []):
                if rec["type"] == "understock" and rec["severity"] == "critical":
                    actions.append(f"URGENT: Reorder {opt['name']} - {rec['message']}")
        
        # High severity overstocks
        for opt in optimizations:
            for rec in opt.get("recommendations", []):
                if rec["type"] == "overstock" and rec["severity"] == "high":
                    actions.append(f"Reduce {opt['name']} overstock - {rec['message']}")
        
        # Dead stock
        for opt in optimizations:
            for rec in opt.get("recommendations", []):
                if rec["type"] == "dead_stock":
                    actions.append(f"Address slow-moving {opt['name']} - {rec['message']}")
        
        return actions[:5]  # Return top 5 actions
    
    async def track_supplier(
        self,
        supplier_id: Optional[str] = None,
        include_performance: bool = True
    ) -> Dict[str, Any]:
        """Track supplier performance and reliability"""
        supabase = get_supabase()
        
        # Mock supplier data
        suppliers = [
            {
                "id": "sup_001",
                "name": "Primary Supplier Co",
                "contact_email": "orders@primarysupplier.com",
                "lead_time_days": 7,
                "status": "active",
                "categories": ["widgets", "gadgets"],
                "payment_terms": "Net 30",
                "minimum_order": 500.00,
                "performance": {
                    "on_time_delivery_rate": 94.5,
                    "quality_rating": 4.7,
                    "average_lead_time": 6.8,
                    "orders_last_90_days": 12,
                    "total_spent_last_90_days": 15420.00,
                    "defect_rate": 1.2,
                    "response_time_hours": 4
                }
            },
            {
                "id": "sup_002",
                "name": "Backup Supplies Inc",
                "contact_email": "sales@backupsupplies.com",
                "lead_time_days": 10,
                "status": "active",
                "categories": ["accessories", "widgets"],
                "payment_terms": "Net 45",
                "minimum_order": 250.00,
                "performance": {
                    "on_time_delivery_rate": 88.0,
                    "quality_rating": 4.2,
                    "average_lead_time": 11.2,
                    "orders_last_90_days": 5,
                    "total_spent_last_90_days": 4280.00,
                    "defect_rate": 2.8,
                    "response_time_hours": 12
                }
            },
            {
                "id": "sup_003",
                "name": "Express Parts Ltd",
                "contact_email": "urgent@expressparts.com",
                "lead_time_days": 3,
                "status": "active",
                "categories": ["widgets", "gadgets", "accessories"],
                "payment_terms": "Net 15",
                "minimum_order": 100.00,
                "performance": {
                    "on_time_delivery_rate": 98.5,
                    "quality_rating": 4.5,
                    "average_lead_time": 2.9,
                    "orders_last_90_days": 8,
                    "total_spent_last_90_days": 8920.00,
                    "defect_rate": 1.5,
                    "response_time_hours": 2
                }
            }
        ]
        
        if supplier_id:
            suppliers = [s for s in suppliers if s["id"] == supplier_id]
        
        # Calculate supplier scores
        for supplier in suppliers:
            if include_performance and "performance" in supplier:
                perf = supplier["performance"]
                # Weighted score calculation
                score = (
                    perf["on_time_delivery_rate"] * 0.3 +
                    perf["quality_rating"] * 20 * 0.25 +
                    (100 - perf["defect_rate"] * 10) * 0.2 +
                    min(100, (24 / perf["response_time_hours"]) * 25) * 0.15 +
                    min(100, perf["orders_last_90_days"] * 5) * 0.1
                )
                supplier["overall_score"] = round(score, 1)
                supplier["tier"] = "preferred" if score >= 85 else "approved" if score >= 70 else "conditional"
        
        # Generate recommendations
        recommendations = []
        for supplier in suppliers:
            if supplier.get("overall_score", 0) < 70:
                recommendations.append(f"Review relationship with {supplier['name']} - below performance threshold")
            if supplier.get("performance", {}).get("defect_rate", 0) > 2:
                recommendations.append(f"Address quality issues with {supplier['name']} - {supplier['performance']['defect_rate']}% defect rate")
            if supplier.get("performance", {}).get("on_time_delivery_rate", 100) < 90:
                recommendations.append(f"Discuss delivery reliability with {supplier['name']}")
        
        return {
            "suppliers": suppliers,
            "summary": {
                "total_suppliers": len(suppliers),
                "preferred_suppliers": sum(1 for s in suppliers if s.get("tier") == "preferred"),
                "total_spend_90_days": sum(s.get("performance", {}).get("total_spent_last_90_days", 0) for s in suppliers),
                "average_on_time_rate": round(sum(s.get("performance", {}).get("on_time_delivery_rate", 0) for s in suppliers) / len(suppliers), 1) if suppliers else 0
            },
            "recommendations": recommendations,
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    async def identify_slow_movers(
        self,
        days_threshold: int = 90,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Identify slow-moving and dead stock items"""
        supabase = get_supabase()
        
        # Get forecast data
        forecast_result = await self.forecast_demand()
        products = forecast_result.get("forecasts", [])
        
        slow_movers = []
        total_slow_mover_value = 0
        
        for product in products:
            days_of_stock = product.get("days_of_stock_remaining", 0)
            current_stock = product.get("current_stock", 0)
            
            if days_of_stock >= days_threshold:
                unit_cost = 15.00  # Would come from product data
                inventory_value = current_stock * unit_cost
                total_slow_mover_value += inventory_value
                
                # Categorize slow mover
                if days_of_stock >= 365:
                    category = "dead_stock"
                    urgency = "critical"
                elif days_of_stock >= 180:
                    category = "very_slow"
                    urgency = "high"
                else:
                    category = "slow"
                    urgency = "medium"
                
                slow_mover = {
                    "product_id": product.get("product_id"),
                    "sku": product.get("sku"),
                    "name": product.get("name"),
                    "category": product.get("category"),
                    "current_stock": current_stock,
                    "inventory_value": inventory_value,
                    "days_of_stock": days_of_stock,
                    "avg_daily_sales": product.get("avg_daily_demand", 0),
                    "slow_mover_category": category,
                    "urgency": urgency
                }
                
                if include_recommendations:
                    slow_mover["recommendations"] = self._get_slow_mover_recommendations(category, product)
                
                slow_movers.append(slow_mover)
        
        # Sort by urgency and value
        urgency_order = {"critical": 0, "high": 1, "medium": 2}
        slow_movers.sort(key=lambda x: (urgency_order.get(x["urgency"], 3), -x["inventory_value"]))
        
        return {
            "days_threshold": days_threshold,
            "slow_movers": slow_movers,
            "summary": {
                "total_slow_movers": len(slow_movers),
                "dead_stock_count": sum(1 for s in slow_movers if s["slow_mover_category"] == "dead_stock"),
                "very_slow_count": sum(1 for s in slow_movers if s["slow_mover_category"] == "very_slow"),
                "slow_count": sum(1 for s in slow_movers if s["slow_mover_category"] == "slow"),
                "total_value_at_risk": round(total_slow_mover_value, 2)
            },
            "action_plan": self._generate_slow_mover_action_plan(slow_movers),
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    def _get_slow_mover_recommendations(self, category: str, product: Dict) -> List[str]:
        """Get recommendations for slow-moving items"""
        name = product.get("name", "Product")
        
        base_recommendations = {
            "dead_stock": [
                f"Consider liquidation or write-off for {name}",
                "Explore donation for tax benefits",
                "Contact suppliers about return/exchange programs",
                "Bundle with fast-moving items"
            ],
            "very_slow": [
                f"Implement promotional pricing for {name}",
                "Feature in marketing campaigns",
                "Consider marketplace listing (Amazon, eBay)",
                "Offer to sales team as upsell item"
            ],
            "slow": [
                f"Monitor {name} for another 30 days",
                "Review pricing competitiveness",
                "Consider seasonal factors",
                "Reduce reorder quantities"
            ]
        }
        
        return base_recommendations.get(category, ["Review product performance"])
    
    def _generate_slow_mover_action_plan(self, slow_movers: List[Dict]) -> List[Dict]:
        """Generate prioritized action plan for slow movers"""
        action_plan = []
        
        # Immediate actions (critical)
        critical_items = [s for s in slow_movers if s["urgency"] == "critical"]
        if critical_items:
            action_plan.append({
                "timeframe": "Immediate (This Week)",
                "items_count": len(critical_items),
                "total_value": sum(s["inventory_value"] for s in critical_items),
                "actions": [
                    "Review dead stock items for liquidation",
                    "Contact liquidation partners for quotes",
                    "Assess write-off implications with accounting"
                ]
            })
        
        # Short-term actions (high)
        high_items = [s for s in slow_movers if s["urgency"] == "high"]
        if high_items:
            action_plan.append({
                "timeframe": "Short-term (2-4 Weeks)",
                "items_count": len(high_items),
                "total_value": sum(s["inventory_value"] for s in high_items),
                "actions": [
                    "Launch promotional campaign for slow movers",
                    "Create bundle offers with popular items",
                    "List on secondary marketplaces"
                ]
            })
        
        # Medium-term actions
        medium_items = [s for s in slow_movers if s["urgency"] == "medium"]
        if medium_items:
            action_plan.append({
                "timeframe": "Medium-term (1-2 Months)",
                "items_count": len(medium_items),
                "total_value": sum(s["inventory_value"] for s in medium_items),
                "actions": [
                    "Adjust reorder points to prevent overstock",
                    "Review product mix and consider discontinuation",
                    "Implement demand forecasting improvements"
                ]
            })
        
        return action_plan
