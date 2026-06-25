import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')

def generate_report(analysis_data, candidate_name="Candidate", resume_name="resume"):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"report_{candidate_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            rightMargin=inch*0.75, leftMargin=inch*0.75,
                            topMargin=inch, bottomMargin=inch)

    PRIMARY = colors.HexColor('#4F46E5')
    SECONDARY = colors.HexColor('#7C3AED')
    ACCENT = colors.HexColor('#06B6D4')
    DARK = colors.HexColor('#0F172A')
    LIGHT_BG = colors.HexColor('#F8FAFC')
    GREEN = colors.HexColor('#10B981')
    RED = colors.HexColor('#EF4444')

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                 textColor=colors.white, fontSize=22,
                                 fontName='Helvetica-Bold', alignment=TA_CENTER)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                   textColor=PRIMARY, fontSize=13,
                                   fontName='Helvetica-Bold', spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                textColor=DARK, fontSize=10,
                                fontName='Helvetica', leading=16)
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
                               textColor=colors.HexColor('#64748B'),
                               fontSize=9, fontName='Helvetica', leading=14)

    story = []

    # Header banner via table
    header_data = [[Paragraph(f"<b>Resumetic Analyzer</b>", title_style)],
                   [Paragraph("PDF Analyzer & ATS Score", ParagraphStyle('subtitle', textColor=colors.white, fontSize=12, fontName='Helvetica-Bold', alignment=TA_CENTER))],
                   [Paragraph(f"Resumetic Analyzer Report — {datetime.now().strftime('%B %d, %Y')}", 
                              ParagraphStyle('sub', textColor=colors.HexColor('#C7D2FE'),
                                            fontSize=10, fontName='Helvetica', alignment=TA_CENTER))]]
    header_table = Table(header_data, colWidths=[7*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 18),
        ('BOTTOMPADDING', (0,0), (-1,-1), 18),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 16))

    # Candidate info
    story.append(Paragraph("Candidate Information", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))
    info_data = [
        ["Candidate Name:", candidate_name],
        ["Resume File:", resume_name],
        ["Analysis Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    ]
    info_table = Table(info_data, colWidths=[2*inch, 5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), DARK),
        ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#475569')),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_BG, colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # Scores section
    story.append(Paragraph("Score Summary", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    ats = analysis_data.get('ats_score', 0)
    match = analysis_data.get('job_match', 0)
    ats_color = GREEN if ats >= 70 else (colors.HexColor('#F59E0B') if ats >= 50 else RED)
    match_color = GREEN if match >= 70 else (colors.HexColor('#F59E0B') if match >= 50 else RED)

    score_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Score</b>", body_style), Paragraph("<b>Rating</b>", body_style)],
        ["ATS Score", f"{ats}%", "Excellent" if ats >= 75 else ("Good" if ats >= 55 else "Needs Work")],
        ["Job Match", f"{match}%", "Excellent" if match >= 75 else ("Good" if match >= 55 else "Needs Work")],
    ]
    if 'breakdown' in analysis_data:
        bd = analysis_data['breakdown']
        score_data += [
            ["Skill Match", f"{bd.get('skill_match',0)}%", ""],
            ["Experience", f"{bd.get('experience',0)}%", ""],
            ["Education", f"{bd.get('education',0)}%", ""],
            ["Formatting", f"{bd.get('formatting',0)}%", ""],
        ]
    score_table = Table(score_data, colWidths=[3*inch, 2*inch, 2*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_BG, colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TEXTCOLOR', (1,2), (1,2), ats_color),
        ('TEXTCOLOR', (1,3), (1,3), match_color),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 16))

    # Skills found
    skills = analysis_data.get('skills_found', [])
    if skills:
        story.append(Paragraph("Skills Identified", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))
        skill_text = " • ".join(skills)
        story.append(Paragraph(skill_text, body_style))
        story.append(Spacer(1, 16))

    # Missing skills
    missing = analysis_data.get('missing_skills', [])
    if missing:
        story.append(Paragraph("Missing Skills (from Job Description)", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=RED, spaceAfter=8))
        miss_text = " • ".join(missing)
        p = ParagraphStyle('miss', parent=body_style, textColor=RED)
        story.append(Paragraph(miss_text, p))
        story.append(Spacer(1, 16))

    # Suggestions
    suggestions = analysis_data.get('suggestions', [])
    if suggestions:
        story.append(Paragraph("Improvement Suggestions", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=8))
        for i, s in enumerate(suggestions, 1):
            story.append(Paragraph(f"<b>{i}.</b> {s}", body_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 16))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0')))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Generated by Resumetic Analyzer • Confidential", sub_style))

    doc.build(story)
    return filepath, filename