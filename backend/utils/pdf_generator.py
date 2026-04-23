from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import cm
import io
from datetime import datetime

COMPANY_NAME = "KLAUDHUB TECHSOLUTIONS PRIVATE LIMITED"
COMPANY_ALIAS = "(Cloudhubs)"
COMPANY_ADDR1 = "Registered Office: Flat 904, Manjeera Majestic Homes Soc 85356,"
COMPANY_ADDR2 = "KPHB, Tirumalagiri, Hyderabad – 500085, Telangana"
COMPANY_EMAIL = "hr@cloudhub.in"
COMPANY_PAN   = "AABCK1234P"   # placeholder - update if needed
COMPANY_CIN   = "U72900TG2020PTC123456"  # placeholder

PRIMARY   = colors.HexColor('#1e3a5f')
SECONDARY = colors.HexColor('#2563eb')
LIGHT_BG  = colors.HexColor('#f0f4ff')
EARN_BG   = colors.HexColor('#e8f5e9')
DED_BG    = colors.HexColor('#fce4ec')
NET_BG    = colors.HexColor('#e3f2fd')
BORDER    = colors.HexColor('#b0bec5')

def generate_salary_slip(employee, salary_record):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.2*cm, bottomMargin=1.2*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm
    )
    styles = getSampleStyleSheet()
    story = []

    # ── Header ──
    co_style  = ParagraphStyle('Co',  fontName='Helvetica-Bold', fontSize=14, textColor=PRIMARY, spaceAfter=1)
    co2_style = ParagraphStyle('Co2', fontName='Helvetica-Bold', fontSize=10, textColor=SECONDARY, spaceAfter=1)
    ad_style  = ParagraphStyle('Ad',  fontName='Helvetica',      fontSize=8,  textColor=colors.HexColor('#555555'), spaceAfter=1)
    
    header_data = [[
        Paragraph(COMPANY_NAME, co_style),
        Paragraph("PAYSLIP", ParagraphStyle('PS', fontName='Helvetica-Bold', fontSize=18, textColor=PRIMARY, alignment=2))
    ],[
        Paragraph(COMPANY_ALIAS, co2_style),
        Paragraph(
            datetime(salary_record.year, salary_record.month, 1).strftime("%B %Y"),
            ParagraphStyle('MY', fontName='Helvetica', fontSize=11, textColor=SECONDARY, alignment=2)
        )
    ],[
        Paragraph(COMPANY_ADDR1, ad_style),
        Paragraph("", ad_style)
    ],[
        Paragraph(COMPANY_ADDR2 + " | " + COMPANY_EMAIL, ad_style),
        Paragraph("", ad_style)
    ]]
    ht = Table(header_data, colWidths=[12*cm, 6*cm])
    ht.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(ht)
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=6))

    # ── Employee Details ──
    doj = str(employee.date_of_joining) if employee.date_of_joining else "-"
    pf  = employee.pf_number  or "-"
    uan = employee.uan_number or "-"
    bank = (employee.bank_name or "-") + " / " + (employee.bank_account or "-")
    ifsc = employee.ifsc_code or "-"

    emp_data = [
        ["Employee ID",   employee.employee_id,          "Name",        f"{employee.first_name} {employee.last_name}"],
        ["Designation",   employee.designation or "-",   "Department",  employee.department or "-"],
        ["Date of Joining", doj,                         "Employment",  employee.employment_type or "-"],
        ["PF Number",     pf,                            "UAN Number",  uan],
        ["Bank / Account", bank,                         "IFSC Code",   ifsc],
    ]

    lbl_style = ParagraphStyle('Lbl', fontName='Helvetica-Bold', fontSize=8, textColor=PRIMARY)
    val_style = ParagraphStyle('Val', fontName='Helvetica', fontSize=8)

    emp_fmt = [[Paragraph(r[0],lbl_style), Paragraph(str(r[1]),val_style),
                Paragraph(r[2],lbl_style), Paragraph(str(r[3]),val_style)] for r in emp_data]

    et = Table(emp_fmt, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    et.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LIGHT_BG),
        ('BACKGROUND', (2,0), (2,-1), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#f8faff')]),
    ]))
    story.append(et)
    story.append(Spacer(1, 0.4*cm))

    # ── Working Days ──
    import calendar
    days_in_month = calendar.monthrange(salary_record.year, salary_record.month)[1]
    wd_data = [
        [Paragraph("ATTENDANCE DETAILS", ParagraphStyle('WH', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)),
         "", "", "", "", ""],
        [Paragraph("Days in Month", lbl_style), Paragraph(str(days_in_month), val_style),
         Paragraph("Working Days", lbl_style), Paragraph(str(days_in_month), val_style),
         Paragraph("Days Present", lbl_style), Paragraph(str(days_in_month), val_style)],
        [Paragraph("Days Absent", lbl_style), Paragraph("0", val_style),
         Paragraph("LOP Days", lbl_style), Paragraph("0", val_style),
         Paragraph("Paid Days", lbl_style), Paragraph(str(days_in_month), val_style)],
    ]
    wt = Table(wd_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    wt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('SPAN', (0,0), (-1,0)),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(wt)
    story.append(Spacer(1, 0.4*cm))

    # ── Earnings & Deductions (side by side) ──
    hdr_e = ParagraphStyle('He', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)
    hdr_d = ParagraphStyle('Hd', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)
    earn_rows = [
        ("Basic Salary",        salary_record.basic),
        ("House Rent Allowance (HRA)", salary_record.hra),
        ("Special Allowances",  salary_record.allowances),
        ("Performance Bonus",   salary_record.bonus),
    ]
    ded_rows = [
        ("Provident Fund (PF)", salary_record.pf_deduction),
        ("Professional Tax",    salary_record.professional_tax),
        ("Income Tax (TDS)",    salary_record.income_tax),
    ]

    def fmt_amt(v):
        return f"₹ {v:,.2f}" if v else "₹ 0.00"

    max_rows = max(len(earn_rows), len(ded_rows))
    earn_rows_padded = earn_rows + [("-", 0)] * (max_rows - len(earn_rows))
    ded_rows_padded  = ded_rows  + [("-", 0)] * (max_rows - len(ded_rows))

    combined = [
        [Paragraph("EARNINGS", hdr_e), Paragraph("Amount (₹)", hdr_e),
         Paragraph("DEDUCTIONS", hdr_d), Paragraph("Amount (₹)", hdr_d)]
    ]
    for (el, ev), (dl, dv) in zip(earn_rows_padded, ded_rows_padded):
        combined.append([
            Paragraph(el, val_style), Paragraph(fmt_amt(ev) if el != "-" else "-", val_style),
            Paragraph(dl, val_style), Paragraph(fmt_amt(dv) if dl != "-" else "-", val_style),
        ])
    # Total row
    combined.append([
        Paragraph("GROSS EARNINGS", lbl_style), Paragraph(fmt_amt(salary_record.gross_salary), lbl_style),
        Paragraph("TOTAL DEDUCTIONS", lbl_style), Paragraph(fmt_amt(salary_record.total_deductions), lbl_style),
    ])

    ct = Table(combined, colWidths=[5.5*cm, 3*cm, 5.5*cm, 4*cm])
    n = len(combined)
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#2e7d32')),
        ('BACKGROUND', (2,0), (3,0), colors.HexColor('#c62828')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,n-1), (1,n-1), EARN_BG),
        ('BACKGROUND', (2,n-1), (3,n-1), DED_BG),
        ('FONTNAME', (0,n-1), (-1,n-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,n-2), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.3*cm))

    # ── Net Pay Banner ──
    net_data = [[
        Paragraph("NET PAY (Take Home)", ParagraphStyle('NL', fontName='Helvetica-Bold', fontSize=12, textColor=PRIMARY)),
        Paragraph(fmt_amt(salary_record.net_salary), ParagraphStyle('NV', fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#1b5e20'), alignment=2)),
    ]]
    nt = Table(net_data, colWidths=[13*cm, 5*cm])
    nt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NET_BG),
        ('GRID', (0,0), (-1,-1), 1, PRIMARY),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(nt)
    story.append(Spacer(1, 0.3*cm))

    # ── Amount in Words ──
    try:
        net_int = int(salary_record.net_salary)
        words = _num_to_words(net_int)
        story.append(Paragraph(
            f"<b>Net Pay in Words:</b> {words} Only",
            ParagraphStyle('AW', fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#444'))
        ))
    except:
        pass
    story.append(Spacer(1, 0.3*cm))

    # ── Footer ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=4))
    footer_data = [[
        Paragraph("This is a system-generated payslip and does not require a physical signature.", 
                  ParagraphStyle('FT', fontName='Helvetica-Oblique', fontSize=7, textColor=colors.grey)),
        Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M')} | {COMPANY_NAME}",
                  ParagraphStyle('FD', fontName='Helvetica', fontSize=7, textColor=colors.grey, alignment=2)),
    ]]
    ft = Table(footer_data, colWidths=[9*cm, 9*cm])
    story.append(ft)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def _num_to_words(n):
    """Convert integer to Indian number words."""
    if n == 0: return "Zero"
    ones = ['','One','Two','Three','Four','Five','Six','Seven','Eight','Nine',
            'Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen',
            'Seventeen','Eighteen','Nineteen']
    tens = ['','','Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety']
    def _below_hundred(n):
        if n < 20: return ones[n]
        return tens[n//10] + (' ' + ones[n%10] if n%10 else '')
    def _below_thousand(n):
        if n < 100: return _below_hundred(n)
        return ones[n//100] + ' Hundred' + (' and ' + _below_hundred(n%100) if n%100 else '')
    if n < 0: return 'Minus ' + _num_to_words(-n)
    parts = []
    if n >= 10000000:
        parts.append(_below_thousand(n // 10000000) + ' Crore'); n %= 10000000
    if n >= 100000:
        parts.append(_below_thousand(n // 100000) + ' Lakh'); n %= 100000
    if n >= 1000:
        parts.append(_below_thousand(n // 1000) + ' Thousand'); n %= 1000
    if n > 0:
        parts.append(_below_thousand(n))
    return ' '.join(parts)
