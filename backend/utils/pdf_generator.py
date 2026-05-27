from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime
import json

# -- Font setup --
import os as _os
_dv = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
if _os.path.exists(_dv):
    pdfmetrics.registerFont(TTFont('DV',   _dv))
    pdfmetrics.registerFont(TTFont('DV-B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DV-I', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))
    pdfmetrics.registerFont(TTFont('DV-BI','/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf'))
    F_REG = 'DV'
    F_BLD = 'DV-B'
else:
    # Use standard built-in fonts
    F_REG = 'Helvetica'
    F_BLD = 'Helvetica-Bold'

COMPANY_NAME  = "KLAUDHUB TECHSOLUTIONS PRIVATE LIMITED"
COMPANY_ALIAS = "(CloudHub)"
COMPANY_ADDR1 = "Registered Office: Flat 904, Manjeera Majestic Homes Soc 85356,"
COMPANY_ADDR2 = "KPHB, Tirumalagiri, Hyderabad - 500085, Telangana"
COMPANY_EMAIL = "hr@cloudhubs.in"

PRIMARY   = colors.HexColor('#1e3a5f')
SECONDARY = colors.HexColor('#2563eb')
LIGHT_BG  = colors.HexColor('#e8eef8')
EARN_BG   = colors.HexColor('#e8f5e9')
DED_BG    = colors.HexColor('#fce4ec')
NET_BG    = colors.HexColor('#e3f2fd')
BORDER    = colors.HexColor('#b0bec5')
EARN_HDR  = colors.HexColor('#1b5e20')
DED_HDR   = colors.HexColor('#b71c1c')

def _clean_employment_type(val):
    if not val:
        return '-'
    return str(val).replace('_', ' ').title()

def _fmt(v):
    if v is None: return 'INR 0.00'
    return f"INR {float(v):,.2f}"

def _json_rows(value):
    if not value:
        return []
    try:
        rows = json.loads(value) if isinstance(value, str) else value
    except Exception:
        return []
    return [r for r in rows if r.get('name') and float(r.get('amount') or 0) != 0]

