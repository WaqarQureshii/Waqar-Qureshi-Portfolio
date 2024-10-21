import streamlit as st
import openai
import time

st.set_page_config(layout="wide",
                   page_title="REACT: Resume Enhancement and Customization Tool",
                   initial_sidebar_state="collapsed")

st.title("REACT: Resume Enhancement and Customization Tool")
st.write("Resume Enhancement and Customization Tool (REACT) is pre-trained to be an action-oriented resume editor that takes your resume & your selected job description as a prompt. What differentiates this from other resume editors? It is action-oriented, maintains the spirit of your original resume, and incorporates the key job description skillsets that a hiring manager would look for.")

api_key = st.text_input("Input your Open AI API key",placeholder="sk-proj-XXXXXXXXXXX")
if 'valid_api_key' not in st.session_state:
    st.warning("Input your Open AI API Key to get on your way to editing your resume.")
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

    # SETTING THE ROLE
    prompt_prime1 = "I am re-writing my resume and need your expertise. You specialize in crafting resumes that stand out in both human and ATS reviews. Your role is to present my work experience, skills, and relevant job descriptions concisely, with action-oriented language that avoids redundancy and clichés. The resume should be ATS-friendly while highlighting how my experience and skills solve the specific pain points of the target company. Tailor each section to show that I meet and exceed the primary job requirements. Please keep these instructions in mind throughout our session."

    # KEY INFORMATION FROM THE JOB DESCRIPTION
    prompt_prime2 = f'''First, I'll provide the job description for the role I want to apply for. Please review it carefully to identify:
        Key Technical Skills: The specific technical skills that would give me an advantage in this role.
        Key Soft Skills: The soft skills that the job description emphasizes.
        Key Language: Important phrases or terminology used that would give me an advantage if mirrored in my resume.
        Key Problems: The main challenges or pain points the company is trying to solve by hiring for this role.
        Job Description:
        {jobdescription}'''

    # KEY ORGANIZATIONAL INFORMATION
    prompt_prime3 = f"""Now I am going to provide you with more information on the hiring company, so you can tailor my work experience more effectively to the hiring company's needs. I want you to memorize this information as "Key Organizational Information"?

    Company name: {company_name}

    Information about the company:
    {about_us}

    Here is additional information about the company:
    {additional_information}
    """

    # WORK EXPERIENCES
    prompt_prime4 = f'''
    I will now provide my work experiences, which contain detailed information about my roles, responsibilities, and accomplishments. Please review them carefully and retain this information as 'Work Experiences.' I will ask you to leverage these details later to tailor my resume.

    Work Experiences:
    {workexperience}
    '''

    # COMMON AREAS OF EXPERTISE
    prompt_prime5 = f"What are the most common areas of expertise for a {job_title} role? Keep it in memory as the 'Common Areas of Expertise' "

    # RE-WRITE WORK EXPERIENCES
    prompt_prime6 = f'''
    Re-write my Work Experiences following these rules:

    1) Highlight the most relevant Key Technical Skills, Key Soft Skills, and Key Language that address the Key Problems (all of which should be retained in your memory).
    2) Focus on accomplishments, ordered by the importance of the skills, from most to least relevant to the job description.
    3) Avoid vague, non-specific words like 'several' or 'a variety of.' Use specific data and details. If my Work Experiences don’t provide specific figures, create realistic, context-appropriate fictitious data points.
    4) Quantify my achievements by incorporating numbers to emphasize the impact I've made.
    5) Begin each bullet point with a strong action or power verb, and vary the verbs throughout to avoid repetition.
    6) Keep bullet points succinct and to the point.
    7) Do not use personal pronouns.
    8) Use the formula: Power Verb + Result + Task OR Power Verb + Task + Result.
    9) Please focus on the "HOW" with details on how I accomplishments these results. For example "by building leveraging Power BI to merge 4 datasets into one user-friendly dashboard". 
    '''

    prompt_prime7 = f'''
    Build a summary of skills section of no more than 5 that align with the Key Technical Skills, Key Soft Skills and the Key Problems. Feel free to use my existing skillsets that I may provide in the next prompt in LaTeX format.
    '''

    prompt_prime8 = f"Using what you created for me with my work experience, write 3-6 sentences to summarize my professional experience, including only what's relevant to the {job_title} job description I sent you earlier. Highlight my {highlight_years} number of years of experience in the {industry} field. Showcase how my experience and expertise can address {company_name}'s Key Problems (mentioned before). Write it using the same Work Experiences rules provided earlier. Try to organize it from most to least important when considering getting the attention of my reader in relation to the job description and Key Problems."

    prompt_prime9 = f'''I want you to put everything together and all of the sections in generating a resume. If I don't provide you a resume in LaTeX format of my existing resume, then please output a new one that you wrote up based on all of the work you've completed so far. If I have provided you my resume in LaTeX format, then please replace all of the sections with the work you've done so far but keep my Name, phone number webpages, LinkedIn, job titles, job locations, job companies and time all the same.
    
    The next prompt with either include or not include a LaTeX template of my resume as discussed.
    '''

    prompt_prime10 = f'''
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
                {"role": "user", "content": prompt_prime10},
            ]
        )

        st.write(response.choices[0].message.content)
        for pct_complete in range(100):
            time.sleep(0.5)
        print(response.usage)