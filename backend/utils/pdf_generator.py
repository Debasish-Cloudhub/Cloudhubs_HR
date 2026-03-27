from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
import io
from datetime import datetime
def generate_salary_slip(employee, salary_record):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    elements = []
    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=16, textColor=colors.HexColor('#1a237e'))
    sub_style = ParagraphStyle('S', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    elements.append(Paragraph("CloudHub Technologies Pvt. Ltd.", title_style))
    elements.append(Paragraph("Hitech City, Hyderabad - 500081 | hr@cloudhub.in", sub_style))
    elements.append(Spacer(1, 0.3*cm))
    month_name = datetime(salary_record.year, salary_record.month, 1).strftime("%B %Y")
    elements.append(Paragraph(f"SALARY SLIP - {month_name}", styles['h2']))
    elements.append(Spacer(1, 0.3*cm))
    emp_data = [["Employee ID", employee.employee_id, "Name", f"{employee.first_name} {employee.last_name}"],
                ["Designation", employee.designation or "-", "Department", employee.department or "-"],
                ["Bank", employee.bank_name or "-", "Account", employee.bank_account or "-"]]
    et = Table(emp_data, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    et.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),colors.HexColor('#e8eaf6')),('BACKGROUND',(2,0),(2,-1),colors.HexColor('#e8eaf6')),('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),9),('GRID',(0,0),(-1,-1),0.5,colors.grey),('PADDING',(0,0),(-1,-1),5)]))
    elements.append(et)
    elements.append(Spacer(1, 0.4*cm))
    for title, rows in [("EARNINGS",[["Basic",salary_record.basic],["HRA",salary_record.hra],["Allowances",salary_record.allowances],["Bonus",salary_record.bonus],["Gross",salary_record.gross_salary]]),("DEDUCTIONS",[["PF",salary_record.pf_deduction],["Prof Tax",salary_record.professional_tax],["Income Tax",salary_record.income_tax],["Total",salary_record.total_deductions],["NET SALARY",salary_record.net_salary]])]:
        data = [[title,"Amount (INR)"]]+[[r[0],f"{r[1]:,.2f}"] for r in rows]
        t = Table(data, colWidths=[10*cm, 8*cm])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a237e')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),10),('BACKGROUND',(0,-1),(-1,-1),colors.HexColor('#e8eaf6')),('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),0.5,colors.grey),('PADDING',(0,0),(-1,-1),6)]))
        elements.append(t); elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M')}", sub_style))
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()