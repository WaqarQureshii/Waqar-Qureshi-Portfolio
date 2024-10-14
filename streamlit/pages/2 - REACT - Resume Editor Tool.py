import streamlit as st
import openai

st.set_page_config(layout="wide",
                   page_title="REACT: Resume Enhancement and Customization Tool",
                   initial_sidebar_state="collapsed")

st.title("REACT: Resume Enhancement and Customization Tool")
st.write("Resume Enhancement and Customization Tool (REACT) is pre-trained to be an action-oriented resume editor that takes your resume & your selected job description as a prompt. What differentiates this from other resume editors? It is action-oriented, maintains the spirit of your original resume, and incorporates the key job description skillsets that a hiring manager would look for.")

api_key = st.text_input("Input your Open AI API key",placeholder="sk-proj-XXXXXXXXXXX")
if 'valid_api_key' not in st.session_state:
     st.session_state['valid_api_key'] = False

def validate_api_key(api_key=api_key):
    client=openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
        st.session_state['valid_api_key']=True
    except openai.AuthenticationError:
        st.session_state['valid_api_key']=False
    except openai.APIConnectionError:
        st.session_state['valid_api_key']=False
validate_api_key = st.button("Validate Key", key="validate_api_key", on_click=validate_api_key)

if st.session_state['valid_api_key'] == False:
    st.error("Error with Open AI API Key")
else:
    st.success("Valid API Key")
    with st.form(key="resume form"):
        col1, col2, col3, col4 = st.columns(4)
        job_title = col1.text_area(label="Copy and paste job title", placeholder="Senior Financial Analyst")
        company_name = col2.text_area(label="Insert company name", placeholder="Nvidia Corporation")
        industry = col3.text_area(label="Insert your industry", placeholder="Finance")
        highlight_years = col4.slider(label="Number of years of experience you'd like to highlight - this will show up in your professional profile.", min_value=0, max_value=99, step=1)

        aboutcol1, aboutcol2 = st.columns(2)
        
        about_us = aboutcol1.text_area(label="Copy and paste the \"About Us\" section from the job description/website.", placeholder="NVIDIA has continuously reinvented itself over two decades. Our invention of the GPU in 1999 sparked the growth of the PC gaming market, redefined modern computer graphics, and revolutionized parallel computing. More recently, GPU deep learning ignited modern AI — the next era of computing. NVIDIA is a “learning machine” that constantly evolves by adapting to new opportunities that are hard to solve, that only we can tackle, and that matter to the world. This is our life's work, to amplify human imagination and intelligence. Make the choice, join our diverse team today!", height=1)
        
        additional_information = aboutcol2.text_area(label="Additional Information", placeholder="NVIDIA, founded in 1993, is a key innovator in computer graphics and AI technology. They invented the GPU in 1999, which transformed PC gaming and redefined computer graphics. NVIDIA specializes in products and platforms for gaming, professional visualization, data center, and automotive markets123.")
        
        jobdescription = st.text_area(label="Job description", placeholder='''We are looking for a Senior Financial Analyst to join our Information Technology FP&A team. The team is responsible for P&L forecasting and reporting as well as providing financial analysis that enables informed decision making across the company. This role is critical within our Finance department, requiring advanced tools and analytical skills, attention to detail, and the ability to meet deadlines. We are looking for a candidate with strong financial modeling abilities, and the capacity to thrive in a fast-paced environment.

        What you'll be doing:
        Complete monthly and quarterly financial closing, planning, and reporting processes.
        Focus areas will be Networking & Infrastructure.
        Build and maintain robust financial models for accurate forecasting and analysis.
        Monitor business performance metrics and provide insights on key drivers.
        Continuously drive operational improvement in financial consolidation and reporting activities.
        Collaborate with BU finance, cost accounting, and operations teams to maintain, validate, and reconcile data in forecasting and reporting systems.
        Prepare periodic internal financial reports and presentation materials.
        Partner with FP&A teams to maintain hierarchies and mappings needed for management and external reporting.

        What we need to see:
        8+ years of experience in finance, business, or analytics, within a global, high-tech corporation.
        Bachelor’s degree in finance, accounting, economics, or a business-related field (or equivalent experience).
        Proficiency in leading ERP systems (e.g., SAP, Oracle) and experience working with large datasets.
        Advanced Microsoft Excel skills are required. Experience with BPC, Tableau, Power BI, Python, SQL, and other visualization tools is a plus.
        An ability to balance being working in the weeds as well as seeing the big picture.
        Detail-orientated with a strong focus on accuracy and completeness.
        Excellent communication and interpersonal skills, with an ability to build relationships and collaborate with individuals at all levels of an organization.
        Ways to stand out from the crowd:
        Master’s degree in business administration, finance, or accounting.
        Experience in the Semiconductor industry or Corporate FP&A.
        Self-starter and problem solver, comfortable dealing with complexity, ambiguity, changes, and tight deadlines.
        Demonstration of high level analytical and financial modeling skills, with a proven track record of driving process and system improvements.
        ''', height=100)
        
        workexperience = st.text_area(label="Work experience", placeholder='''Senior Financial Analyst at ABC Corp
        Functions as a broker between the company's corporate finance and regional operations departments. Prepares post-close financial results versus budget analysis of spending with a focus on performance in key areas. Responds to ad-hoc requests for financial information from 17 operations personnel as needed. Reconciles accrued expense and advance payment balance-sheet accounts for assigned business units to ensure financial continuity per unit
                                    
        Financial Analyst at Clearwater:
        Updated all renovation-project spreadsheets to new commitments and monitored expenditures for budget compliance. Analyzed and reported variances on overtime expenditures by comparing payroll's OT Differential Report versus approved OT requests, resulting in 33% cost savings. Provided ongoing education and management consulting to ensure that all 77 stakeholders properly understood reports, methodologies, systems and source data.
        ''')

        latex_resume = st.text_area(label="Your LaTeX Resume, if you have one.", placeholder="Consider researching Jake's Resume on Overleaf if you don't have a resume written in LaTeX format.")
        
        submitted = st.form_submit_button(label="SUBMIT AND GENERATE")

    # PROMPTS TO FEED TO LLM
    prompt_prime1 = "I am re-writing my resume and I need your help. You are going to act as a professional resume writer skilled in presenting information concisely and using niche-appropriate language, while avoiding redundancy and cliché terms. Your task is to position my experience as a solution to my target company's pain points, tailoring it specifically so that it's clear that I can manage the primary requirements of the job. I want you to memorize these instructions for the duration of our session. Is that understood? No need to respond."

    prompt_prime2 = f'''First, I am going to provide you with the job description for the role I want to apply for. Can you read it carefully so that when I ask you questions about it later, you will reference the job description and provide me with accurate answers? No need to respond.

    Job Description:
    {jobdescription}'''

    prompt_prime3 = f"""Now I am going to provide you with more information on the hiring company, so you can tailor my work experience more effectively to the hiring company's needs. I want you to memorize this information so that you consider it when helping me rewrite my work experience later. Is that understood? No need to respond.

    Company name: {company_name}

    Information about the company:
    {about_us}

    Here is additional information about the company:
    {additional_information}
    """

    prompt_prime4 = f'''
    I am about to give you my resume which contains detailed information about my past work experiences. I want you to rewrite each work experience with resume bullet points, and please tailor each bullet point specifically for the {job_title} I sent you previously. By "tailor", I mean try to implement the following 6 actions for each bullet point
    1) Start each bullet point with an action verb, followed by the task, and conclude with the result. Please do your best to quantify each statement using numbers, percentages or dollar amounts.
    2) Ensure the bullet points include results-driven achievement statements
    3) Use similar language to what's written in the job description
    4) Use or leverage my existing work experiences such as the results, if there are no results, please create fictitious results that would work well with the job title provided earlier. 
    5) Try to keep the bullet points per work experience between 3 to 5 bullet points.
    6) Try to order the bullet points in the order of highest priority that will address the primary requirements of the job.

    I am now going to provide you my work experience:

    {workexperience}
    '''

    prompt_prime5 = f"Based on the {job_title} job description I sent to you earlier, what are the most important technical skills required for the job? Which technical skills would give me an advantage in this role? Keep the response in memory and no need to respond."

    prompt_prime6 = f"What are the most common areas of expertise for a {job_title}? Keep it in memory, no need to respond."

    prompt_prime7 = f"Using what you created for me with my work experience, write 3-6 sentences to summarize my professional experience, including only what's relevant to the {job_title} job description I sent you earlier. Highlight my {highlight_years} number of years of experience in the {industry} field. Showcase how my experience and expertise can address {company_name}'s pain points. Write it using resume language (passive third person). Keep this in memory and no need to respond."

    prompt_prime8 = f'''
    If I have not provided a valid LaTeX Resume tempalte in the next prompt, then please simply output a resume utilizing all of the information I have now provided to you.

    If I provide you a valid LaTeX resume template then please do the following:
    Could you please edit my current resume written in a latex template by utilizing all of the information I have now provided you? For example, replace all the work experiences currently in the template with the bullet points you have come up with, and replace the Professional Summary section with your summary of my professional experience.

    I will now either provide you a valid LaTeX Resume template or won't in the next prompt:

    '''

    prompt_prime9 = f'''
    My LaTeX Resume template:
    {latex_resume}
    '''

    if submitted:
        client=openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "user", "content": prompt_prime1},
                {"role": "user", "content": prompt_prime2},
                {"role": "user", "content": prompt_prime3},
                {"role": "user", "content": prompt_prime4},
                {"role": "user", "content": prompt_prime5},
                {"role": "user", "content": prompt_prime6},
                {"role": "user", "content": prompt_prime7},
                {"role": "user", "content": prompt_prime8},
                {"role": "user", "content": prompt_prime9},
            ]
        )

        st.write(response.choices[0].message.content)
        print(response.usage)