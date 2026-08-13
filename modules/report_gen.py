from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

def generate_pdf(debris_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("ORBIT-GUARD THREAT ASSESSMENT REPORT", styles["Title"]))
    elements.append(Paragraph("AI-Powered Space Debris Risk Analysis", styles["Normal"]))
    elements.append(Spacer(1, 20))
    table_data = [["#", "OBJECT NAME", "NORAD ID", "RISK LEVEL", "RISK SCORE", "PERIGEE (km)"]]
    for obj in debris_data:
        table_data.append([str(obj["priority_rank"]), obj["name"], str(obj["norad_id"]), obj["risk_level"], str(obj["risk_percent"])+"%", str(obj["perigee"])+" km"])
    t = Table(table_data, colWidths=[30, 160, 70, 80, 70, 80])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#003366")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f0f4f8")]),("GRID",(0,0),(-1,-1),0.5,colors.grey)]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer
