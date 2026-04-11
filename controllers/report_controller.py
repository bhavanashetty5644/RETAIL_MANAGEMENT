from controllers.product_controller  import get_all_products
from controllers.auth_controller     import get_all_users
from controllers.order_controller    import get_sales_summary
from controllers.procurement_controller import get_procurement_stats

def get_dashboard_stats():
    try: products   = get_all_products()
    except Exception: products = []
    
    try: users      = get_all_users()
    except Exception: users   = []
    
    try: order_sum  = get_sales_summary()
    except Exception: order_sum = {"total_orders": 0, "total_revenue": 0}
    
    try: proc       = get_procurement_stats()
    except Exception: proc    = {"total_pos":0,"total_cost":0,"pending_count":0,
                                 "received_count":0,"cancelled_count":0,"pending_value":0}

    # Try sales stats — table may not exist yet or have old schema
    try:
        from controllers.sales_controller import get_sales_stats
        sales = get_sales_stats()
    except Exception:
        sales = {"total_sales":0,"total_revenue":0,"today_count":0,"today_revenue":0}

    try:
        low_stock = [p for p in products if p.get("quantity", 0) <= 5]
    except Exception:
        low_stock = []

    return {
        "total_products":    len(products),
        "total_users":       len(users),
        "total_orders":      order_sum.get("total_orders", 0),
        "total_revenue":     order_sum.get("total_revenue", 0),
        "low_stock_count":   len(low_stock),
        "low_stock_items":   low_stock,
        # Procurement
        "proc_pending":       proc.get("pending_count", 0),
        "proc_pending_value": proc.get("pending_value", 0),
        "proc_total":         proc.get("total_pos", 0),
        "proc_total_cost":    proc.get("total_cost", 0),
        # Sales
        "sales_today":        sales.get("today_count", 0),
        "sales_today_rev":    sales.get("today_revenue", 0),
        "sales_total":        sales.get("total_sales", 0),
        "sales_revenue":      sales.get("total_revenue", 0),
    }
