import streamlit as st
from openai import OpenAI
import pandas as pd
from io import BytesIO
import datetime
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import io
import datetime
import io
import json

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

# OpenAI API functions
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
    """
    Get specific suggestions following the exact required format
    
    Args:
        business_info (str): Business priorities from previous responses
        suggestion_type (str): Type of analysis (e.g., Business Valuation, Financial Healthcheck)
        openai_api_key (str): OpenAI API key
    """
    prompt = f"""Based on the user's stated business priorities:
{business_info}

Provide a {suggestion_type} analysis with exactly these requirements (Maximum 200 words):

1. List and describe the potential purposes of doing a {suggestion_type} and how it will benefit users
   - Provide specific purposes tailored to their case
   - Clearly explain benefits for their situation
   - Make all examples relevant to their context

2. Explain the linkages between what is being answered here and the earlier responses given in terms of the user's priorities in the next 6-12 months
   - Show direct connections to their stated priorities
   - Demonstrate how {suggestion_type} supports their goals
   - Reference specific priorities from their input

3. Provide examples with specific facts and figures
   - Include concrete numbers and metrics
   - Use relevant industry benchmarks
   - Quantify potential benefits

4. List out the types of information that needs to be ready before a {suggestion_type} is carried out
   - Required documents
   - Essential data points
   - Preparation timeline

Keep responses specific to their context:
{business_info}"""

    system_prompt = f"""You are a specialized {suggestion_type} consultant responding to specific business priorities.
Your task:
1. Follow the exact 4-section format provided
2. Use only information from their business context
3. Make all examples specific to their situation
4. Keep within 200 words total
5. Avoid any generic advice or hypothetical scenarios

Important: Each section must directly reference the user's stated priorities and goals."""

    return get_openai_response(prompt, system_prompt, openai_api_key)

def get_company_summary(profile_info, openai_api_key):
    """Generate comprehensive company summary"""
    prompt = f"""
    Based on the following company profile, provide a comprehensive summary of the business:
    
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
        "You are a business analyst providing comprehensive company summaries.",
        openai_api_key
    )

def generate_comprehensive_summary(profile_info, business_priorities, company_summary, openai_api_key):
    """Generate comprehensive business analysis and recommendations"""
    prompt = f"""
    Based on the following information, provide a comprehensive 2000-word analysis:
    
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
        "You are a senior business consultant providing comprehensive analysis and recommendations.",
        openai_api_key
    )

def create_custom_styles():
    """Create custom styles for the PDF document"""
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1a237e'),  # Dark blue
        alignment=TA_CENTER
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#303f9f'),  # Medium blue
        spaceBefore=12,
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    # Section heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#1976d2'),  # Light blue
        spaceBefore=20,
        spaceAfter=10,
        leftIndent=0,
        borderPadding=(10, 0, 10, 0),
        borderWidth=0,
        borderColor=colors.HexColor('#e3f2fd')  # Very light blue
    )
    
    # Subheading style
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2196f3'),  # Bright blue
        spaceBefore=15,
        spaceAfter=8
    )
    
    # Body text style
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceBefore=6,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#424242')  # Dark gray
    )
    
    # List item style
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        leftIndent=20,
        bulletIndent=10,
        spaceBefore=3,
        spaceAfter=3,
        textColor=colors.HexColor('#424242')  # Dark gray
    )
    
    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'heading': heading_style,
        'subheading': subheading_style,
        'content': content_style,
        'list': list_style
    }

