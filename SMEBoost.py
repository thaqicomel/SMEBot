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
        f"Explain with possible examples, Provide strategic implications and Maximum 180 words",
        "You are a helpful assistant specialized in providing business priority suggestions.",
        openai_api_key
    )

def get_specific_suggestions(business_info, suggestion_type, openai_api_key):
    """Get specific suggestions for business areas"""
    prompt = f"""Based on the user's stated business priorities:
{business_info}

Provide a {suggestion_type} analysis with exactly these requirements (Maximum 200 words):

1. List and describe the potential purposes and benefits
2. Explain linkages with earlier responses
3. Provide examples with specific facts and figures
4. List required information and preparation steps

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
def clean_text(text):
    """Clean text by removing markdown formatting"""
    if not text:
        return ""
    # Remove section markers
    text = text.replace('###', '')
    # Remove bullet points
    text = text.replace('- ', '')
    # Remove bold markers
    text = text.replace('**', '')
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Clean up any remaining markdown artifacts
    text = text.replace('_', ' ')
    text = text.replace('`', '')
    text = text.replace('*', '')
    text = text.replace('##', '')
    text = text.replace('....', '.')
    text = text.replace('...', '.')
    text = text.replace('..', '.')
    return text.strip()

def process_section(text):
    """Process a section of text, handling both title and content"""
    if ':' in text:
        title, content = text.split(':', 1)
        return clean_text(title), clean_text(content)
    return None, clean_text(text)

def create_custom_styles():
    """Create custom styles for the PDF document"""
    styles = getSampleStyleSheet()
    
    # Define all styles
    custom_styles = {
        'front_title': ParagraphStyle(
            'FrontTitle',
            parent=styles['Title'],
            fontSize=40,
            spaceAfter=50,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_LEFT,
            leading=44,
            fontName='Helvetica-Bold'
        ),
        'front_subtitle': ParagraphStyle(
            'FrontSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT,
            spaceBefore=100
        ),
        'front_date': ParagraphStyle(
            'FrontDate',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT,
            spaceBefore=10
        ),
        'toc_title': ParagraphStyle(
            'TOCTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_LEFT,
            leading=28,
            fontName='Helvetica-Bold'
        ),
        'toc_entry': ParagraphStyle(
            'TOCEntry',
            parent=styles['Normal'],
            fontSize=12,
            leading=18,
            textColor=colors.HexColor('#4d4d4d')
        ),
        'toc_entry_level2': ParagraphStyle(
            'TOCEntryLevel2',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            leftIndent=20,
            textColor=colors.HexColor('#666666')
        ),
        'title': ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            spaceAfter=30,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_LEFT,
            leading=32,
            fontName='Helvetica-Bold'
        ),
        'heading': ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceBefore=25,
            spaceAfter=15,
            alignment=TA_LEFT,
            leading=24,
            fontName='Helvetica-Bold'
        ),
        'subheading': ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceBefore=15,
            spaceAfter=10,
            alignment=TA_LEFT,
            leading=20,
            fontName='Helvetica-Bold'  # Ensure subheadings are bold
        ),
        'numbered_section': ParagraphStyle(
            'NumberedSection',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceBefore=15,
            spaceAfter=10,
            alignment=TA_LEFT,
            leading=20,
            fontName='Helvetica-Bold'  # Make numbered sections bold
        ),
        'content': ParagraphStyle(
            'CustomContent',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#4d4d4d'),
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=6
        ),
        'bullet': ParagraphStyle(
            'BulletPoint',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            leftIndent=20,
            bulletIndent=12,
            spaceBefore=6,
            spaceAfter=6,
            textColor=colors.HexColor('#4d4d4d')
        )
    }
    
    return custom_styles
def create_front_page(styles, profile_info):
    """Create the front page elements with fixed company logos"""
    elements = []
    
    # Create a table for the logos
    if os.path.exists("smeimge.jpg") and os.path.exists("finb.jpg"):
        logo_left = Image("smeimge.jpg", width=2*inch, height=1*inch)
        logo_right = Image("finb.jpg", width=2*inch, height=1*inch)
        
        logo_table = Table(
            [[logo_left, logo_right]], 
            colWidths=[4*inch, 2*inch],
            style=TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ])
        )
        elements.append(logo_table)
    
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("Business Analysis Report for SME", styles['front_title']))
    elements.append(Paragraph("Lite Version", styles['front_subtitle']))

    
    # Decorative line
    # line = Table([['']], colWidths=[5*inch], rowHeights=[2])
    # line.setStyle(TableStyle([
    #     ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
    #     ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1a1a1a')),
    # ]))
    # elements.append(line)
    
    # Company info
    # elements.append(Spacer(1, 30))
    # elements.append(Paragraph(f"Industry: {clean_text(profile_info.get('industry', 'N/A'))}", styles['front_subtitle']))
    # elements.append(Spacer(1, 10))
    # elements.append(Paragraph(f"Revenue Range: {clean_text(profile_info.get('revenue_range', 'N/A'))}", styles['front_subtitle']))
    # elements.append(Spacer(1, 40))
    
    # Date
    current_date = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")
    elements.append(Paragraph(f"Generated on: {current_date}", styles['front_date']))
    
    elements.append(PageBreak())
    return elements

def create_dynamic_toc(elements, styles, content_sections):
    """Create dynamic table of contents"""
    elements.append(Paragraph("Table of Contents", styles['toc_title']))
    elements.append(Spacer(1, 20))
    
    current_page = 2  # Start from page 2 (after front page)
    toc_entries = []
    e_page = 3
    # Build TOC entries dynamically
    toc_entries.append(("Executive Summary", e_page))
    current_page += 3
    
    if content_sections.get('business_areas'):
        toc_entries.append(("Selected Business Areas", current_page))
        current_page += 1
        for area in content_sections['business_areas']:
            toc_entries.append((f"    {area}", current_page))
            current_page += 1
    
    toc_entries.append(("Comprehensive Analysis", current_page))
    
    # Generate TOC entries with dot leaders
    for title, page in toc_entries:
        if title.startswith("    "):
            # Level 2 entry (indented)
            title = title.strip()
            elements.append(
                Paragraph(
                    f"{title} {'.' * (60 - len(title))} {page}",
                    styles['toc_entry_level2']
                )
            )
        else:
            # Level 1 entry
            elements.append(
                Paragraph(
                    f"{title} {'.' * (60 - len(title))} {page}",
                    styles['toc_entry']
                )
            )
    
    elements.append(PageBreak())
    return current_page

# def create_company_profile_table(styles, profile_info):
#     """Create a formatted table with company profile data"""
#     elements = []
    
#     elements.append(Paragraph("Company Profile", styles['title']))
    
#     # Define table data
#     data = [['Field', 'Value']]  # Header row
    
#     field_mapping = {
#         'revenue_range': 'Revenue Range',
#         'staff_strength': 'Staff Strength',
#         'customer_base': 'Customer Base',
#         'business_model': 'Business Model',
#         'industry': 'Industry',
#         'products_services': 'Products/Services',
#         'differentiation': 'Competitive Differentiation'
#     }
    
#     # Add profile info to table data in specified order
#     for key, display_name in field_mapping.items():
#         if key in profile_info:
#             data.append([display_name, str(profile_info[key]).strip()])
    
#     # Create table style
#     table_style = TableStyle([
#         # Header style
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 11),
#         ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
#         # Cell style
#         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 1), (-1, -1), 10),
#         ('ALIGN', (0, 0), (0, -1), 'LEFT'),
#         ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        
#         # Grid and colors
#         ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e6e6e6')),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.white),
#         ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        
#         # Padding
#         ('TOPPADDING', (0, 0), (-1, -1), 6),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
#         ('LEFTPADDING', (0, 0), (-1, -1), 12),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 12),
#     ])
    
#     table = Table(data, colWidths=[2.5*inch, 3.5*inch])
#     table.setStyle(table_style)
    
#     elements.append(table)
#     elements.append(Spacer(1, 20))
#     elements.append(PageBreak())
    
#     return elements

def create_header_footer(canvas, doc):
    """Add header and footer to each page with company logo"""
    canvas.saveState()
    
    if doc.page > 1:
        # Header with fixed logo
        if os.path.exists("finb.jpg"):
            canvas.drawImage("finb.jpg", 
                           letter[0] - 1.5*inch, 
                           letter[1] - 0.75*inch, 
                           width=1.3*inch, 
                           height=0.8*inch, 
                           preserveAspectRatio=True)
        
        canvas.setStrokeColor(colors.HexColor('#e6e6e6'))
        # canvas.line(inch, letter[1] - 0.5*inch, letter[0] - inch, letter[1] - 0.5*inch)
        
        # Footer
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.setFont('Helvetica', 9)
        
        # Page number
        page_num = f"Page {doc.page}"
        canvas.drawString(letter[0] - 2*inch, 0.5*inch, page_num)
        
        # Company name
        canvas.drawString(inch, 0.5*inch, "Business Analysis Report")
        
        # Footer line
        canvas.line(inch, 0.75*inch, letter[0] - inch, 0.75*inch)
    
    canvas.restoreState()
def generate_pdf(comprehensive_summary, profile_info, selected_areas, company_summary):
    """Generate the complete PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1.25*inch,
        leftMargin=1.25*inch,
        topMargin=1.25*inch,
        bottomMargin=inch
    )
    
    styles = create_custom_styles()
    elements = []
    
    # Front page with fixed logos
    elements.extend(create_front_page(styles, profile_info))
    
    # Table of Contents
    content_sections = {
        'business_areas': selected_areas,
        'analysis_sections': ["Comprehensive Analysis"]
    }
    create_dynamic_toc(elements, styles, content_sections)
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", styles['title']))
    if company_summary:
        elements.append(Paragraph(clean_text(company_summary), styles['content']))
    else:
        elements.append(Paragraph("No executive summary available.", styles['content']))
    elements.append(Spacer(1, 20))
    elements.append(PageBreak())
    
    # Company Profile
    #elements.extend(create_company_profile_table(styles, profile_info))
    
    # Selected Business Areas
    elements.append(Paragraph("Selected Business Areas", styles['title']))
    for area in selected_areas:
        elements.append(Paragraph(clean_text(area), styles['heading']))
        elements.append(Paragraph(clean_text(BUSINESS_OPTIONS[area]), styles['content']))
        
        # Add specific analysis
        area_key = f"{area.lower().replace(' ', '_')}_analysis"
        if area_key in st.session_state.user_data:
            elements.append(Paragraph("Analysis", styles['subheading']))
            analysis_text = clean_text(st.session_state.user_data[area_key])
            for paragraph in analysis_text.split('\n'):
                if paragraph.strip():
                    elements.append(Paragraph(paragraph.strip(), styles['content']))
            elements.append(PageBreak())
    
    # Comprehensive Analysis
    elements.append(Paragraph("Comprehensive Analysis", styles['title']))
    elements.append(Spacer(1, 20))
    
    # Define main sections and their variations
    main_sections = {
        "Synthesized Company Summary and Priorities": ["synthesized company summary", "company summary and priorities"],
        "5 Reasons for Needing an Advisor/Coach": ["reasons for needing", "specific reasons", "five specific reasons"],
        "Detailed Advisor/Coach Solutions": ["detailed advisor", "coach solutions", "advisor/coach solutions"],
        "Specific KPIs for Tracking Progress": ["specific kpis", "kpis for tracking", "tracking progress"]
    }
    
    if comprehensive_summary:
        # Clean up the text
        clean_text_content = comprehensive_summary.replace('#', '').replace('*', '')
        paragraphs = [p.strip() for p in clean_text_content.split('\n') if p.strip()]
        
        for paragraph in paragraphs:
            clean_paragraph = paragraph.strip()
            lower_paragraph = clean_paragraph.lower()
            
            # Check if this is a main section (or variation)
            is_main_section = False
            for section, variations in main_sections.items():
                if any(var in lower_paragraph for var in variations):
                    elements.append(Spacer(1, 20))
                    elements.append(Paragraph(section, styles['subheading']))
                    elements.append(Spacer(1, 10))
                    is_main_section = True
                    break
            
            if not is_main_section:
                # Check if it's a timing-related header
                if any(term in clean_paragraph for term in ['Short Term', 'Medium Term', 'Long Term']):
                    elements.append(Paragraph(clean_paragraph, styles['heading']))
                # Handle bullet points
                elif '•' in clean_paragraph or clean_paragraph.startswith('-'):
                    points = clean_paragraph.replace('-', '•').split('•')
                    for point in points:
                        if point.strip():
                            elements.append(Paragraph(f"• {clean_text(point)}", styles['bullet']))
                # Regular paragraphs
                else:
                    if clean_paragraph:
                        elements.append(Paragraph(clean_text(clean_paragraph), styles['content']))
                        elements.append(Spacer(1, 12))
    else:
        elements.append(Paragraph("No comprehensive analysis available.", styles['content']))

    # Build the PDF with header/footer
    doc.build(
        elements,
        onFirstPage=create_header_footer,
        onLaterPages=create_header_footer
    )
    buffer.seek(0)
    return buffer
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

# Helper function to wrap PDF generation with error handling
def generate_business_analysis_pdf(comprehensive_summary, profile_info, selected_areas, company_summary):
    """
    Wrapper function to handle PDF generation with error handling
    """
    try:
        return generate_pdf(comprehensive_summary, profile_info, selected_areas, company_summary)
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return create_error_pdf()

# Function to validate PDF inputs
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

# Main function to generate PDF report
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

# Example usage in Streamlit app
def offer_pdf_download(pdf_buffer):
    """Helper function to offer PDF download in Streamlit"""
    st.download_button(
        label="📥 Download Business Analysis Report",
        data=pdf_buffer,
        file_name=f"business_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        help="Click to download your complete business analysis report as PDF"
    )
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
                #     st.markdown("### Company Summary")
                #     st.write(company_summary)
                    
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