def generate_salary_slip(employee, salary_record):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.2*cm, bottomMargin=1.2*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm
    )
    story = []

    def ps(name, font=F_REG, size=9, color=colors.black, bold=False,
                       align=0, space_after=2, leading=None):
        return ParagraphStyle(name,
                              fontName=F_BLD if bold else font,
                              fontSize=size,
                              textColor=color,
                              alignment=align,
                              spaceAfter=space_after,
                              leading=leading or (size * 1.3)
                             )

    hdr_data = [[
        Paragraph(COMPANY_NAME, ps('cn', size=14, color=PRIMARY, bold=True)),
        Paragraph('PAYSLIP', ps('ps', size=20, color=PRIMARY, bold=True, align=2))
    ],[
        Paragraph(COMPANY_ALIAS, ps('ca', size=10, color=SECONDARY, bold=True)),
        Paragraph(datetime(salary_record.year, salary_record.month, 1).strftime('%B %Y'),
                  ps('my', size=11, color=SECONDARY, align=2))
    ],[
        Paragraph(COMPANY_ADDR1, ps('a1', size=8, color=colors.HexColor('#555'))),
        Paragraph('', ps('x'))
    ],[
        Paragraph(COMPANY_ADDR2 + ' | ' + COMPANY_EMAIL, ps('a2', size=8, color=colors.HexColor('#555'))),
        Paragraph('', ps('x'))
    ]]
    ht = Table(hdr_data, colWidths=[12*cm, 6*cm])
    ht.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),1)]))
    story.append(ht)
    story.append(HRFlowable(width='100%', thickness=2, color=PRIMARY, spaceAfter=6))

    lbl = ps('lbl', bold=True, color=PRIMARY, size=8)
    val = ps('val', size=8)

    doj      = str(employee.date_of_joining) if employee.date_of_joining else '-'
    emp_type = _clean_employment_type(employee.employment_type)
    pf       = employee.pf_number  or '-'
    uan      = employee.uan_number or '-'
    bank     = (employee.bank_name or '-') + ' / ' + (employee.bank_account or '-')
    ifsc     = employee.ifsc_code  or '-'
    full_name= f'{employee.first_name} {employee.last_name}'

    emp_rows = [
        ['Employee ID',    employee.employee_id,          'Name',        full_name],
        ['Designation',    employee.designation or '-',   'Department',  employee.department or '-'],
        ['Date of Joining', doj,                          'Employment',  emp_type],
        ['PF Number',      pf,                            'UAN Number',  uan],
        ['Bank / Account', bank,                          'IFSC Code',   ifsc],
    ]
    fmt_emp = [[Paragraph(r[0],lbl), Paragraph(str(r[1]),val),
                Paragraph(r[2],lbl), Paragraph(str(r[3]),val)] for r in emp_rows]
    et = Table(fmt_emp, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    et.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),LIGHT_BG), ('BACKGROUND',(2,0),(2,-1),LIGHT_BG),
        ('GRID',(0,0),(-1,-1),0.4,BORDER), ('PADDING',(0,0),(-1,-1),5),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.white, colors.HexColor('#f4f7ff')]),
    ]))
    story.append(et)
    story.append(Spacer(1, 0.4*cm))

    import calendar
    days = calendar.monthrange(salary_record.year, salary_record.month)[1]
    att_data = [
        [Paragraph('ATTENDANCE DETAILS', ps('ah', bold=True, color=colors.white, size=9)),'','','','',''],
        [Paragraph('Days in Month',lbl),Paragraph(str(days),val),
         Paragraph('Working Days',lbl),Paragraph(str(days),val),
         Paragraph('Days Present',lbl),Paragraph(str(days),val)],
        [Paragraph('Days Absent',lbl),Paragraph('0',val),
         Paragraph('LOP Days',lbl),Paragraph('0',val),
         Paragraph('Paid Days',lbl),Paragraph(str(days),val)],
    ]
    at = Table(att_data, colWidths=[3*cm,3*cm,3*cm,3*cm,3*cm,3*cm])
    at.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),PRIMARY), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('SPAN',(0,0),(-1,0)), ('GRID',(0,0),(-1,-1),0.4,BORDER), ('PADDING',(0,0),(-1,-1),5),
    ]))
    story.append(at)
    story.append(Spacer(1, 0.4*cm))

    earn_rows = [
        ('Basic Salary',               salary_record.basic),
        ('House Rent Allowance (HRA)', salary_record.hra),
        ('Special Allowances',         salary_record.allowances),
        ('Performance Bonus',          salary_record.bonus),
        ('Leave Travel Allowance (LTA)', getattr(salary_record, 'lta', 0)),
    ]
    earn_rows.extend((row.get('name'), row.get('amount')) for row in _json_rows(getattr(salary_record, 'extra_earnings', None)))
    ded_rows = [
        ('Provident Fund (PF)',  salary_record.pf_deduction),
        ('Professional Tax',     salary_record.professional_tax),
        ('Income Tax (TDS)',     salary_record.income_tax),
    ]
    ded_rows.extend((row.get('name'), row.get('amount')) for row in _json_rows(getattr(salary_record, 'extra_deductions', None)))
    ded_rows.extend(
        (row.get('name'), row.get('amount'))
        for row in _json_rows(getattr(salary_record, 'deduction_breakdown', None))
        if row.get('name') not in {'Provident Fund (PF)', 'Professional Tax', 'Income Tax (TDS)'}
    )
    max_r  = max(len(earn_rows), len(ded_rows))
    earn_p = earn_rows + [('-', None)] * (max_r - len(earn_rows))
    ded_p  = ded_rows  + [('-', None)] * (max_r - len(ded_rows))

    wh = ps('wh', bold=True, color=colors.white, size=9)
    ed_data = [[
        Paragraph('EARNINGS', wh), Paragraph('Amount (INR)', wh),
        Paragraph('DEDUCTIONS', wh), Paragraph('Amount (INR)', wh),
    ]]
    for (el, ev), (dl, dv) in zip(earn_p, ded_p):
        ed_data.append([
            Paragraph(el, val), Paragraph(_fmt(ev) if ev is not None else '-', val),
            Paragraph(dl, val), Paragraph(_fmt(dv) if dv is not None else '-', val),
        ])

    tot_lbl = ps('tl', bold=True, size=9)
    ed_data.append([
        Paragraph('GROSS EARNINGS',   tot_lbl), Paragraph(_fmt(salary_record.gross_salary),    tot_lbl),
        Paragraph('TOTAL DEDUCTIONS', tot_lbl), Paragraph(_fmt(salary_record.total_deductions),tot_lbl),
    ])
    n = len(ed_data)
    edt = Table(ed_data, colWidths=[5.5*cm, 3*cm, 5.5*cm, 4*cm])
    edt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(1,0),EARN_HDR), ('BACKGROUND',(2,0),(3,0),DED_HDR),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('BACKGROUND',(0,n-1),(1,n-1),EARN_BG), ('BACKGROUND',(2,n-1),(3,n-1),DED_BG),
        ('FONTNAME',(0,n-1),(-1,n-1),F_BLD),
        ('GRID',(0,0),(-1,-1),0.4,BORDER), ('PADDING',(0,0),(-1,-1),5),
        ('ROWBACKGROUNDS',(0,1),(-1,n-2),[colors.white, colors.HexColor('#f9fafb')]),
    ]))
    story.append(edt)
    story.append(Spacer(1, 0.3*cm))

    net_data = [[
        Paragraph('NET PAY (Take Home)', ps('nl', bold=True, size=12, color=PRIMARY)),
        Paragraph(_fmt(salary_record.net_salary), ps('nv', bold=True, size=14, color=colors.HexColor('#1b5e20'), align=2)),
    ]]
    nt = Table(net_data, colWidths=[13*cm, 5*cm])
    nt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),NET_BG), ('GRID',(0,0),(-1,-1),1,PRIMARY),
        ('PADDING',(0,0),(-1,-1),10), ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(nt)
    story.append(Spacer(1, 0.3*cm))

    try:
        words = _num_to_words(int(salary_record.net_salary))
        story.append(Paragraph(
            f'Net Pay in Words: {words} Only',
            ps('aw', size=8, color=colors.HexColor('#444'))
        ))
    except Exception:
        pass
    story.append(Spacer(1, 0.4*cm))

    story.append(HRFlowable(width='100%', thickness=0.5, color=BORDER, spaceAfter=4))
    ft_data = [[
        Paragraph('This is a system-generated payslip and does not require a physical signature.',
                  ps('fl', size=7, color=colors.grey)),
        Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M')} | {COMPANY_NAME}",
                  ps('fd', size=7, color=colors.grey, align=2)),
    ]]
    story.append(Table(ft_data, colWidths=[9*cm, 9*cm]))
    doc.build(story)
    buffer.seek(0)
    return buffer.read()

