"""
Personal Finance Survey Analyzer
A command-line application for analyzing personal finance survey data.

This application provides insights into spending patterns, savings behavior,
investment preferences, and fintech adoption among survey respondents.
"""

import os
import sys
from src.data_handler import DataHandler
from src.analyzer import FinanceAnalyzer
from src.visualizer import DataVisualizer
from src.google_sheets_handler import GoogleSheetsHandler
from src.utils import clear_screen, validate_choice


class PersonalFinanceAnalyzer:
    """Main application class for the Personal Finance Survey Analyzer."""
    
    def __init__(self):
        """Initialize the application components."""
        self.data_handler = None
        self.analyzer = None
        self.visualizer = None
        self.sheets_handler = None
        self.data_loaded = False
        self.sheets_connected = False
        self.username = ""
        
    def display_welcome(self):
        """Display welcome message and application information."""
        clear_screen()
        print("=" * 60)
        print("    PERSONAL FINANCE SURVEY ANALYZER")
        print("=" * 60)
        print("\nWelcome to the Personal Finance Survey Analyzer!")
        print("This tool helps you analyze personal finance survey data")
        print("to gain insights into spending patterns, savings behavior,")
        print("and fintech adoption trends.\n")
        
        # Get username
        self.username = input("Please enter your name: ").strip()
        if not self.username:
            self.username = "Guest"
        print(f"\nWelcome, {self.username}!")
        input("\nPress Enter to continue...")
        
    def display_menu(self):
        """Display the main menu options."""
        print("\n" + "=" * 50)
        print("           MAIN MENU")
        print("=" * 50)
        print("📂 DATA SOURCES:")
        print("1. Load Local CSV Data")
        print("2. Connect to Google Sheets")
        print("3. Load Data from Google Sheets")
        print("\n📊 ANALYSIS:")
        print("4. View Data Summary")
        print("5. Analyze Spending Patterns")
        print("6. Compare Income vs Savings")
        print("7. Cryptocurrency & Investment Analysis")
        print("8. Financial Literacy Insights")
        print("9. Generate Complete Report")
        print("\n💾 EXPORT:")
        print("10. Export Analysis Results")
        print("11. Save Results to Google Sheets")
        print("\n🔧 OPTIONS:")
        print("12. View Google Sheets Info")
        print("13. Exit Application")
        print("=" * 50)
        
    def handle_menu_choice(self, choice):
        """Handle user menu selection."""
        actions = {
            '1': self.load_local_data,
            '2': self.connect_google_sheets,
            '3': self.load_google_sheets_data,
            '4': self.view_data_summary,
            '5': self.analyze_spending_patterns,
            '6': self.compare_income_savings,
            '7': self.analyze_crypto_investments,
            '8': self.analyze_financial_literacy,
            '9': self.generate_complete_report,
            '10': self.export_results,
            '11': self.save_to_google_sheets,
            '12': self.view_sheets_info,
            '13': lambda: False
        }
        
        action = actions.get(choice)
        if action:
            return action() if choice != '13' else False
        else:
            print("\n❌ Invalid choice. Please select a number from 1-13.")
            input("Press Enter to continue...")
            return True
        
    def load_local_data(self):
        """Load survey data from local CSV file."""
        print("\n" + "-" * 50)
        print("LOADING LOCAL CSV DATA")
        print("-" * 50)
        
        try:
            self.data_handler = DataHandler()
            success = self.data_handler.load_csv('data/sample_survey.csv')
            
            if success:
                self.analyzer = FinanceAnalyzer(self.data_handler.data)
                self.visualizer = DataVisualizer(self.data_handler.data)
                self.data_loaded = True
                print("✅ Data loaded successfully!")
                print(f"📊 Dataset contains {len(self.data_handler.data)} responses")
                
                # Log session if connected to Google Sheets
                if self.sheets_connected and self.sheets_handler:
                    self.sheets_handler.log_user_session(
                        self.username, 
                        "Loaded local CSV data"
                    )
            else:
                print("❌ Failed to load data. Please check the file path.")
                
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            
        input("\nPress Enter to continue...")
        return True
    
    def connect_google_sheets(self):
        """Connect to Google Sheets API."""
        print("\n" + "-" * 50)
        print("CONNECTING TO GOOGLE SHEETS")
        print("-" * 50)
        
        try:
            self.sheets_handler = GoogleSheetsHandler()
            success = self.sheets_handler.connect()
            
            if success:
                self.sheets_connected = True
                print("\n📝 Next step: Use option 3 to load data from a spreadsheet")
                self.sheets_handler.log_user_session(
                    self.username, 
                    "Connected to Google Sheets"
                )
            else:
                print("\n❌ Connection failed. Please check:")
                print("  1. creds.json file exists in project root")
                print("  2. Service account has necessary permissions")
                print("  3. Google Sheets API is enabled")
                print("\n💡 TIP: The app works perfectly without Google Sheets!")
                print("   Use Option 1 to load local CSV data instead.")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
        input("\nPress Enter to continue...")
        return True
    
    def load_google_sheets_data(self):
        """Load data from Google Sheets."""
        if not self.sheets_connected:
            print("\n❌ Please connect to Google Sheets first (Option 2)")
            print("💡 Or use Option 1 to load local CSV data")
            input("Press Enter to continue...")
            return True
        
        print("\n" + "-" * 50)
        print("LOADING DATA FROM GOOGLE SHEETS")
        print("-" * 50)
        
        try:
            spreadsheet_name = input("\nEnter spreadsheet name: ").strip()
            if not spreadsheet_name:
                print("❌ Spreadsheet name cannot be empty")
                input("Press Enter to continue...")
                return True
            
            if self.sheets_handler.open_spreadsheet(spreadsheet_name):
                worksheet_name = input("Enter worksheet name (default: survey_data): ").strip()
                if not worksheet_name:
                    worksheet_name = 'survey_data'
                
                data = self.sheets_handler.load_survey_data(worksheet_name)
                
                if data is not None:
                    self.data_handler = DataHandler()
                    self.data_handler.data = data
                    self.data_handler.original_data = data.copy()
                    self.analyzer = FinanceAnalyzer(data)
                    self.visualizer = DataVisualizer(data)
                    self.data_loaded = True
                    
                    print(f"\n✅ Loaded {len(data)} records from Google Sheets!")
                    
                    # Log session
                    self.sheets_handler.log_user_session(
                        self.username, 
                        f"Loaded data from {spreadsheet_name}/{worksheet_name}"
                    )
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
        input("\nPress Enter to continue...")
        return True