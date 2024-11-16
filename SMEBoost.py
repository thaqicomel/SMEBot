import streamlit as st
from openai import OpenAI
import datetime
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageTemplate, Frame
from reportlab.lib.pagesizes import letter
import re

# Constants
BUSINESS_OPTIONS = {
    "Business Valuation": "I want to assess my company's worth, helping me make informed decisions and gain investor trust.",
    "Financial Healthcheck": "I want to review my finances, checking assets, debts, cash flow, and overall stability",
    "Business Partnering": "I want to build partnerships to grow, sharing strengths and resources with others for mutual benefit.",
    "Fund Raising": "I want to secure funds from investors to expand, innovate, or support my business operations.",
    "Bankability and Leverage": "I want to evaluate my creditworthiness, improving access to financing and managing debt effectively.",
    "Mergers and Acquisitions": "I want to pursue growth by combining my business with others, expanding resources and market reach.",
    "Budget and Resourcing": "I want to allocate resources wisely to achieve my goals efficiently and boost productivity.",
    "Business Remodelling": "I want to reshape my operations to stay relevant and seize new market opportunities.",
    "Succession Planning": "I want to prepare for future leadership transitions, ensuring the right people continue my business legacy."
}

def get_openai_response(prompt, system_content, api_key):
    """Get response from OpenAI API with error handling"""
    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error communicating with OpenAI API: {str(e)}")
        return None

def business_priority(business_info, openai_api_key):
    """Get business priority suggestions"""
    return get_openai_response(
        f"User Information: {business_info}. Please expand the given points, Synthesize and organise the inputs, "
        f"Explain with 3 possible examples, Provide strategic implications with supporting facts and examples and Maximum 250 words",
        "You are a top business coach who specialized in providing guidance.Make the language simple and relatable.",
        openai_api_key
    )

def get_specific_suggestions(business_info, suggestion_type, openai_api_key):
    """Get specific suggestions for business areas"""
    prompt = f"""Based on the user's stated business priorities:
{business_info}

Provide a {suggestion_type} analysis with exactly these requirements (Maximum 200 words):

1. Explain how to focus energy and resources on activities that directly support your stated priority - give 3 examples 
2. How to develop a clear plan with measurable milestones to ensure consistent progress toward your goal. Highlight and explain the importance of structured goal-setting in the specific context. 
3. Explain how to delegate tasks that do not align with your priority to maintain focus and efficiency - give examples om how to promote  prioritization and productivity.
4. Explain how to Communicate your priorities clearly to your team to ensure alignment and collective action." Provide examples on how to emphasize the value of shared understanding and collaboration.
5. Explain how to Regularly review your progress and adapt your approach to stay aligned with your desired outcomes." Give examples on how to Advocate for continuous evaluation and flexibility in this situation.


Keep responses specific to their context:
{business_info}"""

    return get_openai_response(prompt, 
        f"You are a specialized {suggestion_type} consultant responding to specific business priorities.",
        openai_api_key)
def generate_comprehensive_summary(profile_info, business_priorities, company_summary, openai_api_key):
    """Generate comprehensive business analysis and recommendations"""
    prompt = f"""
    Based on the following information, provide a comprehensive more than 1500-words analysis:
    
    Company Profile:
    {json.dumps(profile_info, indent=2)}
    
    Business Priorities: {business_priorities}
    
    Previous Analysis: {company_summary}
    
    Please provide:
    1. Synthesized company summary and priorities 
    2. 5 specific reasons for needing an advisor/coach 
    3. Detailed advisor/coach solutions for key pain points
    4. Specific KPIs for:
       - Short term (3 months)
       - Medium term (3-6 months)
       - Long term (6-12 months)
    """
    return get_openai_response(
        prompt,
        "You are a senior business consultant providing comprehensive analysis and recommendations",
        openai_api_key
    )
def get_company_summary(profile_info, openai_api_key):
    """Generate comprehensive company summary"""
    prompt = f"""
    Based on the following company profile, provide a comprehensive 1500-word summary of the business in a paragraph.I dont want in points:
    
    Annual Revenue Range: {profile_info['revenue_range']}
    Staff Strength: {profile_info['staff_strength']}
    Customer Base: {profile_info['customer_base']}
    Business Model: {profile_info['business_model']}
    Industry: {profile_info['industry']}
    Products/Services: {profile_info['products_services']}
    Competitive Differentiation: {profile_info['differentiation']}
    
    Please provide:
    1. Company profile analysis
    2. In-depth analysis of business needs
    3. Financial and operating summary with macro analysis
    4. SWOT Analysis
    5. Industry overview with supporting facts and statistics
    """
    return get_openai_response(
        prompt,
        "You are a business analyst providing comprehensive company summaries in a paragraph.",
        openai_api_key
    )
