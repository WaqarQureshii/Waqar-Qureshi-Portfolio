# Technology Stack

This document outlines the core technologies and libraries used in the project.

## Programming Language

- **Python**: Version >=3.13 is required.

## Frontend Framework

- **Streamlit**: Used for building the interactive web application interface.

## Data Storage

- **Firebase Firestore**: Utilized for storing lightweight metadata such as release dates, schemas, row counts, and update timestamps.
- **Google Cloud Storage**: Employed for storing actual data files in Parquet format, respecting Firestore's 1MB document limit.

## Data Processing & Analysis

- **Polars**: Preferred library for efficient DataFrame operations, over pandas.

## Visualization

- **Plotly**: Used for creating interactive charts and visualizations within the Streamlit application.

## API Integrations

- **FRED (Federal Reserve Economic Data)**: Integrated using the `fredapi` library for fetching economic data (e.g., DGS10, DGS2, CPIAUCSL, GDPC1, HOUST).
- **Yahoo Finance (yfinance)**: Used for accessing equity market data, historical prices, and company information for ticker symbols.
- **Stats Canada**: Integrated for fetching data using Product IDs (PIDs) like "36100434".

## Authentication

- **Google OAuth**: Planned for user authentication.

## Other Libraries

- **firebase-admin**: For interacting with Firebase services.
- **google-cloud-firestore**: Client library for Google Cloud Firestore.
- **google-cloud-storage**: Client library for Google Cloud Storage.
- **Authlib**: For authentication and authorization.
- **google-auth**: Google Authentication Library.
- **pyarrow**: For Arrow-based data manipulation, likely supporting Parquet files.
- **requests**: For making HTTP requests to external APIs.
