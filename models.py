from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import date
import calendar

COMPANY_NAME = "CloudHub"
COMPANY_ADDRESS = [
    "Flat 904, Manjeera Majestic Homes Soc 85356",
    "KPHB Colony, Tirumalagiri",
    "Hyderabad 500085, Telangana"
]

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

PRIMARY_COLOR = colors.HexColor("#1a3a5c")
ACCENT_COLOR = colors.HexColor("#0ea5e9")
LIGHT_BG = colors.HexColor("#f0f7ff")
WHITE = colors.white
GRAY = colors.HexColor("#64748b")
DARK = colors.HexColor("#0f172a")

def generate_salary_slip(employee, salary_record) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    story = []

    # Header
    header_data = [
        [
            Paragraph(f"<font size='22'><b>{COMPANY_NAME}</b></font>", ParagraphStyle('co', alignment=TA_LEFT, textColor=PRIMARY_COLOR)),
            Paragraph(f"<font size='9' color='#64748b'>{COMPANY_ADDRESS[0]}<br/>{COMPANY_ADDRESS[1]}<br/>{COMPANY_ADDRESS[2]}</font>",
                      ParagraphStyle('addr', alignment=TA_RIGHT))
        ]
    ]
    header_table = Table(header_data, colWidths=[90*mm, 90*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_table)

    # Title bar
    month_name = MONTH_NAMES.get(salary_record.month, "")
    title_data = [[Paragraph(f"<font size='13' color='white'><b>SALARY SLIP — {month_name.upper()} {salary_record.year}</b></font>",
                             ParagraphStyle('title', alignment=TA_CENTER))]]
    title_table = Table(title_data, colWidths=[180*mm])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(title_table)
    story.append(Spacer(1, 8))

    # Employee details grid
    def info_row(label, value):
        return [
            Paragraph(f"<font size='9' color='#64748b'>{label}</font>", ParagraphStyle('lbl', alignment=TA_LEFT)),
            Paragraph(f"<font size='9'><b>{value or '—'}</b></font>", ParagraphStyle('val', alignment=TA_LEFT)),
        ]

    emp_data = [
        info_row("Employee Name", employee.full_name),
        info_row("Employee ID", employee.employee_id),
        info_row("Designation", employee.designation),
        info_row("Department", employee.department),
        info_row("Date of Joining", str(employee.date_of_joining) if employee.date_of_joining else None),
        info_row("Location", employee.location),
        info_row("Bank Name", employee.bank_name),
        info_row("Bank Account", employee.bank_account),
        info_row("PF Number", employee.pf_number),
        info_row("UAN", employee.uan),
        info_row("Worked Days", f"{salary_record.worked_days} / {salary_record.total_days}"),
        info_row("LOP Days", str(salary_record.lop_days)),
    ]

    # Split into two columns
    left_items = emp_data[:6]
    right_items = emp_data[6:]

    combined = []
    for i in range(max(len(left_items), len(right_items))):
        l = left_items[i] if i < len(left_items) else ["", ""]
        r = right_items[i] if i < len(right_items) else ["", ""]
        combined.append(l + [""] + r)

    emp_table = Table(combined, colWidths=[38*mm, 50*mm, 4*mm, 38*mm, 50*mm])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 10))

    # Earnings & Deductions tables side by side
    earn_header = [Paragraph("<font size='10' color='white'><b>EARNINGS</b></font>", ParagraphStyle('eh', alignment=TA_LEFT))]
    ded_header = [Paragraph("<font size='10' color='white'><b>DEDUCTIONS</b></font>", ParagraphStyle('dh', alignment=TA_LEFT))]

    def fmt(v):
        return f"₹ {v:,.2f}"

    earn_rows = [
        ["Basic Salary", fmt(salary_record.basic)],
        ["HRA", fmt(salary_record.hra)],
        ["Allowances", fmt(salary_record.allowances)],
        ["Bonus", fmt(salary_record.bonus)],
        ["", ""],
        [Paragraph("<b>Gross Earnings</b>", ParagraphStyle('g', fontSize=9)), Paragraph(f"<b>{fmt(salary_record.gross_salary)}</b>", ParagraphStyle('gv', fontSize=9, alignment=TA_RIGHT))],
    ]

    ded_rows = [
        ["Provident Fund (PF)", fmt(salary_record.pf)],
        ["Professional Tax", fmt(salary_record.professional_tax)],
        ["Income Tax (TDS)", fmt(salary_record.income_tax)],
        ["", ""],
        ["", ""],
        [Paragraph("<b>Total Deductions</b>", ParagraphStyle('td', fontSize=9)), Paragraph(f"<b>{fmt(salary_record.total_deductions)}</b>", ParagraphStyle('tdv', fontSize=9, alignment=TA_RIGHT))],
    ]

    def build_sub_table(rows, header_color):
        data = rows
        t = Table(data, colWidths=[50*mm, 32*mm])
        style = TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TEXTCOLOR', (1,0), (1,-1), DARK),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (0,-1), (-1,-1), LIGHT_BG),
            ('LINEABOVE', (0,-1), (-1,-1), 1, PRIMARY_COLOR),
        ])
        t.setStyle(style)
        return t

    earn_t = build_sub_table(earn_rows, ACCENT_COLOR)
    ded_t = build_sub_table(ded_rows, colors.HexColor("#dc2626"))

    # Headers
    earn_hdr = Table([[Paragraph("<font size='10' color='white'><b>EARNINGS</b></font>", ParagraphStyle('eh', alignment=TA_LEFT, leftIndent=8))]], colWidths=[82*mm])
    earn_hdr.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PRIMARY_COLOR),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))

    ded_hdr = Table([[Paragraph("<font size='10' color='white'><b>DEDUCTIONS</b></font>", ParagraphStyle('dh', alignment=TA_LEFT, leftIndent=8))]], colWidths=[82*mm])
    ded_hdr.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#dc2626")),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))

    side_by_side = Table(
        [[earn_hdr, Spacer(16,1), ded_hdr],
         [earn_t, Spacer(16,1), ded_t]],
        colWidths=[82*mm, 16*mm, 82*mm]
    )
    side_by_side.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(side_by_side)
    story.append(Spacer(1, 10))

    # Net Pay banner
    net_data = [[
        Paragraph("<font size='13' color='white'><b>NET PAY</b></font>", ParagraphStyle('np', alignment=TA_LEFT)),
        Paragraph(f"<font size='16' color='white'><b>{fmt(salary_record.net_salary)}</b></font>", ParagraphStyle('npv', alignment=TA_RIGHT))
    ]]
    net_table = Table(net_data, colWidths=[130*mm, 50*mm])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (0,0), 15),
        ('RIGHTPADDING', (-1,-1), (-1,-1), 15),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(net_table)
    story.append(Spacer(1, 15))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<font size='8' color='#94a3b8'>This is a computer-generated salary slip and does not require a physical signature. "
        f"Generated on {date.today().strftime('%d %B %Y')} by CloudHub HR Portal.</font>",
        ParagraphStyle('footer', alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
