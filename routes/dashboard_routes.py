from flask import Blueprint, render_template, session
from middleware.auth_middleware import login_required
from controllers.report_controller import get_dashboard_stats
from controllers.order_controller import get_all_orders

dashboard_bp = Blueprint("dashboard", __name__)

_EMPTY_STATS = {
    "total_products": 0, "total_users": 0, "total_orders": 0,
    "total_revenue": 0, "low_stock_count": 0, "low_stock_items": [],
    "proc_pending": 0, "proc_pending_value": 0,
    "proc_total": 0, "proc_total_cost": 0,
    "sales_today": 0, "sales_today_rev": 0,
    "sales_total": 0, "sales_revenue": 0,
}

@dashboard_bp.route("/dashboard")
@login_required
def index():
    try:
        stats = get_dashboard_stats()
        orders = get_all_orders()[:5]
    except Exception as e:
        from flask import flash
        flash(f"Database sync issue: {e}", "error")
        stats = _EMPTY_STATS
        orders = []

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_orders=orders,
        user={"name": session.get("user_name", "User"), "role": session.get("role", "staff")}
    )
