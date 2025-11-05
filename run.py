"""
Personal Finance Survey Analyzer
A command-line application with ASCII art visualization
ADAPTED FOR CODE INSTITUTE TEMPLATE - HEROKU DEPLOYMENT
"""

import os
import sys

# Import matplotlib first and set backend before other imports
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for Heroku
import matplotlib.pyplot as plt  # noqa: E402

from src.data_handler import DataHandler  # noqa: E402
from src.analyzer import FinanceAnalyzer  # noqa: E402
from src.visualizer import DataVisualizer  # noqa: E402
from src.google_sheets_handler import GoogleSheetsHandler  # noqa: E402
from src.utils import validate_choice  # noqa: E402


class ASCIIVisualizer:
    """Helper class for creating ASCII art visualizations."""

    @staticmethod
    def create_bar_chart(title, data_dict, max_width=40,
                         show_values=True, currency=True):
        """
        Create horizontal ASCII bar chart.

        Args:
            title (str): Chart title
            data_dict (dict): label: value pairs
            max_width (int): Maximum bar width
            show_values (bool): Show values at end of bars
            currency (bool): Format as currency
        """
        print(f"\n📊 {title}")
        print("-" * 70)

        if not data_dict:
            print("  No data to display")
            return

        # Sort by value (descending)
        sorted_items = sorted(
            data_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Find max value for scaling
        max_value = max(data_dict.values()) if data_dict else 1

        # Display bars
        for label, value in sorted_items:
            # Calculate bar length
            if max_value > 0:
                bar_length = int((value / max_value) * max_width)
            else:
                bar_length = 0

            # Create bar
            bar = "█" * bar_length

            # Format value
            if show_values:
                if currency:
                    value_str = f"${value:,.0f}"
                elif value < 1:
                    value_str = f"{value:.1%}"
                else:
                    value_str = f"{value:.1f}"
            else:
                value_str = ""

            # Print row (truncate label if too long)
            label_display = label[:18] if len(label) > 18 else label
            print(f"  {label_display:18} {bar:42} {value_str}")

        print("-" * 70)

    @staticmethod
    def create_pie_chart(title, data_dict):
        """
        Create ASCII pie chart representation.

        Args:
            title (str): Chart title
            data_dict (dict): label: value pairs
        """
        print(f"\n🥧 {title}")
        print("-" * 70)

        if not data_dict:
            print("  No data to display")
            return

        total = sum(data_dict.values())

        if total == 0:
            print("  No data to display")
            return

        # Sort by value (descending)
        sorted_items = sorted(
            data_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Calculate percentages and create visual
        print("  ┌" + "─" * 48 + "┐")

        for label, value in sorted_items:
            percentage = (value / total) * 100

            # Create visual bar (proportional to percentage)
            bar_length = int((percentage / 100) * 30)
            bar = "●" * bar_length

            # Format label and percentage
            label_display = label[:15] if len(label) > 15 else label
            pct_display = f"{percentage:5.1f}%"

            print(f"  │ {label_display:15} {bar:30} {pct_display} │")

        print("  └" + "─" * 48 + "┘")
        print("-" * 70)

    @staticmethod
    def create_distribution_chart(title, values, bins=10):
        """
        Create ASCII histogram/distribution chart.

        Args:
            title (str): Chart title
            values (list): List of numeric values
            bins (int): Number of bins
        """
        print(f"\n📈 {title}")
        print("-" * 70)

        if not values or len(values) == 0:
            print("  No data to display")
            return

        # Calculate histogram bins
        min_val = min(values)
        max_val = max(values)

        if min_val == max_val:
            print(f"  All values are {min_val:.1f}")
            return

        bin_width = (max_val - min_val) / bins

        # Count values in each bin
        bin_counts = [0] * bins
        for value in values:
            bin_idx = min(int((value - min_val) / bin_width), bins - 1)
            bin_counts[bin_idx] += 1

        # Find max count for scaling
        max_count = max(bin_counts) if bin_counts else 1

        # Display histogram
        for i, count in enumerate(bin_counts):
            bin_start = min_val + (i * bin_width)
            bin_end = bin_start + bin_width

            # Create bar
            bar_length = int((count / max_count) * 40)
            bar = "▓" * bar_length

            # Format range
            range_str = f"[{bin_start:6.0f}-{bin_end:6.0f})"

            print(f"  {range_str:20} {bar:40} ({count:3d})")

        print("-" * 70)
        avg_val = sum(values) / len(values)
        print(f"  Min: ${min_val:,.0f} | Max: ${max_val:,.0f} | "
              f"Avg: ${avg_val:,.0f}")
        print("-" * 70)

    @staticmethod
    def create_comparison_bars(title, data_pairs):
        """
        Create side-by-side comparison bars.

        Args:
            title (str): Chart title
            data_pairs (list): [(label1, val1, label2, val2), ...]
        """
        print(f"\n⚖️  {title}")
        print("-" * 70)

        if not data_pairs:
            print("  No data to display")
            return

        for item in data_pairs:
            if len(item) >= 4:
                label1, val1, label2, val2 = item[:4]

                # Calculate relative sizes
                max_val = max(val1, val2)
                if max_val > 0:
                    bar1_len = int((val1 / max_val) * 20)
                    bar2_len = int((val2 / max_val) * 20)
                else:
                    bar1_len = 0
                    bar2_len = 0

                bar1 = "█" * bar1_len
                bar2 = "█" * bar2_len

                print(f"\n  {label1:12} {bar1:20} ${val1:8,.0f}")
                print(f"  {label2:12} {bar2:20} ${val2:8,.0f}")
                print("  " + "─" * 45)


class PersonalFinanceAnalyzer:
    """Main application class with ASCII visualization."""

    def __init__(self):
        """Initialize the application components."""
        self.data_handler = None
        self.analyzer = None
        self.visualizer = None
        self.sheets_handler = None
        self.ascii_viz = ASCIIVisualizer()
        self.data_loaded = False
        self.sheets_connected = False
        self.username = ""

    def display_welcome(self):
        """Display welcome message."""
        print("=" * 70)
        print("    PERSONAL FINANCE SURVEY ANALYZER")
        print("=" * 70)
        print("\nWelcome to the Personal Finance Survey Analyzer!")
        print("This tool provides comprehensive financial analysis")
        print("with beautiful terminal-based visualizations.\n")

        # Get username
        self.username = input("Please enter your name: ").strip()
        if not self.username:
            self.username = "Guest"
        print(f"\nWelcome, {self.username}!")
        input("\nPress Enter to continue...")

    def display_menu(self):
        """Display the main menu options."""
        print("\n" + "=" * 70)
        print("           MAIN MENU")
        print("=" * 70)
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
        print("=" * 70)

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
            print("\n❌ Invalid choice. Please select 1-13.")
            input("Press Enter to continue...")
            return True

    def load_local_data(self):
        """Load survey data from local CSV file."""
        print("\n" + "-" * 70)
        print("LOADING LOCAL CSV DATA")
        print("-" * 70)

        try:
            # Get absolute path to data file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, 'data', 'sample_survey.csv')

            self.data_handler = DataHandler()
            success = self.data_handler.load_csv(file_path)

            if success:
                self.analyzer = FinanceAnalyzer(self.data_handler.data)
                self.visualizer = DataVisualizer(self.data_handler.data)
                self.data_loaded = True
                print("✅ Data loaded successfully!")
                record_count = len(self.data_handler.data)
                print(f"📊 Dataset contains {record_count} responses")

                # Log session if connected
                if self.sheets_connected and self.sheets_handler:
                    self.sheets_handler.log_user_session(
                        self.username,
                        "Loaded local CSV data"
                    )
            else:
                print("❌ Failed to load data.")

        except (IOError, OSError) as e:
            print(f"❌ Error loading data: {str(e)}")

        input("\nPress Enter to continue...")
        return True

    def connect_google_sheets(self):
        """Connect to Google Sheets API."""
        print("\n" + "-" * 70)
        print("CONNECTING TO GOOGLE SHEETS")
        print("-" * 70)

        try:
            self.sheets_handler = GoogleSheetsHandler()
            success = self.sheets_handler.connect()

            if success:
                self.sheets_connected = True
                print("\n✅ Successfully connected to Google Sheets!")
                self.sheets_handler.log_user_session(
                    self.username,
                    "Connected to Google Sheets"
                )
            else:
                print("\n❌ Connection failed.")
                print("💡 TIP: The app works perfectly without "
                      "Google Sheets!")

        except (IOError, OSError) as e:
            print(f"❌ Error: {str(e)}")

        input("\nPress Enter to continue...")
        return True

    def load_google_sheets_data(self):
        """Load data from Google Sheets."""
        if not self.sheets_connected:
            print("\n❌ Please connect to Google Sheets first (Option 2)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 70)
        print("LOADING DATA FROM GOOGLE SHEETS")
        print("-" * 70)

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

                    print(f"\n✅ Loaded {len(data)} records!")

                    self.sheets_handler.log_user_session(
                        self.username,
                        f"Loaded data from {spreadsheet_name}"
                    )

        except (IOError, OSError) as e:
            print(f"❌ Error: {str(e)}")

        input("\nPress Enter to continue...")
        return True

    def view_data_summary(self):
        """Display basic data summary with ASCII visualization."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 70)
        print("DATA SUMMARY")
        print("-" * 70)

        summary = self.data_handler.get_data_summary()

        for section, data in summary.items():
            print(f"\n{section}:")
            for key, value in data.items():
                print(f"  {key}: {value}")

        # ASCII visualization of key metrics
        if 'Technology Adoption' in summary:
            tech_data = {}
            for key, value in summary['Technology Adoption'].items():
                # Extract percentage
                pct_str = value.replace('%', '')
                try:
                    tech_data[key] = float(pct_str) / 100
                except (ValueError, TypeError):
                    pass

            if tech_data:
                self.ascii_viz.create_bar_chart(
                    "Technology Adoption Rates",
                    tech_data,
                    currency=False,
                    show_values=True
                )

        input("\nPress Enter to continue...")
        return True

    def analyze_spending_patterns(self):
        """Analyze spending patterns with ASCII visualization."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 70)
        print("SPENDING PATTERNS ANALYSIS")
        print("-" * 70)

        analysis = self.analyzer.get_spending_analysis()

        # Display overview
        if "Spending Overview" in analysis:
            print("\n📊 Spending Overview:")
            for key, value in analysis["Spending Overview"].items():
                print(f"  {key}: {value}")

        # ASCII BAR CHART - Average Spending by Category
        if "Category Breakdown" in analysis:
            chart_data = {}
            for category, data in analysis["Category Breakdown"].items():
                # Parse average value
                avg_str = data["Average"].replace('$', '').replace(',', '')
                try:
                    chart_data[category] = float(avg_str)
                except (ValueError, TypeError):
                    pass

            if chart_data:
                self.ascii_viz.create_bar_chart(
                    "Average Monthly Spending by Category",
                    chart_data,
                    currency=True
                )

        # ASCII PIE CHART - Spending Distribution
        if "Category Breakdown" in analysis:
            pie_data = {}
            for category, data in analysis["Category Breakdown"].items():
                # Parse percentage
                pct_str = data.get("Percentage of Total", "0%")
                pct_str = pct_str.replace('%', '')
                try:
                    pie_data[category] = float(pct_str)
                except (ValueError, TypeError):
                    pass

            if pie_data:
                self.ascii_viz.create_pie_chart(
                    "Spending Distribution",
                    pie_data
                )

        # Display insights
        if "Insights" in analysis:
            print("\n💡 Key Insights:")
            for insight in analysis["Insights"]:
                print(f"  • {insight}")

        input("\nPress Enter to continue...")
        return True

    def compare_income_savings(self):
        """Compare income vs savings with ASCII visualization."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 70)
        print("INCOME VS SAVINGS ANALYSIS")
        print("-" * 70)

        analysis = self.analyzer.get_savings_analysis()

        # Display savings overview
        if "Savings Overview" in analysis:
            print("\n💰 Savings Overview:")
            for key, value in analysis["Savings Overview"].items():
                print(f"  {key}: {value}")

        # ASCII DISTRIBUTION - Savings amounts
        if 'monthly_savings' in self.data_handler.data.columns:
            savings_values = self.data_handler.data[
                'monthly_savings'
            ].dropna().tolist()

            if savings_values:
                self.ascii_viz.create_distribution_chart(
                    "Monthly Savings Distribution",
                    savings_values,
                    bins=8
                )

        # Display savings rate
        if "Savings Rate Analysis" in analysis:
            print("\n📊 Savings Rate Analysis:")
            for key, value in analysis["Savings Rate Analysis"].items():
                print(f"  {key}: {value}")

        # ASCII BAR CHART - Savings categories
        if "Savings Rate Analysis" in analysis:
            if 'annual_income' in self.data_handler.data.columns:
                data = self.data_handler.data
                rate_data = {
                    "High Savers": len(data[
                        (data['annual_income'] > 0) &
                        ((data['monthly_savings'] * 12 /
                          data['annual_income']) > 0.2)
                    ]),
                    "Medium Savers": len(data[
                        (data['annual_income'] > 0) &
                        ((data['monthly_savings'] * 12 /
                          data['annual_income']) >= 0.1) &
                        ((data['monthly_savings'] * 12 /
                          data['annual_income']) <= 0.2)
                    ]),
                    "Low Savers": len(data[
                        (data['annual_income'] > 0) &
                        ((data['monthly_savings'] * 12 /
                          data['annual_income']) < 0.1)
                    ])
                }

                self.ascii_viz.create_bar_chart(
                    "Savers by Category (>20%, 10-20%, <10%)",
                    rate_data,
                    currency=False
                )

        # Display insights
        if "Insights" in analysis:
            print("\n💡 Key Insights:")
            for insight in analysis["Insights"]:
                print(f"  • {insight}")

        input("\nPress Enter to continue...")
        return True

    def analyze_crypto_investments(self):
        """Analyze cryptocurrency with ASCII visualization."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 70)
        print("CRYPTOCURRENCY & INVESTMENT ANALYSIS")
        print("-" * 70)

        analysis = self.analyzer.get_investment_analysis()

        # ASCII PIE CHART - Investment preferences
        if ("Investment Preferences" in analysis and
                "Distribution" in analysis["Investment Preferences"]):

            inv_data = {}
            for inv_type, count_str in analysis[
                    "Investment Preferences"]["Distribution"].items():
                # Extract count from "X respondents (Y%)"
                try:
                    count = int(count_str.split()[0])
                    inv_data[inv_type] = count
                except (ValueError, IndexError):
                    pass

            if inv_data:
                self.ascii_viz.create_pie_chart(
                    "Investment Preferences Distribution",
                    inv_data
                )

        # Display investment preferences text
        if ("Investment Preferences" in analysis and
                "Distribution" in analysis["Investment Preferences"]):
            print("\n📈 Investment Preferences:")
            for inv_type, count in analysis[
                    "Investment Preferences"]["Distribution"].items():
                print(f"  {inv_type}: {count}")

        # ASCII BAR CHART - Crypto ownership
        if 'owns_crypto' in self.data_handler.data.columns:
            crypto_sum = int(self.data_handler.data['owns_crypto'].sum())
            crypto_data = {
                "Owns Crypto": crypto_sum,
                "No Crypto": int(len(self.data_handler.data) - crypto_sum)
            }

            self.ascii_viz.create_bar_chart(
                "Cryptocurrency Ownership",
                crypto_data,
                currency=False
            )

        # Display crypto analysis
        if "Cryptocurrency Analysis" in analysis:
            print("\n🪙 Cryptocurrency Analysis:")
            for key, value in analysis["Cryptocurrency Analysis"].items():
                print(f"  {key}: {value}")

        # Display insights
        if "Insights" in analysis:
            print("\n💡 Key Insights:")
            for insight in analysis["Insights"]:
                print(f"  • {insight}")

        input("\nPress Enter to continue...")
        return True

    def analyze_financial_literacy(self):
        """Analyze financial literacy with ASCII visualization."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 70)
        print("FINANCIAL LITERACY INSIGHTS")
        print("-" * 70)

        analysis = self.analyzer.get_financial_literacy_analysis()

        # Display literacy overview
        if "Literacy Overview" in analysis:
            print("\n🎓 Literacy Overview:")
            for key, value in analysis["Literacy Overview"].items():
                print(f"  {key}: {value}")

        # ASCII DISTRIBUTION - Literacy scores
        if 'financial_literacy_score' in self.data_handler.data.columns:
            literacy_values = self.data_handler.data[
                'financial_literacy_score'
            ].dropna().tolist()

            if literacy_values:
                # Create custom distribution for scores 1-10
                print("\n📊 Financial Literacy Score Distribution")
                print("-" * 70)

                score_counts = {}
                for score in range(1, 11):
                    count = sum(1 for v in literacy_values
                                if int(v) == score)
                    if count > 0:
                        score_counts[f"Score {score}"] = count

                if score_counts:
                    max_count = max(score_counts.values())
                    for label, count in sorted(score_counts.items()):
                        bar_len = int((count / max_count) * 40)
                        bar = "▓" * bar_len
                        print(f"  {label:10} {bar:40} ({count:2d})")
                    print("-" * 70)

        # ASCII PIE CHART - Literacy categories
        if "Score Distribution" in analysis:
            lit_data = {}
            for category, count_str in analysis[
                    "Score Distribution"].items():
                # Extract count
                try:
                    count = int(count_str.split()[0])
                    lit_data[category] = count
                except (ValueError, IndexError):
                    pass

            if lit_data:
                self.ascii_viz.create_pie_chart(
                    "Literacy Level Categories",
                    lit_data
                )

        # Display score distribution text
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

        input("\nPress Enter to continue...")
        return True

    def generate_complete_report(self):
        """Generate complete report with comprehensive ASCII viz."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 70)
        print("GENERATING COMPLETE REPORT")
        print("-" * 70)

        report = self.analyzer.get_comprehensive_report()

        # Display executive summary
        print("\n" + "=" * 70)
        print("EXECUTIVE SUMMARY")
        print("=" * 70)
        for key, value in report["Executive Summary"].items():
            print(f"{key}: {value}")

        # Create comprehensive ASCII dashboard
        print("\n" + "=" * 70)
        print("COMPREHENSIVE DASHBOARD")
        print("=" * 70)

        # 1. Age distribution
        if 'age' in self.data_handler.data.columns:
            age_values = self.data_handler.data['age'].dropna().tolist()
            self.ascii_viz.create_distribution_chart(
                "Age Distribution",
                age_values,
                bins=6
            )

        # 2. Income vs Savings comparison
        if ('annual_income' in self.data_handler.data.columns and
                'monthly_savings' in self.data_handler.data.columns):
            avg_income = self.data_handler.data['annual_income'].mean()
            avg_savings_monthly = self.data_handler.data[
                'monthly_savings'
            ].mean()
            avg_savings_annual = avg_savings_monthly * 12

            comparison_data = [
                ("Annual Income", avg_income,
                 "Annual Savings", avg_savings_annual)
            ]

            self.ascii_viz.create_comparison_bars(
                "Average Income vs Savings (Annual)",
                comparison_data
            )

        # 3. Technology adoption
        if ('uses_mobile_banking' in self.data_handler.data.columns and
                'owns_crypto' in self.data_handler.data.columns):
            mobile_sum = int(self.data_handler.data[
                'uses_mobile_banking'
            ].sum())
            crypto_sum = int(self.data_handler.data['owns_crypto'].sum())
            tech_data = {
                "Mobile Banking": mobile_sum,
                "Crypto": crypto_sum
            }

            self.ascii_viz.create_bar_chart(
                "Technology Adoption",
                tech_data,
                currency=False
            )

        # Display all key findings
        print("\n" + "=" * 70)
        print("KEY FINDINGS")
        print("=" * 70)
        for i, finding in enumerate(report["Key Findings"], 1):
            print(f"{i}. {finding}")

        # Ask if user wants detailed breakdown
        show_detail = input(
            "\n📄 Would you like to see detailed analysis? (yes/no): "
        ).strip().lower()

        if show_detail in ['yes', 'y']:
            for section_name, section_data in report[
                    "Detailed Analysis"].items():
                print("\n" + "-" * 70)
                print(section_name.upper())
                print("-" * 70)
                if (isinstance(section_data, dict) and
                        "Insights" in section_data):
                    for insight in section_data["Insights"]:
                        print(f"  • {insight}")

        input("\nPress Enter to continue...")
        return True

    def export_results(self):
        """Export analysis results to files."""
        if not self.data_loaded:
            print("\n❌ Please load data first (Option 1 or 3)")
            input("Press Enter to continue...")
            return True

        print("\n" + "-" * 70)
        print("EXPORTING RESULTS")
        print("-" * 70)

        print("\nExport Options:")
        print("1. Export PNG charts (for presentation)")
        print("2. Export cleaned data (CSV)")
        print("3. Export both")

        choice = input("\nSelect export option (1-3): ").strip()

        base_dir = os.path.dirname(os.path.abspath(__file__))

        if choice == '1' or choice == '3':
            print("\n📊 Exporting PNG charts...")
            chart_dir = os.path.join(base_dir, 'exports', 'charts')
            os.makedirs(chart_dir, exist_ok=True)

            try:
                # Export all matplotlib charts
                self.visualizer.export_all_charts(chart_dir)
                print("✅ PNG charts exported to exports/charts/")
            except (IOError, OSError) as e:
                print(f"⚠️  Error exporting charts: {str(e)}")

        if choice == '2' or choice == '3':
            print("\n💾 Exporting cleaned data...")
            data_path = os.path.join(
                base_dir, 'exports', 'data', 'cleaned_data.csv'
            )
            self.data_handler.export_cleaned_data(data_path)

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

        print("\n" + "-" * 70)
        print("SAVING TO GOOGLE SHEETS")
        print("-" * 70)

        print("\nWhat would you like to save?")
        print("1. Analysis summary")
        print("2. Cleaned data")
        print("3. Both")

        choice = input("\nSelect option (1-3): ").strip()

        try:
            if choice == '1' or choice == '3':
                report = self.analyzer.get_comprehensive_report()
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
                print("❌ Invalid choice.")

            self.sheets_handler.log_user_session(
                self.username,
                "Saved results to Google Sheets"
            )

        except (IOError, OSError) as e:
            print(f"❌ Error: {str(e)}")

        input("\nPress Enter to continue...")
        return True

    def view_sheets_info(self):
        """View Google Sheets connection information."""
        print("\n" + "-" * 70)
        print("GOOGLE SHEETS INFORMATION")
        print("-" * 70)

        if not self.sheets_connected:
            print("\n❌ Not connected to Google Sheets")
            print("💡 Use Option 2 to connect")
            print("\nNote: Google Sheets is optional!")
        else:
            info = self.sheets_handler.get_spreadsheet_info()

            if 'error' in info:
                print(f"\n❌ Error: {info['error']}")
            else:
                print(f"\n📊 Spreadsheet: {info.get('title', 'N/A')}")
                print(f"🔗 URL: {info.get('url', 'N/A')}")
                print(f"📑 Total Worksheets: {info.get('worksheets', 0)}")
                print("\n📄 Worksheet Names:")
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
                print("\n❌ Invalid choice. Enter 1-13.")
                input("Press Enter to continue...")
                continue

            continue_app = self.handle_menu_choice(choice)

            if not continue_app:
                print("\n" + "=" * 70)
                print(f"Thank you, {self.username}!")
                print("=" * 70)

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
    except (IOError, OSError) as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()