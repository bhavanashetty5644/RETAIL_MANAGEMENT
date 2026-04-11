from flask import Blueprint, request, send_file, jsonify
from middleware.auth_middleware import login_required
from controllers.order_controller import get_order
from utils.voice_generator import generate_voice, order_summary_text
import io

voice_bp = Blueprint("voice", __name__)

@voice_bp.route("/voice", methods=["POST"])
@login_required
def speak():
    data = request.get_json(silent=True) or {}
    text = data.get("text","").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400
    mp3 = generate_voice(text)
    return send_file(io.BytesIO(mp3), mimetype="audio/mpeg",
                     as_attachment=False, download_name="voice.mp3")

@voice_bp.route("/voice/order/<int:oid>")
@login_required
def speak_order(oid):
    order = get_order(oid)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    text = order_summary_text(order)
    mp3  = generate_voice(text)
    return send_file(io.BytesIO(mp3), mimetype="audio/mpeg",
                     as_attachment=False, download_name=f"order_{oid}.mp3")