def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'show_options' not in st.session_state:
        st.session_state.show_options = False
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
def render_header():
    """Render application header"""
    col1, col2 = st.columns([3, 1])
    with col1:
        logo_path = "smeimge.jpg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
    with col2:
        logo_path = "finb.jpg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
def render_business_priority_form():
    """Render business priority input form"""
    with st.form(key="business_priority_form"):
        business_priorities = st.text_area(
            "#### TELL ME MORE ABOUT YOUR BUSINESS PRIORITIES IN THE NEXT 6 - 12 MONTHS",
            height=100
        )
        submit_button = st.form_submit_button(label="Enter")
        
        if submit_button and business_priorities:
            return business_priorities
    return None
def render_business_options(business_priorities, openai_api_key):
    """Render business options selection"""
    # Generate business priority suggestions if not already present
    if 'business_priority_suggestions' not in st.session_state.user_data:
        with st.spinner("Analyzing your business priorities..."):
            suggestions = business_priority(business_priorities, openai_api_key)
            if suggestions:
                st.session_state.user_data['business_priority_suggestions'] = suggestions
    
    # Display suggestions
    if st.session_state.user_data.get('business_priority_suggestions'):
        with st.expander("Business Priority Suggestions", expanded=True):
            st.write("Here are some business priority suggestions based on your input:")
            st.markdown(st.session_state.user_data['business_priority_suggestions'])
    
    st.write("### Business Areas for Analysis")
    st.write("Based on your priorities, select the relevant business areas:")
    
    with st.form(key="business_options_form"):
        selected_options = {}
        cols = st.columns(3)
        
        for idx, (option, description) in enumerate(BUSINESS_OPTIONS.items()):
            col = cols[idx % 3]
            with col:
                with st.expander(f"📊 {option}", expanded=False):
                    st.markdown(f"**{description}**")
                    selected_options[option] = st.checkbox(
                        "Select this area",
                        key=f"checkbox_{option}"
                    )
        
        submit = st.form_submit_button("💫 Generate Analysis for Selected Areas")
        if submit:
            return selected_options
    return None
def render_business_profile_form():
    """Render business profile form"""
    st.write("### Business Profile")
    st.write("Please provide information about your business to receive a customized analysis.")
    
    with st.form(key="business_profile_form"):
        profile_info = {
            "revenue_range": st.radio(
                "Select your annual revenue range:",
                ["Below RM 1 Million", 
                "RM 1-5 Million", 
                "RM 5-10 Million", 
                "RM 10-50 Million", 
                "Above RM 50 Million"]
            ),
            "staff_strength": st.radio(
                "Select your current staff strength:",
                ["1-10", "11-50", "51-200", "201-500", "500+"]
            ),
            "customer_base": st.radio(
                "Select your primary customer base:",
                ["Only Domestic", "Only off-shore", "Mixed"]
            ),
            "business_model": st.text_area(
                "Describe your business model:",
                height=100
            ),
            "industry": st.text_area(
                "Describe your industry:",
                height=100
            ),
            "products_services": st.text_area(
                "Describe your products/services:",
                height=100
            ),
            "differentiation": st.text_area(
                "Explain your competitive differentiation:",
                height=100
            )
        }
        
        if st.form_submit_button("Generate Analysis"):
            return profile_info
    return None

