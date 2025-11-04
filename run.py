"""
Personal Finance Survey Analyzer
A command-line application for analyzing personal finance survey data.

This application provides insights into spending patterns, savings behavior,
investment preferences, and fintech adoption among survey respondents.
"""

import os
import sys
import matplotlib.pyplot as plt
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
                print(
                    f"📊 Dataset contains "
                    f"{len(self.data_handler.data)} responses"
                )

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
                print(
                    "\n📝 Next step: Use option 3 to load data from a "
                    "spreadsheet"
                )
                self.sheets_handler.log_user_session(
                    self.username,
                    "Connected to Google Sheets"
                )
            else:
                print("\n❌ Connection failed. Please check:")
                print("  1. creds.json file exists in project root")
                print("  2. Service account has necessary permissions")
                print("  3. Google Sheets API is enabled")
                print(
                    "\n💡 TIP: The app works perfectly without Google "
                    "Sheets!"
                )
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
                worksheet_name = input(
                    "Enter worksheet name (default: survey_data): "
                ).strip()
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

                    print(
                        f"\n✅ Loaded {len(data)} records from "
                        f"Google Sheets!"
                    )

                    # Log session
                    self.sheets_handler.log_user_session(
                        self.username,
                        f"Loaded data from "
                        f"{spreadsheet_name}/{worksheet_name}"
                    )

        except Exception as e:
            print(f"❌ Error: {str(e)}")

        input("\nPress Enter to continue...")
        return True

    def view_data_summary(self):
        """Display basic data summary."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 50)
        print("DATA SUMMARY")
        print("-" * 50)

        summary = self.data_handler.get_data_summary()

        for section, data in summary.items():
            print(f"\n{section}:")
            for key, value in data.items():
                print(f"  {key}: {value}")

        input("\nPress Enter to continue...")
        return True

    def analyze_spending_patterns(self):
        """Analyze spending patterns across categories."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 50)
        print("SPENDING PATTERNS ANALYSIS")
        print("-" * 50)

        analysis = self.analyzer.get_spending_analysis()

        # Display overview
        if "Spending Overview" in analysis:
            print("\n📊 Spending Overview:")
            for key, value in analysis["Spending Overview"].items():
                print(f"  {key}: {value}")

        # Display insights
        if "Insights" in analysis:
            print("\n💡 Key Insights:")
            for insight in analysis["Insights"]:
                print(f"  • {insight}")

        # Ask if user wants visualization
        show_viz = input(
            "\n📈 Would you like to see spending charts? (yes/no): "
        ).strip().lower()
        if show_viz in ['yes', 'y']:
            print("\n📊 Opening chart window...")
            fig = self.visualizer.create_spending_charts()
            if fig:
                plt.show()
                print("✅ Chart displayed! Close the window to continue.")

        input("\nPress Enter to continue...")
        return True

    def compare_income_savings(self):
        """Compare income vs savings analysis."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 50)
        print("INCOME VS SAVINGS ANALYSIS")
        print("-" * 50)

        analysis = self.analyzer.get_savings_analysis()

        # Display savings overview
        if "Savings Overview" in analysis:
            print("\n💰 Savings Overview:")
            for key, value in analysis["Savings Overview"].items():
                print(f"  {key}: {value}")

        # Display savings rate
        if "Savings Rate Analysis" in analysis:
            print("\n📊 Savings Rate Analysis:")
            for key, value in analysis["Savings Rate Analysis"].items():
                print(f"  {key}: {value}")

        # Display insights
        if "Insights" in analysis:
            print("\n💡 Key Insights:")
            for insight in analysis["Insights"]:
                print(f"  • {insight}")

        # Ask if user wants visualization
        show_viz = input(
            "\n📈 Would you like to see savings charts? (yes/no): "
        ).strip().lower()
        if show_viz in ['yes', 'y']:
            print("\n📊 Opening chart window...")
            fig = self.visualizer.create_savings_charts()
            if fig:
                plt.show()
                print("✅ Chart displayed! Close the window to continue.")

        input("\nPress Enter to continue...")
        return True

    def analyze_crypto_investments(self):
        """Analyze cryptocurrency and investment preferences."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 50)
        print("CRYPTOCURRENCY & INVESTMENT ANALYSIS")
        print("-" * 50)

        analysis = self.analyzer.get_investment_analysis()

        # Display investment preferences
        if ("Investment Preferences" in analysis and
                "Distribution" in analysis["Investment Preferences"]):
            print("\n📈 Investment Preferences:")
            for inv_type, count in analysis[
                    "Investment Preferences"]["Distribution"].items():
                print(f"  {inv_type}: {count}")

        # Display crypto analysis - THE FINTECH FOCUS!
        if "Cryptocurrency Analysis" in analysis:
            print("\n🪙 Cryptocurrency Analysis:")
            for key, value in analysis["Cryptocurrency Analysis"].items():
                print(f"  {key}: {value}")

        # Display insights
        if "Insights" in analysis:
            print("\n💡 Key Insights:")
            for insight in analysis["Insights"]:
                print(f"  • {insight}")

        # Ask if user wants visualization
        show_viz = input(
            "\n📈 Would you like to see investment charts? (yes/no): "
        ).strip().lower()
        if show_viz in ['yes', 'y']:
            print("\n📊 Opening chart window...")
            fig = self.visualizer.create_investment_charts()
            if fig:
                plt.show()
                print("✅ Chart displayed! Close the window to continue.")

        input("\nPress Enter to continue...")
        return True

    def analyze_financial_literacy(self):
        """Analyze financial literacy scores and correlations."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 50)
        print("FINANCIAL LITERACY INSIGHTS")
        print("-" * 50)

        analysis = self.analyzer.get_financial_literacy_analysis()

        # Display literacy overview
        if "Literacy Overview" in analysis:
            print("\n🎓 Literacy Overview:")
            for key, value in analysis["Literacy Overview"].items():
                print(f"  {key}: {value}")

        # Display score distribution
        if "Score Distribution" in analysis:
            print("\n📊 Score Distribution:")
            for key, value in analysis["Score Distribution"].items():
                print(f"  {key}: {value}")

        # Display correlations
        if "Correlations" in analysis:
            print("\n🔗 Correlations with Other Factors:")
            for key, value in analysis["Correlations"].items():
                print(f"  Literacy vs {key}: {value}")

        # Display insights
        if "Insights" in analysis:
            print("\n💡 Key Insights:")
            for insight in analysis["Insights"]:
                print(f"  • {insight}")

        # Ask if user wants visualization
        show_viz = input(
            "\n📈 Would you like to see literacy charts? (yes/no): "
        ).strip().lower()
        if show_viz in ['yes', 'y']:
            print("\n📊 Opening chart window...")
            fig = self.visualizer.create_financial_literacy_charts()
            if fig:
                plt.show()
                print("✅ Chart displayed! Close the window to continue.")

        input("\nPress Enter to continue...")
        return True

    def generate_complete_report(self):
        """Generate a complete analysis report."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 50)
        print("GENERATING COMPLETE REPORT")
        print("-" * 50)

        report = self.analyzer.get_comprehensive_report()

        # Display executive summary
        print("\n" + "=" * 50)
        print("EXECUTIVE SUMMARY")
        print("=" * 50)
        for key, value in report["Executive Summary"].items():
            print(f"{key}: {value}")

        # Display all key findings
        print("\n" + "=" * 50)
        print("KEY FINDINGS")
        print("=" * 50)
        for i, finding in enumerate(report["Key Findings"], 1):
            print(f"{i}. {finding}")

        # Ask if user wants detailed breakdown
        show_detail = input(
            "\n📄 Would you like to see detailed analysis sections? "
            "(yes/no): "
        ).strip().lower()
        if show_detail in ['yes', 'y']:
            for section_name, section_data in report[
                    "Detailed Analysis"].items():
                print("\n" + "-" * 50)
                print(section_name.upper())
                print("-" * 50)
                if (isinstance(section_data, dict) and
                        "Insights" in section_data):
                    for insight in section_data["Insights"]:
                        print(f"  • {insight}")

        # Ask if user wants comprehensive dashboard
        show_dash = input(
            "\n📊 Would you like to see the comprehensive dashboard? "
            "(yes/no): "
        ).strip().lower()
        if show_dash in ['yes', 'y']:
            print("\n📊 Opening dashboard window...")
            fig = self.visualizer.create_comprehensive_dashboard()
            if fig:
                plt.show()
                print("✅ Dashboard displayed! Close the window to continue.")

        input("\nPress Enter to continue...")
        return True

    def export_results(self):
        """Export analysis results to files."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 50)
        print("EXPORTING RESULTS")
        print("-" * 50)

        print("\nExport Options:")
        print("1. Export charts (PNG)")
        print("2. Export cleaned data (CSV)")
        print("3. Export both")

        choice = input("\nSelect export option (1-3): ").strip()

        if choice == '1' or choice == '3':
            print("\n📊 Exporting charts...")
            self.visualizer.export_all_charts()

        if choice == '2' or choice == '3':
            print("\n💾 Exporting cleaned data...")
            self.data_handler.export_cleaned_data(
                'exports/data/cleaned_data.csv'
            )

        if choice not in ['1', '2', '3']:
            print("❌ Invalid choice. Please select 1, 2, or 3.")

        # Log session if connected
        if self.sheets_connected and self.sheets_handler:
            self.sheets_handler.log_user_session(
                self.username,
                "Exported analysis results"
            )

        input("\nPress Enter to continue...")
        return True

    def save_to_google_sheets(self):
        """Save analysis results to Google Sheets."""
        if not self.sheets_connected:
            print("\n❌ Please connect to Google Sheets first (Option 2)")
            print("💡 Or use Option 10 to export locally")
            input("Press Enter to continue...")
            return True

        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 50)
        print("SAVING TO GOOGLE SHEETS")
        print("-" * 50)

        print("\nWhat would you like to save?")
        print("1. Analysis summary")
        print("2. Cleaned data")
        print("3. Both")

        choice = input("\nSelect option (1-3): ").strip()

        try:
            if choice == '1' or choice == '3':
                # Get comprehensive analysis
                report = self.analyzer.get_comprehensive_report()

                # Prepare analysis data
                analysis_data = {
                    'analysis_type': 'Comprehensive Report',
                    'total_respondents': len(self.data_handler.data),
                    'key_finding': ', '.join(
                        report.get('Key Findings', [])[:2]
                    ),
                    'details': report.get('Executive Summary', {})
                }

                self.sheets_handler.save_analysis_results(analysis_data)

            if choice == '2' or choice == '3':
                self.sheets_handler.export_dataframe_to_sheets(
                    self.data_handler.data,
                    'cleaned_survey_data'
                )

            if choice not in ['1', '2', '3']:
                print("❌ Invalid choice. Please select 1, 2, or 3.")

            # Log session
            self.sheets_handler.log_user_session(
                self.username,
                "Saved results to Google Sheets"
            )

        except Exception as e:
            print(f"❌ Error: {str(e)}")

        input("\nPress Enter to continue...")
        return True

    def view_sheets_info(self):
        """View Google Sheets connection information."""
        print("\n" + "-" * 50)
        print("GOOGLE SHEETS INFORMATION")
        print("-" * 50)

        if not self.sheets_connected:
            print("\n❌ Not connected to Google Sheets")
            print("💡 Use Option 2 to connect")
            print("\nNote: Google Sheets is optional!")
            print(
                "The app works perfectly with local CSV files (Option 1)"
            )
        else:
            info = self.sheets_handler.get_spreadsheet_info()

            if 'error' in info:
                print(f"\n❌ Error: {info['error']}")
            else:
                print(f"\n📊 Spreadsheet: {info.get('title', 'N/A')}")
                print(f"🔗 URL: {info.get('url', 'N/A')}")
                print(f"📑 Total Worksheets: {info.get('worksheets', 0)}")
                print(f"\n📄 Worksheet Names:")
                for name in info.get('worksheet_names', []):
                    print(f"  • {name}")

        input("\nPress Enter to continue...")
        return True

    def run(self):
        """Main application loop."""
        self.display_welcome()

        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-13): ").strip()

            if not validate_choice(choice, 1, 13):
                print(
                    "\n❌ Invalid choice. Please enter a number "
                    "between 1 and 13."
                )
                input("Press Enter to continue...")
                continue

            continue_app = self.handle_menu_choice(choice)

            if not continue_app:
                print("\n" + "=" * 60)
                print(
                    f"Thank you for using Personal Finance Survey "
                    f"Analyzer, {self.username}!"
                )
                print("=" * 60)

                # Close Google Sheets connection if active
                if self.sheets_connected and self.sheets_handler:
                    self.sheets_handler.log_user_session(
                        self.username,
                        "Exited application"
                    )
                    self.sheets_handler.close_connection()

                break


def main():
    """Application entry point."""
    try:
        app = PersonalFinanceAnalyzer()
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()