def generate_appraisal_report(employee, appraisal, manager=None, reviewers=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.4*cm, bottomMargin=1.2*cm,
        leftMargin=1.6*cm, rightMargin=1.6*cm
    )
    story = []

    def ps(name, font=F_REG, size=9, color=colors.black, bold=False, align=0, space_after=4, leading=None):
        return ParagraphStyle(
            name, fontName=F_BLD if bold else font, fontSize=size,
            textColor=color, alignment=align, spaceAfter=space_after,
            leading=leading or (size * 1.35)
        )

    story.append(Paragraph(COMPANY_NAME, ps('app_cn', size=14, color=PRIMARY, bold=True, align=1)))
    story.append(Paragraph(COMPANY_ALIAS, ps('app_ca', size=10, color=SECONDARY, bold=True, align=1)))
    story.append(Paragraph('APPRAISAL LETTER / REPORT', ps('app_title', size=18, color=PRIMARY, bold=True, align=1, space_after=10)))
    story.append(HRFlowable(width='100%', thickness=2, color=PRIMARY, spaceAfter=12))

    full_name = f'{employee.first_name} {employee.last_name}'
    manager_name = f'{manager.first_name} {manager.last_name}' if manager else '-'
    reviewer_names = ', '.join(f'{r.first_name} {r.last_name}' for r in (reviewers or [])) or '-'
    meta_rows = [
        ['Employee ID', employee.employee_id, 'Employee Name', full_name],
        ['Designation', employee.designation or '-', 'Department', employee.department or '-'],
        ['Appraisal Year', appraisal.appraisal_year or '-', 'Period', appraisal.period],
        ['Assigned Manager', manager_name, 'Additional Reviewers', reviewer_names],
        ['Final Status', appraisal.final_status or str(appraisal.status).replace('_', ' ').title(), 'Salary Hike %', appraisal.salary_hike_percent if appraisal.salary_hike_percent is not None else '-'],
    ]
    lbl = ps('app_lbl', bold=True, color=PRIMARY, size=8)
    val = ps('app_val', size=8)
    table = Table(
        [[Paragraph(str(r[0]), lbl), Paragraph(str(r[1]), val), Paragraph(str(r[2]), lbl), Paragraph(str(r[3]), val)] for r in meta_rows],
        colWidths=[3.4*cm, 5.2*cm, 3.4*cm, 5.8*cm]
    )
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),LIGHT_BG), ('BACKGROUND',(2,0),(2,-1),LIGHT_BG),
        ('GRID',(0,0),(-1,-1),0.4,BORDER), ('PADDING',(0,0),(-1,-1),5),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.4*cm))

    section = ps('app_section', bold=True, color=PRIMARY, size=11, space_after=6)
    body = ps('app_body', size=9, leading=13)
    for title, text in [
        ('Manager Feedback', appraisal.manager_feedback),
        ('Additional Reviewer Feedback', appraisal.additional_reviewer_feedback),
        ('Ratings / Comments', appraisal.comments),
    ]:
        story.append(Paragraph(title, section))
        story.append(Paragraph((text or '-').replace('\n', '<br/>'), body))
        story.append(Spacer(1, 0.2*cm))

    rating = appraisal.overall_rating if appraisal.overall_rating is not None else '-'
    story.append(Paragraph(f'<b>Overall Rating:</b> {rating}', body))
    approved_date = appraisal.approved_at.strftime('%d %B %Y') if appraisal.approved_at else datetime.now().strftime('%d %B %Y')
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph(
        f'This appraisal has been approved by HR/Admin on {approved_date}. This is a system-generated report and does not require a physical signature.',
        ps('app_note', size=8, color=colors.grey)
    ))
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def _num_to_words(n):
    if n == 0: return 'Zero'
    ones = ['','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten',
            'Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen']
    tens_w = ['','','Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety']
    def _h(num):
        if num < 20: return ones[num]
        return tens_w[num//10] + (' ' + ones[num%10] if num%10 else '')
    def _th(num):
        if num < 100: return _h(num)
        return ones[num//100] + ' Hundred' + (' and ' + _h(num%100) if num%100 else '')
    
    if n < 0: return 'Minus ' + _num_to_words(-n)
    
    parts = []
    if n >= 10000000:
        parts.append(_th(n//10000000) + ' Crore')
        n %= 10000000
    if n >= 100000:
        parts.append(_th(n//100000) + ' Lakh')
        n %= 100000
    if n >= 1000:
        parts.append(_th(n//1000) + ' Thousand')
        n %= 1000
    if n > 0:
        parts.append(_th(n))
    
    return ' '.join(parts)