def create_custom_styles():
    """Create custom styles for the PDF document using Helvetica font family"""
    styles = getSampleStyleSheet()
    
    # Define modern color scheme
    custom_colors = {
        'primary': colors.HexColor('#1a1a1a'),      # Main text
        'secondary': colors.HexColor('#4A5568'),    # Secondary text
        'accent': colors.HexColor('#2B6CB0'),       # Titles and headings
        'subtle': colors.HexColor('#718096'),       # Subtle text
        'background': colors.HexColor('#F7FAFC'),   # Background elements
        'divider': colors.HexColor('#E2E8F0')       # Lines and dividers
    }
    
    custom_styles = {
        'front_title': ParagraphStyle(
            'FrontTitle',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=36,
            spaceAfter=40,
            textColor=custom_colors['accent'],
            alignment=TA_LEFT,
            leading=44
        ),
        'front_subtitle': ParagraphStyle(
            'FrontSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=18,
            textColor=custom_colors['secondary'],
            alignment=TA_LEFT,
            spaceBefore=100,
            leading=22
        ),
        'title': ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=28,
            spaceAfter=30,
            spaceBefore=20,
            textColor=colors.HexColor('#2B6CB0'),
            alignment=TA_LEFT,
            leading=34
        ),
        'heading': ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor('#1a1a1a'),
            spaceBefore=25,
            spaceAfter=15,
            alignment=TA_LEFT,
            leading=28
        ),
        'subheading': ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=custom_colors['secondary'],
            spaceBefore=20,
            spaceAfter=12,
            alignment=TA_LEFT,
            leading=24
        ),
        'content': ParagraphStyle(
            'CustomContent',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=18,
            textColor=custom_colors['primary'],
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=12,
            bulletIndent=12,
            firstLineIndent=0
        ),
        'bullet': ParagraphStyle(
            'BulletPoint',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=18,
            leftIndent=20,
            bulletIndent=12,
            spaceBefore=4,
            spaceAfter=4,
            textColor=custom_colors['primary']
        ),
        'table_header': ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=custom_colors['accent'],
            alignment=TA_LEFT,
            leading=16
        ),
        'table_cell': ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=custom_colors['primary'],
            alignment=TA_LEFT,
            leading=16
        ),
        'caption': ParagraphStyle(
            'Caption',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=custom_colors['subtle'],
            alignment=TA_LEFT,
            leading=12
        ),
        'toc_title': ParagraphStyle(
            'TOCTitle',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=24,
            spaceAfter=30,
            textColor=custom_colors['primary'],
            alignment=TA_LEFT,
            leading=28
        ),
        'toc_entry': ParagraphStyle(
            'TOCEntry',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=12,
            leading=18,
            textColor=custom_colors['primary']
        ),
        'toc_entry_level2': ParagraphStyle(
            'TOCEntryLevel2',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=16,
            leftIndent=20,
            textColor=custom_colors['secondary']
        ),
        'front_date': ParagraphStyle(
            'FrontDate',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=14,
            textColor=custom_colors['subtle'],
            alignment=TA_LEFT,
            spaceBefore=10
        )
    }
    
    return custom_styles

def process_section_content(content, styles, elements):
    """Process section content and add appropriate styling"""
    main_sections = {
        "Company Overview": ["company overview", "business overview"],
        "Market Analysis": ["market analysis", "industry analysis"],
        "Strategic Recommendations": ["strategic recommendations", "recommendations"],
        "Financial Implications": ["financial implications", "financial impact"],
        "Implementation Timeline": ["implementation timeline", "timeline"],
        "Risk Assessment": ["risk assessment", "risks"],
        "Next Steps": ["next steps", "action items"]
    }

    # Clean up the text
    clean_text_content = content.replace('#', '').replace('*', '')
    paragraphs = [p.strip() for p in clean_text_content.split('\n') if p.strip()]

    for paragraph in paragraphs:
        clean_paragraph = paragraph.strip()
        lower_paragraph = clean_paragraph.lower()

        # Check if this is a main section
        is_main_section = False
        for section, variations in main_sections.items():
            if any(var in lower_paragraph for var in variations):
                elements.append(Spacer(1, 20))
                elements.append(Paragraph(section, styles['subheading']))
                elements.append(Spacer(1, 10))
                is_main_section = True
                break

        if not is_main_section:
            # Handle bullet points
            if '•' in clean_paragraph or clean_paragraph.startswith('-'):
                points = clean_paragraph.replace('-', '•').split('•')
                for point in points:
                    if point.strip():
                        elements.append(Paragraph(f"• {clean_text(point)}", styles['bullet']))
            # Regular paragraphs
            else:
                if clean_paragraph:
                    elements.append(Paragraph(clean_text(clean_paragraph), styles['content']))
                    elements.append(Spacer(1, 12))

