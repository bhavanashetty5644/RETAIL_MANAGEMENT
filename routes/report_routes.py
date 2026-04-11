from flask import Blueprint, send_file, flash, redirect, url_for
from middleware.auth_middleware import login_required
from controllers.order_controller import get_order
from utils.pdf_generator import generate_invoice_pdf
import io

report_bp = Blueprint("reports", __name__)

@report_bp.route("/generate-pdf/<int:oid>")
@login_required
def generate_pdf(oid):
    order = get_order(oid)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders.index"))
    try:
        pdf_bytes = generate_invoice_pdf(order)
        return send_file(io.BytesIO(pdf_bytes), mimetype="application/pdf",
                         as_attachment=True, download_name=f"invoice_{oid}.pdf")
    except Exception as e:
        flash(f"PDF generation failed: {e}", "error")
        return redirect(url_for("orders.invoice", oid=oid))
