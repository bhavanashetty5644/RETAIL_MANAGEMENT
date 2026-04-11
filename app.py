import traceback
from flask import Flask, session, redirect, url_for, request, render_template

def create_app():
    from config import Config
    from routes.auth_routes        import auth_bp
    from routes.dashboard_routes   import dashboard_bp
    from routes.product_routes     import product_bp
    from routes.order_routes       import order_bp
    from routes.report_routes      import report_bp
    from routes.voice_routes       import voice_bp
    from routes.user_routes        import user_bp
    from routes.analytics_routes   import reports_analytics_bp
    from routes.supplier_routes    import supplier_bp
    from routes.procurement_routes import procurement_bp
    from routes.sales_routes       import sales_bp

    app = Flask(__name__)
    app.config.from_object(Config)

    for bp in (auth_bp, dashboard_bp, product_bp, order_bp, report_bp,
               voice_bp, user_bp, reports_analytics_bp, supplier_bp,
               procurement_bp, sales_bp):
        app.register_blueprint(bp)

    # ── Session guard on every request ─────────────────────────────────────
    OPEN = {"auth.login_page", "auth.login", "auth.register_page",
            "auth.register", "auth.logout", "static"}

    @app.before_request
    def guard():
        if request.endpoint in OPEN or request.endpoint is None:
            return
        if not (session.get("user_id") and session.get("_st")):
            session.clear()
            from flask import flash
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("auth.login_page"))

    # ── Cache headers ────────────────────────────────────────────────────────
    @app.after_request
    def cache_ctl(response):
        if request.endpoint == "static":
            response.headers["Cache-Control"] = "public, max-age=86400"
        else:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"]  = "no-cache"
            response.headers["Expires"] = "0"
        return response

    # ── Error handlers ───────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        # Log full traceback to console for debugging
        traceback.print_exc()
        # Show user-friendly message; include error string for dev visibility
        return render_template("500.html", error=str(e)), 500

    @app.errorhandler(Exception)
    def unhandled(e):
        traceback.print_exc()
        return render_template("500.html", error=str(e)), 500

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n+------------------------------------------+")
    print("|  RetailOS v2 -> http://127.0.0.1:5000    |")
    print("|  Superadmin: admin@gmail.com             |")
    print("|  Password:   admin123                    |")
    print("+------------------------------------------+\n")
    app.run(debug=False, port=5000, threaded=True)