def generate_pdf(comprehensive_summary, profile_info, selected_areas, company_summary):
    """Generate the complete PDF report with enhanced styling and layout"""
    buffer = io.BytesIO()

    # Validate inputs before proceeding
    if not comprehensive_summary or not profile_info or not selected_areas or not company_summary:
        st.error("Missing required content for PDF generation")
        return create_error_pdf()

    try:
        # Create document with adjusted margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=1.25 * inch,
            leftMargin=1.25 * inch,
            topMargin=1.5 * inch,
            bottomMargin=1 * inch
        )

        # Create styles
        styles = create_custom_styles()

        # Build elements list
        elements = []

        # Front page
        if profile_info:
            elements.extend(create_front_page(styles, profile_info))
        else:
            elements.append(Paragraph("Profile Information Missing", styles['error']))

        # Table of Contents
        content_sections = {
            'business_areas': selected_areas
        }
        create_dynamic_toc(elements, styles, content_sections)

        # Executive Summary
        elements.append(Paragraph("Executive Summary", styles['title']))
        if company_summary:
            elements.extend(create_executive_summary_section(company_summary, styles))
        else:
            elements.append(Paragraph("Company Summary Missing", styles['error']))
        elements.append(PageBreak())

        # Selected Business Areas
        if selected_areas:
            elements.append(Paragraph("Selected Business Areas", styles['title']))
            for area in selected_areas:
                elements.append(Paragraph(area, styles['heading']))
                area_key = f"{area.lower().replace(' ', '_')}_analysis"

                # Add area analysis if available
                if area_key in st.session_state.user_data:
                    elements.extend(create_business_area_section(st.session_state.user_data[area_key], styles))
                else:
                    elements.append(Paragraph(f"Analysis for {area} is missing.", styles['error']))
                elements.append(PageBreak())
        else:
            elements.append(Paragraph("No business areas selected.", styles['error']))

        # Comprehensive Analysis
        if comprehensive_summary:
            elements.append(Paragraph("Comprehensive Analysis", styles['title']))
            content_elements = create_comprehensive_analysis_section(comprehensive_summary, styles)
            if content_elements:
                elements.extend(content_elements)
            else:
                elements.append(Paragraph("Comprehensive Analysis content is incomplete.", styles['error']))
        else:
            elements.append(Paragraph("Comprehensive Analysis Missing.", styles['error']))

        # Build the PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return create_error_pdf()

def create_dynamic_toc(elements, styles, content_sections):
    """Create dynamic table of contents with enhanced styling"""
    elements.append(Table([['']], colWidths=[7*inch], rowHeights=[2],
        style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#2B6CB0')),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ])
    ))
    
    elements.append(Paragraph("Table of Contents", styles['toc_title']))
    elements.append(Spacer(1, 30))
    
    current_page = 2  # Start after front page
    toc_entries = []
    
    # Executive Summary (always starts on page 3)
    toc_entries.append(("Executive Summary", 3))
    current_page = 4  # Next section starts after executive summary
    
    # Business Areas (each on new page)
    if content_sections.get('business_areas'):
        toc_entries.append(("Selected Business Areas", current_page))
        current_page += 1
        for area in content_sections['business_areas']:
            toc_entries.append((f"    {area}", current_page))
            current_page += 2  # Each area gets its own page + spacing
    
    # Comprehensive Analysis
    toc_entries.append(("Comprehensive Analysis", current_page))
    
    # Generate TOC entries with dot leaders
    for title, page in toc_entries:
        if title.startswith("    "):
            # Indent sub-entries
            title = title.strip()
            elements.append(
                Paragraph(
                    f"{title} {'.' * (60 - len(title))} {page}",
                    styles['toc_entry_level2']
                )
            )
        else:
            elements.append(
                Paragraph(
                    f"{title} {'.' * (60 - len(title))} {page}",
                    styles['toc_entry']
                )
            )
        elements.append(Spacer(1, 12))
    
    elements.append(Table([['']], colWidths=[7*inch], rowHeights=[2],
        style=TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#2B6CB0')),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ])
    ))
    
    elements.append(PageBreak())
    return current_page

def create_executive_summary_section(content, styles):
    """Create executive summary section with enhanced formatting"""
    elements = []
    paragraphs = content.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        if i == 0:
            # First paragraph with indentation
            para_style = ParagraphStyle(
                'IndentedContent',
                parent=styles['content'],
                firstLineIndent=36
            )
        else:
            para_style = styles['content']
        
        elements.append(Paragraph(clean_text(paragraph), para_style))
        elements.append(Spacer(1, 12))
    
    return elements

def create_page_background(canvas, doc):
    """Create background for each page"""
    canvas.saveState()
    canvas.setFillColor(colors.HexColor('#F7FAFC'))
    canvas.rect(0, 0, letter[0], letter[1], fill=True)
    canvas.restoreState()