def create_header_footer(canvas, doc):
    """Add header and footer to each page"""
    canvas.saveState()
    
    # Header
    canvas.setFillColor(colors.HexColor('#1a237e'))
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(inch, letter[1] - 0.5*inch, "SMEBoost Business Analysis Report")
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(letter[0] - inch, letter[1] - 0.5*inch, 
                          f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    canvas.line(inch, letter[1] - 0.6*inch, letter[0] - inch, letter[1] - 0.6*inch)
    
    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.drawString(inch, 0.5*inch, "Confidential & Proprietary")
    
    # Center the page number
    page_num = f"Page {doc.page}"
    text_width = canvas._fontsize * len(page_num) * 0.5  # Approximate width
    x = (letter[0] - text_width) / 2
    canvas.drawString(x, 0.5*inch, page_num)
    
    canvas.line(inch, 0.7*inch, letter[0] - inch, 0.7*inch)
    
    canvas.restoreState()

def clean_text(text):
    """Clean text by removing special characters and formatting"""
    # Remove ### from headings
    text = text.replace('###', '')
    # Remove ** from emphasized text
    text = text.replace('**', '')
    # Clean up any extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def generate_pdf(comprehensive_summary):
    """Generate enhanced PDF report with proper styling and formatting"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=1.2*inch,
        bottomMargin=inch
    )
    
    styles = create_custom_styles()
    elements = []
    
    # Cover page
    elements.append(Paragraph("Business Analysis and Advisory Recommendations", styles['title']))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y')}", styles['subtitle']))
    elements.append(Spacer(1, 60))
    
    # Add a decorative line
    table_style = TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1a237e')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#1a237e'))
    ])
    elements.append(Table([['']], colWidths=[400], style=table_style))
    elements.append(PageBreak())
    
    # Format content sections
    sections = comprehensive_summary.split('\n\n')
    for section in sections:
        if not section.strip():
            continue
            
        if ':' in section:
            title, content = section.split(':', 1)
            # Clean both title and content
            title = clean_text(title)
            content = clean_text(content)
            
            if title.isupper():
                elements.append(Paragraph(title, styles['heading']))
                # Add a subtle line under main headings
                elements.append(Table([['']], colWidths=[400], style=TableStyle([
                    ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#e3f2fd'))
                ])))
                
                if content.strip():
                    # Process potential list items
                    if '\n-' in content or '\n•' in content:
                        for item in content.strip().split('\n'):
                            item = clean_text(item)
                            if item.startswith('-') or item.startswith('•'):
                                elements.append(Paragraph(f"•{item[1:]}", styles['list']))
                            else:
                                elements.append(Paragraph(item, styles['content']))
                    else:
                        elements.append(Paragraph(content, styles['content']))
            else:
                elements.append(Paragraph(f"{title}: {content}", styles['content']))
        else:
            cleaned_section = clean_text(section)
            if cleaned_section:
                elements.append(Paragraph(cleaned_section, styles['content']))
    
    # Build the PDF with header and footer
    doc.build(elements, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    buffer.seek(0)
    return buffer

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
    with st.expander("Business Priority Suggestions", expanded=True):
        st.write("Here are some business priority suggestions for you:")
        st.write(st.session_state.user_data['business_priority_suggestions'])

    st.write("### Business Areas for Analysis")
    st.write("Based on your priorities, consider these key business areas:")
    
    with st.form(key="business_options_form"):
        selected_options = {}
        for option, description in BUSINESS_OPTIONS.items():
            with st.expander(f"{option}", expanded=False):
                st.markdown(description)
                selected_options[option] = st.checkbox("Select this area for analysis", key=f"checkbox_{option}")
        
        if st.form_submit_button(label="Generate Analysis"):
            return selected_options
    return None

def render_business_profile_form():
    """Render business profile input form"""
    st.write("### Business Profile")
    st.write("Please provide information about your business to receive a customized analysis.")
    
    with st.form(key="enhanced_business_profile_form"):
        profile_info = {
            "revenue_range": st.radio(
                "Select your annual revenue range:",
                [
                    "Below $1 million",
                    "$1 million - $5 million",
                    "$5 million - $10 million",
                    "$10 million - $50 million",
                    "Above $50 million"
                ]
            ),
            "staff_strength": st.radio(
                "Select your current staff strength:",
                [
                    "1-10 employees",
                    "11-50 employees",
                    "51-200 employees",
                    "201-500 employees",
                    "More than 500 employees"
                ]
            ),
            "customer_base": st.radio(
                "Select your primary customer base:",
                [
                    "B2C (Direct to Consumers)",
                    "B2B (Business to Business)",
                    "B2G (Business to Government)",
                    "Mixed (Multiple Customer Types)"
                ]
            ),
            "business_model": st.text_area(
                "Describe how your company makes money:",
                height=100,
                help="Include your revenue streams, pricing model, and key partnerships if applicable."
            ),
            "industry": st.text_area(
                "Describe the industry you are operating in:",
                height=100,
                help="Include market size, growth trends, and key industry challenges."
            ),
            "products_services": st.text_area(
                "Describe your products/services:",
                height=100,
                help="Include your main offerings, target market, and value proposition."
            ),
            "differentiation": st.text_area(
                "Explain how you differentiate your business from competitors:",
                height=100,
                help="Include specific examples and unique selling propositions."
            )
        }
        
        if st.form_submit_button("Generate Business Profile Analysis"):
            return profile_info
    return None

def main():
    """Main application function with improved context handling"""
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
        # Store raw priorities
        st.session_state.user_data['raw_priorities'] = business_priorities
        # Get and store priority suggestions
        priority_suggestions = business_priority(
            f"Business priorities: {business_priorities}", 
            openai_api_key
        )
        st.session_state.user_data['business_priority_suggestions'] = priority_suggestions
        st.session_state.show_options = True
    
    # Business Options
    if st.session_state.show_options:
        selected_options = render_business_options(
            st.session_state.user_data.get('raw_priorities', ''), 
            openai_api_key
        )
        if selected_options:
            selected_areas = [opt for opt, selected in selected_options.items() if selected]
            
            if not selected_areas:
                st.warning("Please select at least one business area for analysis.")
            else:
                with st.spinner("Generating analysis for selected areas..."):
                    suggestions = {}
                    # Combine business context for analysis
                    business_context = f"""
                    Business Priorities:
                    {st.session_state.user_data.get('raw_priorities', '')}

                    Priority Analysis:
                    {st.session_state.user_data.get('business_priority_suggestions', '')}
                    """
                    
                    for option in selected_areas:
                        suggestion = get_specific_suggestions(
                            business_context.strip(), 
                            option,
                            openai_api_key
                        )
                        suggestions[f"{option.lower().replace(' ', '_')}_suggestions"] = suggestion
                    
                    st.session_state.user_data.update(suggestions)
                    st.session_state.show_profile = True
                    
                    st.write("### Analysis Results")
                    for option in selected_areas:
                        with st.expander(f"{option} Analysis", expanded=True):
                            st.markdown("**Description:**")
                            st.markdown(f"*{BUSINESS_OPTIONS[option]}*")
                            st.markdown("**Recommendations:**")
                            st.write(suggestions[f"{option.lower().replace(' ', '_')}_suggestions"])
    
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
                with st.expander("Company Profile Analysis", expanded=True):
                    st.markdown("### Company Summary")
                    st.write(company_summary)
                    
                    st.markdown("### Detailed Profile Information")
                    for key, value in profile_info.items():
                        st.markdown(f"**{key.replace('_', ' ').title()}**")
                        st.write(value)
                
                with st.expander("Comprehensive Analysis and Advisory Recommendations", expanded=True):
                    st.markdown("### Complete Business Analysis")
                    st.write(comprehensive_summary)
                
                # Generate and offer PDF download
                pdf_buffer = generate_pdf(comprehensive_summary)
                st.download_button(
                    label="Download Complete Analysis as PDF",
                    data=pdf_buffer,
                    file_name=f"business_analysis_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()
