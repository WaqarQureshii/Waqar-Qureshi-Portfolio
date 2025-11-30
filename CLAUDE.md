# Project Context
When working with this codebase, prioritize readability over cleverness. Ask clarifying questions before making architectural changes.

## About This Project
- Building a data science webapp on Streamlit to showcase my quantitative and qualitative research.
- Preference to use Polars to handle database transformations.
- Use firebase and firestore together to store databases retrieved from API calls.
- Intelligently store databases and call APIs to update the database if an update exists.
- Databases to be used:
    - yfinance python package to get equity information
    - FRED API to get economic and debt data like yields, inflation, GDP, housing figures, household debt
    - statscan API to get Canadian economic data such as GDP, inflation by province
- I want there to be one homepage with an intro at a minimum, and any new pages to be under streamlit/pages with proper number formatting in the title.
- Include Streamlit's login feature with Google login.
    - if waqar.qureshi.uoft@gmail.com is logged in, they have special access to manage the databases and update manually as necessary.

## Standards
- Type hints required on all functions to make readability
- Data and graphs in the streamlit webapp to be interactable

## Common Commands
'''.venv/Scripts/Activate.ps1 ''' #activate virtual environment
'''streamlit run Home.py''' # run streamlit webapp locally on web browser from root folder.