def create_enhanced_header_footer(canvas, doc):
    """Create enhanced header and footer with logo and page numbers"""
    canvas.saveState()
    
    if doc.page > 1:
        # Header
        if os.path.exists("finb.jpg"):
            canvas.drawImage(
                "finb.jpg",
                doc.width + doc.rightMargin - 1.5*inch,
                doc.height + doc.topMargin - 0.6*inch,
                width=1.2*inch,
                height=0.5*inch,
                preserveAspectRatio=True
            )
        
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#2B6CB0'))
        canvas.drawString(
            doc.leftMargin,
            doc.height + doc.topMargin - 0.4*inch,
            "Business Analysis Report"
        )
        
        canvas.setStrokeColor(colors.HexColor('#E2E8F0'))
        canvas.setLineWidth(0.5)
        canvas.line(
            doc.leftMargin,
            doc.height + doc.topMargin - 0.7*inch,
            doc.width + doc.rightMargin,
            doc.height + doc.topMargin - 0.7*inch
        )
        
        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#4A5568'))
        
        page_num = f"Page {doc.page}"
        canvas.drawRightString(
            doc.width + doc.rightMargin,
            doc.bottomMargin - 0.25*inch,
            page_num
        )
        
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        canvas.drawString(
            doc.leftMargin,
            doc.bottomMargin - 0.25*inch,
            current_date
        )
        
        canvas.setStrokeColor(colors.HexColor('#E2E8F0'))
        canvas.line(
            doc.leftMargin,
            doc.bottomMargin - 0.125*inch,
            doc.width + doc.rightMargin,
            doc.bottomMargin - 0.125*inch
        )
    
    canvas.restoreState()

def create_business_area_section(content, styles):
    """Create beautifully formatted business area section"""
    elements = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith(('•', '-')):
            text = line.lstrip('•- ')
            elements.append(Paragraph(f"• {clean_text(text)}", styles['bullet']))
        elif line.startswith(('#', '##')):
            text = line.lstrip('#').strip()
            elements.append(Paragraph(clean_text(text), styles['subheading']))
            elements.append(Spacer(1, 6))
        else:
            elements.append(Paragraph(clean_text(line), styles['content']))
            elements.append(Spacer(1, 8))
    
    return elements

