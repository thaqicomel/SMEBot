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
import io
import json

# Constants
BUSINESS_OPTIONS = {
    "Business Evaluation": "I want to assess my company's worth, helping me make informed decisions and gain investor trust.",
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
    """Get specific business suggestions based on type"""
    return get_openai_response(
        f"Based on: {business_info} please provide examples with specific facts and figures and List out the types of "
        f"information that needs to be ready before a {suggestion_type} is carried out. Maximum 200 words",
        f"You are a helpful assistant specialized in providing {suggestion_type} suggestions. List and describe the "
        f"potential purposes of doing a valuation and how it will benefit users and Explain the linkages between what "
        f"is being answered here and the earlier responses given in terms of the {business_info} priorities in the "
        f"next 6 - 12 months",
        openai_api_key
    )

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
    Based on the following information, provide a comprehensive 800-word analysis:
    
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

def generate_pdf(comprehensive_summary):
    """Generate PDF report with proper styling and formatting"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6
    )
    
    content_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceBefore=6,
        spaceAfter=6
    )
    
    elements = []
    
    # Add title and date
    elements.append(Paragraph("Business Analysis and Advisory Recommendations", title_style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Format content sections
    sections = comprehensive_summary.split('\n\n')
    for section in sections:
        if section.strip():
            if ':' in section and section.split(':')[0].isupper():
                elements.append(Paragraph(section, heading_style))
            else:
                elements.append(Paragraph(section, content_style))
            elements.append(Spacer(1, 6))
    
    doc.build(elements)
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
        st.title("💬 SMEBoost Basic Architecture v0.1")
    with col2:
        logo_path = "OIP.jpeg"
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
        business_priority_suggestions = business_priority(f"Business priorities: {business_priorities}", openai_api_key)
        st.session_state.show_options = True
        st.session_state.user_data.update({
            'business_priority_suggestions': business_priority_suggestions
        })
    
    # Business Options
    if st.session_state.show_options:
        selected_options = render_business_options(business_priorities, openai_api_key)
        if selected_options:
            selected_areas = [opt for opt, selected in selected_options.items() if selected]
            
            if not selected_areas:
                st.warning("Please select at least one business area for analysis.")
            else:
                with st.spinner("Generating analysis for selected areas..."):
                    suggestions = {}
                    for option in selected_areas:
                        suggestion = get_specific_suggestions(business_priorities, option, openai_api_key)
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
