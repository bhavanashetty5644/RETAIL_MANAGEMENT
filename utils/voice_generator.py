"""
Voice generator — uses gTTS when network is available,
falls back to a stub silent MP3 so the app never crashes.
"""
import io

def generate_voice(text: str, lang: str = "en") -> bytes:
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        # Return a minimal valid (silent) MP3 frame so the browser doesn't error
        return _silent_mp3()

def order_summary_text(order: dict) -> str:
    product = order.get("products") or {}
    if isinstance(product, list):
        product = product[0] if product else {}
    name  = product.get("name", "Unknown product")
    qty   = order.get("quantity", 0)
    total = order.get("total_price", 0)
    oid   = order.get("id", "")
    return (f"Order number {oid} placed successfully. "
            f"Product: {name}. Quantity: {qty} units. "
            f"Total amount: Rupees {total}. Thank you for your purchase!")

def _silent_mp3() -> bytes:
    """Minimal valid ID3v2 + single silent MPEG frame."""
    # ID3v2.3 header (10 bytes) with no tags, then one silent MP3 frame
    id3  = b"ID3\x03\x00\x00\x00\x00\x00\x00"
    # Silent MPEG1 Layer3 frame header: 0xFF 0xFB 0x90 0x00 + 413 zero bytes
    frame = b"\xff\xfb\x90\x00" + b"\x00" * 413
    return id3 + frame