def create_section_styles(base_styles):
    """Create enhanced styles for comprehensive analysis"""
    return {
        'h1': ParagraphStyle(
            'Heading1',
            parent=base_styles['heading'],
            fontSize=24,
            spaceBefore=20,
            spaceAfter=15,
            textColor=colors.HexColor('#1a365d'),
            borderPadding=(10, 0, 10, 0),
            leading=28
        ),
        'h2': ParagraphStyle(
            'Heading2',
            parent=base_styles['subheading'],
            fontSize=18,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#2b6cb0'),
            leading=22
        ),
        'body': ParagraphStyle(
            'Body',
            parent=base_styles['content'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            firstLineIndent=20
        ),
        'highlight': ParagraphStyle(
            'Highlight',
            parent=base_styles['content'],
            fontSize=12,
            textColor=colors.HexColor('#2b6cb0'),
            backColor=colors.HexColor('#f7fafc'),
            borderPadding=10,
            leading=18
        )
    }

def create_comprehensive_analysis_section(content, styles):
    """Create structured comprehensive analysis section with improved formatting"""
    elements = []
    custom_styles = create_section_styles(styles)
    
    # Parse content into sections
    sections = parse_content_sections(content)
    
    # Company Overview Section
    elements.extend([
        create_section_header("Company Overview and Priorities", custom_styles['h1']),
        create_highlight_box(sections['summary'][0] if sections['summary'] else "", custom_styles)
    ])
    
    # for para in sections['summary'][1:]:
    #     elements.append(Paragraph(clean_text(para), custom_styles['body']))
    
    elements.append(PageBreak())
    
    # Key Reasons Section
    elements.append(create_section_header("Key Reasons for Advisory Support", custom_styles['h1']))
    elements.append(create_reasons_table(sections['reasons'], custom_styles))
    elements.append(PageBreak())
    
    # Solutions Section
    # elements.append(create_section_header("Strategic Solutions and Recommendations", custom_styles['h1']))
    # for category, points in sections['solutions'].items():
    #     elements.extend([
    #         Paragraph(clean_text(category), custom_styles['h2']),
    #         create_solution_box(points, custom_styles)
    #     ])
    
    # elements.append(PageBreak())
    
    # KPIs Section
    elements.append(create_section_header("Performance Metrics and Targets", custom_styles['h1']))
    kpi_periods = [
        ('short', 'Short Term (3 Months)'),
        ('medium', 'Medium Term (3-6 Months)'),
        ('long', 'Long Term (6-12 Months)')
    ]
    
    for period_key, period_title in kpi_periods:
        if sections['kpis'][period_key]:
            elements.extend([
                Paragraph(period_title, custom_styles['h2']),
                create_kpi_table(sections['kpis'][period_key], custom_styles)
            ])
    
    return elements

def parse_content_sections(content):
    """Parse comprehensive analysis content into structured sections"""
    sections = {
        "summary": [],
        "reasons": [],
        "solutions": {},
        "kpis": {
            "short": [],
            "medium": [],
            "long": []
        }
    }
    
    current_section = None
    current_subsection = None
    solution_category = None
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        lower_line = line.lower()
        
        # Identify sections
        if any(x in lower_line for x in ["synthesized company summary", "company summary and priorities"]):
            current_section = "summary"
            continue
        elif "reasons for needing" in lower_line or "5 reasons" in lower_line:
            current_section = "reasons"
            continue
        elif "detailed advisor/coach solutions" in lower_line or "coach solutions" in lower_line:
            current_section = "solutions"
            continue
        elif "short term" in lower_line and "month" in lower_line or "Short-term" in lower_line:
            current_section = "kpis"
            current_subsection = "short"
            continue
        elif "medium term" in lower_line and "month" in lower_line or "Medium-term" in lower_line:
            current_section = "kpis"
            current_subsection = "medium"
            continue
        elif "long term" in lower_line and "month" in lower_line or "Long-term" in lower_line:
            current_section = "kpis"
            current_subsection = "long"
            continue
        
        # Process content based on section
        if current_section == "summary":
            sections["summary"].append(line)
        elif current_section == "reasons":
            if any(char.isdigit() for char in line[:2]):
                cleaned_line = re.sub(r'^\d+\.?\s*', '', line)
                sections["reasons"].append(cleaned_line)
        elif current_section == "solutions":
            if not line.startswith(('•', '-', '*')) and len(line) < 50:
                solution_category = line
                if solution_category not in sections["solutions"]:
                    sections["solutions"][solution_category] = []
            elif solution_category and line.startswith(('•', '-', '*')):
                sections["solutions"][solution_category].append(line.lstrip('•- '))
        elif current_section == "kpis" and current_subsection:
            if line.startswith(('•', '-', '*')):
                sections["kpis"][current_subsection].append(line.lstrip('•- '))
    
    return sections

def create_section_header(title, style):
    """Create formatted section header with decorative elements"""
    return Table(
        [[Paragraph(title, style)]],
        colWidths=[7*inch],
        style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#2b6cb0')),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, 0), 15),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ])
    )

def create_highlight_box(text, styles):
    """Create highlighted box for key content"""
    return Table(
        [[Paragraph(clean_text(text), styles['highlight'])]],
        colWidths=[7*inch],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 8),
        ])
    )

def create_kpi_table(kpis, styles):
    """Create formatted table for KPIs"""
    if not kpis:
        return Spacer(1, 10)
        
    data = []
    for kpi in kpis:
        clean_kpi = clean_text(kpi)
        if clean_kpi:
            data.append([Paragraph(f"• {clean_kpi}", styles['body'])])
    
    if not data:
        return Spacer(1, 10)
    
    return Table(
        data,
        colWidths=[6.5*inch],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
    )

def create_reasons_table(reasons, styles):
    """Create formatted table for reasons section"""
    if not reasons:
        return Spacer(1, 10)
        
    data = []
    for i, reason in enumerate(reasons[:5]):
        clean_reason = clean_text(reason)
        if clean_reason:
            data.append([Paragraph(f"{i+1}. {clean_reason}", styles['body'])])
    
    if not data:
        return Spacer(1, 10)
    
    return Table(
        data,
        colWidths=[7*inch],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ])
    )

def create_solution_box(points, styles):
    """Create formatted box for solution points"""
    if not points:
        return Spacer(1, 10)
        
    data = []
    for point in points:
        clean_point = clean_text(point)
        if clean_point:
            data.append([Paragraph(f"• {clean_point}", styles['body'])])
    
    if not data:
        return Spacer(1, 10)
    
    return Table(
        data,
        colWidths=[6.5*inch],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
    )

