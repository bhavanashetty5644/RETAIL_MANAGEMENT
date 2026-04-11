import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

def generate_invoice_pdf(order):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    C = colors.HexColor

    product = order.get("products") or {}
    if isinstance(product, list):
        product = product[0] if product else {}

    order_id    = order.get("id", "N/A")
    pname       = product.get("name", "N/A")
    pcat        = product.get("category", "General")
    qty         = order.get("quantity", 0)
    unit_price  = float(product.get("price", 0))
    total       = float(order.get("total_price", 0))
    tax         = round(total * 0.18, 2)
    grand       = round(total + tax, 2)
    raw_date    = order.get("created_at", "")
    try:
        dt = datetime.fromisoformat(str(raw_date).replace("Z","+00:00"))
        date_str = dt.strftime("%d %B %Y, %I:%M %p")
    except Exception:
        date_str = str(raw_date)[:10] if raw_date else datetime.now().strftime("%d %B %Y")

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    title_s    = S("T", fontSize=30, textColor=C("#7C3AED"), alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=2)
    sub_s      = S("Sub", fontSize=10, textColor=C("#9CA3AF"), alignment=TA_CENTER, spaceAfter=2)
    inv_s      = S("Inv", fontSize=22, textColor=C("#1F2937"), fontName="Helvetica-Bold")
    normal_s   = styles["Normal"]
    footer_s   = S("F", fontSize=8, textColor=C("#9CA3AF"), alignment=TA_CENTER)

    els = []
    els.append(Paragraph("RetailOS", title_s))
    els.append(Paragraph("Smart Retail Management System", sub_s))
    els.append(Spacer(1, 3*mm))
    els.append(HRFlowable(width="100%", thickness=2, color=C("#7C3AED")))
    els.append(Spacer(1, 5*mm))
    els.append(Paragraph(f"INVOICE  <font color='#7C3AED'>#{order_id}</font>", inv_s))
    els.append(Spacer(1, 4*mm))

    meta = Table([
        [Paragraph("<b>Invoice Date</b>", normal_s), Paragraph(date_str, normal_s)],
        [Paragraph("<b>Category</b>", normal_s),     Paragraph(pcat, normal_s)],
        [Paragraph("<b>Status</b>", normal_s),        Paragraph("Completed", normal_s)],
    ], colWidths=[50*mm, 115*mm])
    meta.setStyle(TableStyle([
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("TEXTCOLOR",(0,0),(0,-1),C("#6B7280")),
    ]))
    els.append(meta)
    els.append(Spacer(1,5*mm))
    els.append(HRFlowable(width="100%", thickness=0.5, color=C("#E5E7EB")))
    els.append(Spacer(1,4*mm))

    tbl = Table(
        [["#","Product","Qty","Unit Price","Amount"],
         ["1", pname, str(qty), f"Rs.{unit_price:,.2f}", f"Rs.{total:,.2f}"]],
        colWidths=[10*mm, 75*mm, 20*mm, 35*mm, 35*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),C("#7C3AED")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,0),10),
        ("ALIGN",(0,0),(-1,0),"CENTER"),
        ("TOPPADDING",(0,0),(-1,0),8),("BOTTOMPADDING",(0,0),(-1,0),8),
        ("FONTSIZE",(0,1),(-1,-1),10),
        ("ALIGN",(2,1),(-1,-1),"CENTER"),
        ("ALIGN",(3,1),(-1,-1),"RIGHT"),
        ("ALIGN",(4,1),(-1,-1),"RIGHT"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C("#F5F3FF"),colors.white]),
        ("TOPPADDING",(0,1),(-1,-1),7),("BOTTOMPADDING",(0,1),(-1,-1),7),
        ("GRID",(0,0),(-1,-1),0.5,C("#E9D5FF")),
    ]))
    els.append(tbl)
    els.append(Spacer(1,6*mm))

    tot_tbl = Table([
        ["Subtotal",   f"Rs.{total:,.2f}"],
        ["GST (18%)",  f"Rs.{tax:,.2f}"],
        ["GRAND TOTAL",f"Rs.{grand:,.2f}"],
    ], colWidths=[115*mm, 50*mm])
    tot_tbl.setStyle(TableStyle([
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("ALIGN",(1,0),(1,-1),"RIGHT"),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("LINEABOVE",(0,-1),(-1,-1),1.5,C("#7C3AED")),
        ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,-1),(-1,-1),13),
        ("TEXTCOLOR",(0,-1),(-1,-1),C("#7C3AED")),
    ]))
    els.append(tot_tbl)
    els.append(Spacer(1,10*mm))
    els.append(HRFlowable(width="100%", thickness=0.5, color=C("#E5E7EB")))
    els.append(Spacer(1,3*mm))
    els.append(Paragraph("Thank you for your purchase! | RetailOS — Smart Retail Management", footer_s))
    els.append(Paragraph("support@retailos.in  |  www.retailos.in", footer_s))

    doc.build(els)
    buffer.seek(0)
    return buffer.read()
