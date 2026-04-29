from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime

# -- Font setup: DejaVu if available, else Helvetica --
import os as _os
_dv = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
if _os.path.exists(_dv):
        pdfmetrics.registerFont(TTFont('DV',   _dv))
        pdfmetrics.registerFont(TTFont('DV-B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('DV-I', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))
        pdfmetrics.registerFont(TTFont('DV-BI','/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf'))
else:
        for _n, _r in [('DV','Helvetica'),('DV-B','Helvetica-Bold'),
                                          ('DV-I','Helvetica-Oblique'),('DV-BI','Helvetica-BoldOblique')]:
                                                      try: pdfmetrics.registerFont(pdfmetrics.Font(_n, _r, 'WinAnsiEncoding'))
                                                                  except: pass

                                              COMPANY_NAME  = "KLAUDHUB TECHSOLUTIONS PRIVATE LIMITED"
COMPANY_ALIAS = "(Cloudhubs)"
COMPANY_ADDR1 = "Registered Office: Flat 904, Manjeera Majestic Homes Soc 85356,"
COMPANY_ADDR2 = "KPHB, Tirumalagiri, Hyderabad - 500085, Telangana"
COMPANY_EMAIL = "hr@cloudhub.in"

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
        """Convert EmploymentTypeEnum.permanent to Permanent."""
    if not val:
                return '-'
            s = str(val)
    if '.' in s:
                s = s.split('.')[-1]
            return s.replace('_', ' ').title()

def _fmt(v):
        return f'Rs. {float(v):,.2f}' if v else 'Rs. 0.00'

def generate_salary_slip(employee, salary_record):
        buffer = io.BytesIO()
    doc = SimpleDocTemplate(
                buffer, pagesize=A4,
                topMargin=1.2*cm, bottomMargin=1.2*cm,
                leftMargin=1.5*cm, rightMargin=1.5*cm
    )
    story = []

    def ps(name, font='DV', size=9, color=colors.black, bold=False,
                      align=0, space_after=2, leading=None):
        return ParagraphStyle(name,
                                          fontName='DV-B' if bold else font,
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
    ]
    ded_rows = [
                ('Provident Fund (PF)',  salary_record.pf_deduction),
                ('Professional Tax',     salary_record.professional_tax),
                ('Income Tax (TDS)',     salary_record.income_tax),
    ]
    max_r  = max(len(earn_rows), len(ded_rows))
    earn_p = earn_rows + [('-', None)] * (max_r - len(earn_rows))
    ded_p  = ded_rows  + [('-', None)] * (max_r - len(ded_rows))

    wh = ps('wh', bold=True, color=colors.white, size=9)
    ed_data = [[
                Paragraph('EARNINGS', wh), Paragraph('Amount (Rs.)', wh),
                Paragraph('DEDUCTIONS', wh), Paragraph('Amount (Rs.)', wh),
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
                ('FONTNAME',(0,n-1),(-1,n-1),'DV-B'),
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


def _num_to_words(n):
        if n == 0: return 'Zero'
                ones = ['','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten',
                                    'Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen']
    tens_w = ['','','Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety']
    def _h(n):
                if n < 20: return ones[n]
                            return tens_w[n//10] + (' ' + ones[n%10] if n%10 else '')
    def _th(n):
                if n < 100: return _h(n)
                            return ones[n//100] + ' Hundred' + (' and ' + _h(n%100) if n%100 else '')
    if n < 0: return 'Minus ' + _num_to_words(-n)
            parts = []
    if n >= 10000000: parts.append(_th(n//10000000) + ' Crore');  n %= 10000000
            if n >= 100000:   parts.append(_th(n//100000)   + ' Lakh');   n %= 100000
                    if n >= 1000:     parts.append(_th(n//1000)     + ' Thousand'); n %= 1000
                            if n > 0:         parts.append(_th(n))
                                    return ' '.join(parts)