def clean_text(text):
    """Clean text by removing markdown formatting"""
    if not text:
        return ""
    text = text.replace('###', '')
    text = text.replace('- ', '')
    text = text.replace('**', '')
    text = ' '.join(text.split())
    text = text.replace('_', ' ')
    text = text.replace('`', '')
    text = text.replace('*', '')
    text = text.replace('##', '')
    text = text.replace('....', '.')
    text = text.replace('...', '.')
    text = text.replace('..', '.')
    return text.strip()
def create_front_page(styles, profile_info):
    """Create front page with MyFinB logo placement"""
    elements = []
    
    # Create table for logo placement
    if os.path.exists("smeimge.jpg") and os.path.exists("finb.jpg"):
        logo_table = Table(
            [[
                Image("smeimge.jpg", width=2*inch, height=0.5*inch),
                '',  # Empty cell for spacing
                Image("finb.jpg", width=1.5*inch, height=0.5*inch)
            ]], 
            colWidths=[2.5*inch, 3*inch, 2*inch],
            style=TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (-1, 0), (-1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ])
        )
        elements.append(logo_table)
    
    elements.extend([
        Spacer(1, 1.5*inch),
        Paragraph("Business Analysis Report for SME", styles['front_title']),
        Paragraph("Lite Version", styles['front_subtitle']),
        Paragraph(
            f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y %I:%M %p')}", 
            styles['front_date']
        ),
        PageBreak()
    ])
    
    return elements

