"""
Google Sheets Handler Module for Personal Finance Survey Analyzer.

This module handles integration with Google Sheets API for loading survey data
and storing analysis results in the cloud.
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import os
import json
from src.utils import (
    display_success_message,
    display_error_message,
    display_loading_message
)


class GoogleSheetsHandler:
    """Handles Google Sheets API integration for data management."""

    # Define the scope for Google Sheets and Google Drive access
    SCOPE = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    def __init__(self, credentials_file='creds.json'):
        """
        Initialize Google Sheets handler.

        Args:
            credentials_file (str): Path to the credentials JSON file
        """
        self.credentials_file = credentials_file
        self.client = None
        self.spreadsheet = None
        self.connected = False

    def connect(self):
        """
        Establish connection to Google Sheets API.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            display_loading_message("Connecting to Google Sheets...")

            # Try to get credentials from environment variable first (for
            # Heroku)
            creds_json = os.environ.get('CREDS')

            if creds_json:
                # Running on Heroku - use environment variable
                creds_dict = json.loads(creds_json)
                creds = Credentials.from_service_account_info(
                    creds_dict, scopes=self.SCOPE)
            else:
                # Running locally - load from file
                creds = Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=self.SCOPE
                )

            # Authorize the client
            self.client = gspread.authorize(creds)
            self.connected = True

            display_success_message("Successfully connected to Google Sheets!")
            return True

        except FileNotFoundError:
            display_error_message(
                f"Credentials file not found: {
                    self.credentials_file}")
            display_error_message(
                "Please ensure creds.json is in the project root directory")
            return False
        except Exception as e:
            display_error_message(
                f"Failed to connect to Google Sheets: {
                    str(e)}")
            return False

    def open_spreadsheet(self, spreadsheet_name):
        """
        Open a Google Spreadsheet by name.

        Args:
            spreadsheet_name (str): Name of the spreadsheet

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            display_error_message(
                "Not connected to Google Sheets. Call connect() first.")
            return False

        try:
            display_loading_message(
                f"Opening spreadsheet: {spreadsheet_name}...")
            self.spreadsheet = self.client.open(spreadsheet_name)
            display_success_message(
                f"Spreadsheet '{spreadsheet_name}' opened successfully!")
            return True

        except gspread.exceptions.SpreadsheetNotFound:
            display_error_message(
                f"Spreadsheet '{spreadsheet_name}' not found")
            display_error_message(
                "Please check the spreadsheet name and sharing permissions")
            return False
        except Exception as e:
            display_error_message(f"Error opening spreadsheet: {str(e)}")
            return False

    def load_survey_data(self, worksheet_name='survey_data'):
        """
        Load survey data from a Google Sheets worksheet.

        Args:
            worksheet_name (str): Name of the worksheet containing survey data

        Returns:
            pd.DataFrame or None: Survey data as DataFrame, or None if error
        """
        if not self.spreadsheet:
            display_error_message(
                "No spreadsheet opened. Call open_spreadsheet() first.")
            return None

        try:
            display_loading_message(
                f"Loading data from worksheet: {worksheet_name}...")

            # Get the worksheet
            worksheet = self.spreadsheet.worksheet(worksheet_name)

            # Get all values from the worksheet
            data = worksheet.get_all_values()

            if not data or len(data) < 2:
                display_error_message("Worksheet is empty or has no data")
                return None

            # Convert to DataFrame (first row as headers)
            df = pd.DataFrame(data[1:], columns=data[0])

            # Convert numeric columns
            numeric_columns = [
                'age', 'annual_income', 'monthly_savings',
                'financial_literacy_score', 'emergency_fund_months'
            ]

            spending_cols = [
                col for col in df.columns if 'spending' in col.lower()]
            numeric_columns.extend(spending_cols)

            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Convert boolean columns
            boolean_columns = ['uses_mobile_banking', 'owns_crypto']
            for col in boolean_columns:
                if col in df.columns:
                    df[col] = df[col].str.lower().map(
                        {'yes': True, 'no': False})

            display_success_message(
                f"Loaded {
                    len(df)} records from Google Sheets!")
            return df

        except gspread.exceptions.WorksheetNotFound:
            display_error_message(f"Worksheet '{worksheet_name}' not found")
            return None
        except Exception as e:
            display_error_message(f"Error loading data: {str(e)}")
            return None

    def save_analysis_results(
            self,
            analysis_data,
            worksheet_name='analysis_results'):
        """
        Save analysis results to Google Sheets.

        Args:
            analysis_data (dict): Dictionary containing analysis results
            worksheet_name (str): Name of the worksheet to save results

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.spreadsheet:
            display_error_message(
                "No spreadsheet opened. Call open_spreadsheet() first.")
            return False

        try:
            display_loading_message(
                "Saving analysis results to Google Sheets...")

            # Try to get existing worksheet, create if doesn't exist
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=100,
                    cols=10
                )
                # Add headers if new worksheet
                worksheet.append_row([
                    'Timestamp', 'Analysis Type', 'Total Respondents',
                    'Key Finding', 'Details'
                ])

            # Prepare data for insertion
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create row data
            row_data = [
                timestamp,
                analysis_data.get('analysis_type', 'General'),
                analysis_data.get('total_respondents', 0),
                analysis_data.get('key_finding', ''),
                str(analysis_data.get('details', {}))
            ]

            # Append the row to the worksheet
            worksheet.append_row(row_data)

            display_success_message("Analysis results saved successfully!")
            return True

        except Exception as e:
            display_error_message(f"Error saving results: {str(e)}")
            return False

    def log_user_session(self, username, action, worksheet_name='session_log'):
        """
        Log user session activity to Google Sheets.

        Args:
            username (str): Name of the user
            action (str): Action performed
            worksheet_name (str): Name of the worksheet for logging

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.spreadsheet:
            return False

        try:
            # Try to get existing worksheet, create if doesn't exist
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=5
                )
                # Add headers
                worksheet.append_row(
                    ['Timestamp', 'Username', 'Action', 'Status'])

            # Log the session
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            worksheet.append_row([timestamp, username, action, 'Success'])

            return True

        except Exception as e:
            # Silent fail for logging - don't interrupt user experience
            return False

    def export_dataframe_to_sheets(self, df, worksheet_name='exported_data'):
        """
        Export a pandas DataFrame to Google Sheets.

        Args:
            df (pd.DataFrame): DataFrame to export
            worksheet_name (str): Name of the worksheet

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.spreadsheet:
            display_error_message("No spreadsheet opened.")
            return False

        try:
            display_loading_message(
                f"Exporting data to worksheet: {worksheet_name}...")

            # Try to get existing worksheet, create if doesn't exist
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
                worksheet.clear()  # Clear existing data
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=len(df) + 10,
                    cols=len(df.columns) + 2
                )

            # Convert DataFrame to list of lists
            data = [df.columns.tolist()] + df.values.tolist()

            # Update worksheet
            worksheet.update('A1', data)

            display_success_message(
                f"Data exported to '{worksheet_name}' successfully!")
            return True

        except Exception as e:
            display_error_message(f"Error exporting data: {str(e)}")
            return False

    def get_spreadsheet_info(self):
        """
        Get information about the current spreadsheet.

        Returns:
            dict: Spreadsheet information
        """
        if not self.spreadsheet:
            return {"error": "No spreadsheet opened"}

        try:
            info = {
                "title": self.spreadsheet.title,
                "url": self.spreadsheet.url,
                "id": self.spreadsheet.id,
                "worksheets": len(
                    self.spreadsheet.worksheets()),
                "worksheet_names": [
                    ws.title for ws in self.spreadsheet.worksheets()]}
            return info
        except Exception as e:
            return {"error": str(e)}

    def get_worksheet_list(self):
        """
        Get list of all worksheets in the current spreadsheet.

        Returns:
            list: List of worksheet names, or empty list if error
        """
        if not self.spreadsheet:
            return []

        try:
            worksheets = self.spreadsheet.worksheets()
            return [ws.title for ws in worksheets]
        except Exception as e:
            display_error_message(f"Error getting worksheet list: {str(e)}")
            return []

    def create_sample_spreadsheet(
            self, spreadsheet_name='PersonalFinanceData'):
        """
        Create a new spreadsheet with sample data structure.

        Args:
            spreadsheet_name (str): Name for the new spreadsheet

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            display_error_message("Not connected. Call connect() first.")
            return False

        try:
            display_loading_message("Creating sample spreadsheet...")

            # Create new spreadsheet
            spreadsheet = self.client.create(spreadsheet_name)

            # Get the default worksheet
            worksheet = spreadsheet.sheet1
            worksheet.update_title('survey_data')

            # Add headers
            headers = [
                'respondent_id', 'age', 'annual_income',
                'monthly_savings', 'uses_mobile_banking', 'owns_crypto',
                'primary_investment', 'monthly_spending_food',
                'monthly_spending_transport',
                'monthly_spending_entertainment',
                'financial_literacy_score', 'emergency_fund_months'
            ]

            worksheet.append_row(headers)

            # Add sample data rows
            sample_data = [
                [1, 25, 45000, 800, 'yes', 'yes', 'stocks',
                 600, 200, 300, 7, 3],
                [2, 32, 65000, 1200, 'yes', 'no', 'bonds',
                 900, 350, 400, 8, 6],
                [3, 28, 52000, 750, 'no', 'yes', 'crypto',
                 700, 180, 250, 6, 2]
            ]

            for row in sample_data:
                worksheet.append_row(row)

            display_success_message(
                f"Spreadsheet '{spreadsheet_name}' created successfully!")
            print(f"\n📊 Spreadsheet URL: {spreadsheet.url}")
            print(
                "⚠️  IMPORTANT: Share this spreadsheet with your "
                "service account email!"
            )
            print(
                "   (Check your creds.json for the 'client_email' field)"
            )

            return True

        except Exception as e:
            display_error_message(f"Error creating spreadsheet: {str(e)}")
            return False

    def close_connection(self):
        """Close the connection and cleanup."""
        self.client = None
        self.spreadsheet = None
        self.connected = False
        display_success_message("Google Sheets connection closed")