def create_error_pdf():
    """Create a simple PDF with error message if generation fails"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Add logos to error page
    if os.path.exists("smeimge.jpg") and os.path.exists("finb.jpg"):
        logo_left = Image("smeimge.jpg", width=2.5*inch, height=1.5*inch)
        logo_right = Image("finb.jpg", width=2.5*inch, height=1.5*inch)
        
        logo_table = Table(
            [[logo_left, logo_right]], 
            colWidths=[4*inch, 4*inch],
            style=TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ])
        )
        elements.append(logo_table)
    
    elements.extend([
        Spacer(1, inch),
        Paragraph("Error Generating Business Analysis Report", styles['Title']),
        Spacer(1, 30),
        Paragraph(
            "We apologize, but an error occurred while generating your report. "
            "Please ensure all required information is provided and try again.",
            styles['Normal']
        ),
        Spacer(1, 20),
        Paragraph(
            f"Time of Error: {datetime.datetime.now().strftime('%B %d, %Y %H:%M:%S')}",
            styles['Normal']
        )
    ])
    
    # Build the error PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def validate_pdf_inputs(profile_info, selected_areas, company_summary, comprehensive_summary):
    """
    Validate all required inputs for PDF generation
    Returns tuple (is_valid, error_message)
    """
    if not profile_info:
        return False, "Missing business profile information"
    
    required_fields = ['industry', 'revenue_range', 'business_model']
    missing_fields = [field for field in required_fields if not profile_info.get(field)]
    if missing_fields:
        return False, f"Missing required profile fields: {', '.join(missing_fields)}"
    
    if not selected_areas:
        return False, "No business areas selected"
    
    if not company_summary:
        return False, "Missing company summary"
    
    if not comprehensive_summary:
        return False, "Missing comprehensive analysis"
    
    return True, ""

def generate_business_analysis_pdf(comprehensive_summary, profile_info, selected_areas, company_summary):
    """
    Wrapper function to handle PDF generation with error handling
    """
    try:
        return generate_pdf(comprehensive_summary, profile_info, selected_areas, company_summary)
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return create_error_pdf()

def create_business_analysis_report(profile_info, selected_areas, company_summary, comprehensive_summary):
    """
    Main function to create the business analysis PDF report
    """
    # Validate inputs
    is_valid, error_message = validate_pdf_inputs(
        profile_info, selected_areas, company_summary, comprehensive_summary
    )
    
    if not is_valid:
        st.error(error_message)
        return create_error_pdf()
    
    # Generate the PDF report
    try:
        pdf_buffer = generate_business_analysis_pdf(
            comprehensive_summary,
            profile_info,
            selected_areas,
            company_summary
        )
        
        return pdf_buffer
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        return create_error_pdf()

def offer_pdf_download(pdf_buffer):
    """Helper function to offer PDF download in Streamlit"""
    st.download_button(
        label="📥 Download Business Analysis Report",
        data=pdf_buffer,
        file_name=f"business_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        help="Click to download your complete business analysis report as PDF"
    )

def process_section(text):
    """Process a section of text, handling both title and content"""
    if ':' in text:
        title, content = text.split(':', 1)
        return clean_text(title), clean_text(content)
    return None, clean_text(text)

def format_section(section_title, content, styles):
    """Format a section of the comprehensive analysis"""
    elements = []
    
    # Add section header
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(section_title, styles['subheading']))
    elements.append(Spacer(1, 10))
    
    # Process content
    for line in content:
        if line.startswith(('•', '-')):
            # Bullet points
            text = line.lstrip('•- ')
            elements.append(Paragraph(f"• {clean_text(text)}", styles['bullet']))
        else:
            # Regular paragraphs
            elements.append(Paragraph(clean_text(line), styles['content']))
    
    return elements

def create_header_footer(canvas, doc):
    """Add header and footer to each page with company logo"""
    canvas.saveState()
    
    if doc.page > 1:
        # Header with logo
        if os.path.exists("finb.jpg"):
            canvas.drawImage("finb.jpg", 
                           letter[0] - 1.5*inch, 
                           letter[1] - 0.75*inch, 
                           width=1.3*inch, 
                           height=0.8*inch, 
                           preserveAspectRatio=True)
        
        canvas.setStrokeColor(colors.HexColor('#e6e6e6'))
        
        # Footer
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.setFont('Helvetica', 9)
        page_num = f"Page {doc.page}"
        canvas.drawString(letter[0] - 2*inch, 0.5*inch, page_num)
        canvas.drawString(inch, 0.5*inch, "Business Analysis Report")
        canvas.line(inch, 0.75*inch, letter[0] - inch, 0.75*inch)
    
    canvas.restoreState()
def main():
    """Main application function"""
    initialize_session_state()
    render_header()
    
    # API Key input
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
        return
    
    st.write("The SMEBoost Lite GenAI platform is a streamlined, AI-powered version of the full SMEBoost program...")
    
    # Business Priority Form
    business_priorities = render_business_priority_form()
    if business_priorities:
        st.session_state.user_data['raw_priorities'] = business_priorities
        st.session_state.show_options = True
    
    # Business Options
    if st.session_state.show_options:
        selected_options = render_business_options(
            st.session_state.user_data.get('raw_priorities', ''),
            openai_api_key
        )
        
        if selected_options:
            selected_areas = [opt for opt, selected in selected_options.items() if selected]
            
            if selected_areas:
                st.session_state.user_data['selected_areas'] = selected_areas
                st.session_state.show_profile = True
                
                # Generate analysis for selected areas
                st.write("### Analysis Results")
                for option in selected_areas:
                    with st.expander(f"📊 {option} Analysis", expanded=True):
                        suggestion = get_specific_suggestions(
                            st.session_state.user_data.get('raw_priorities', ''),
                            option,
                            openai_api_key
                        )
                        if suggestion:
                            st.markdown("#### Overview")
                            st.markdown(f"*{BUSINESS_OPTIONS[option]}*")
                            st.markdown("#### Detailed Analysis")
                            st.markdown(suggestion)
                            st.session_state.user_data[f"{option.lower().replace(' ', '_')}_analysis"] = suggestion
    
    # Business Profile
    if st.session_state.show_profile:
        profile_info = render_business_profile_form()
        if profile_info:
            with st.spinner("Analyzing your business profile..."):
                company_summary = get_company_summary(profile_info, openai_api_key)
                comprehensive_summary = generate_comprehensive_summary(
                    profile_info,
                    st.session_state.user_data.get('business_priority_suggestions', ''),
                    company_summary,
                    openai_api_key
                )
                
                # Display analyses
                # with st.expander("Company Profile Analysis", expanded=True):
                #      st.markdown("### Company Summary")
                #      st.write(company_summary)
                    
                #     st.markdown("### Detailed Profile Information")
                #     for key, value in profile_info.items():
                #         st.markdown(f"**{key.replace('_', ' ').title()}**")
                #         st.write(value)
                
                with st.expander("Comprehensive Analysis and Advisory Recommendations", expanded=True):
                     st.markdown("### Complete Business Analysis")
                     st.write(comprehensive_summary)
                
                # Generate and offer PDF download
                pdf_buffer = generate_pdf(comprehensive_summary,profile_info,st.session_state.user_data['selected_areas'],company_summary)
                st.download_button(
                    label="Download Complete Analysis as PDF",
                    data=pdf_buffer,
                    file_name=f"business_analysis_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                    
                )
if __name__ == "__main__":
    main()
