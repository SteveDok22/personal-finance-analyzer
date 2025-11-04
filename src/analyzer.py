"""
Finance Analyzer Module for Personal Finance Survey Analyzer.

This module contains core analysis functions for examining personal
finance survey data including spending patterns, savings behavior,
and investment preferences.
"""

import pandas as pd
import numpy as np
from src.utils import format_currency, format_percentage, safe_divide


class FinanceAnalyzer:
    """Core analysis class for personal finance survey data."""

    def __init__(self, data):
        """
        Initialize the analyzer with survey data.

        Args:
            data (pd.DataFrame): Survey data to analyze
        """
        self.data = data.copy() if data is not None else pd.DataFrame()

    def get_spending_analysis(self):
        """
        Analyze spending patterns across different categories.

        Returns:
            dict: Comprehensive spending analysis
        """
        if self.data.empty:
            return {"error": "No data available"}

        # Find spending columns (any column with 'spending' in the name)
        spending_cols = [
            col for col in self.data.columns if 'spending' in col.lower()
        ]

        if not spending_cols:
            return {"error": "No spending data found"}

        # Create empty analysis dictionary
        analysis = {
            "Spending Overview": {},
            "Category Breakdown": {},
            "Insights": []
        }

        # Calculate total spending per person
        self.data['total_spending'] = self.data[spending_cols].sum(axis=1)

        # Overall spending statistics
        analysis["Spending Overview"] = {
            "Average Total Spending": format_currency(
                self.data['total_spending'].mean()
            ),
            "Median Total Spending": format_currency(
                self.data['total_spending'].median()
            ),
            "Spending Range": (
                f"{format_currency(self.data['total_spending'].min())} - "
                f"{format_currency(self.data['total_spending'].max())}"
            )
        }

        # Category breakdown
        for col in spending_cols:
            category_name = col.replace(
                'monthly_spending_', ''
            ).replace('_', ' ').title()
            analysis["Category Breakdown"][category_name] = {
                "Average": format_currency(self.data[col].mean()),
                "Percentage of Total": format_percentage(
                    self.data[col].sum() / self.data['total_spending'].sum()
                )
            }

        # Generate insights
        if spending_cols:
            # Find highest spending category
            category_totals = {
                col.replace('monthly_spending_', '').title():
                self.data[col].sum()
                for col in spending_cols
            }
            highest_category = max(
                category_totals, key=category_totals.get
            )
            analysis["Insights"].append(
                f"Highest spending category: {highest_category}"
            )

            # Spending vs income ratio
            if 'annual_income' in self.data.columns:
                monthly_income = self.data['annual_income'] / 12
                spending_ratio = (
                    self.data['total_spending'] / monthly_income
                ).mean()
                analysis["Insights"].append(
                    f"Average spending-to-income ratio: "
                    f"{format_percentage(spending_ratio)}"
                )

        return analysis

    def get_savings_analysis(self):
        """
        Analyze savings behavior and patterns.

        Returns:
            dict: Comprehensive savings analysis
        """
        if (self.data.empty or
                'monthly_savings' not in self.data.columns):
            return {"error": "No savings data available"}

        analysis = {
            "Savings Overview": {},
            "Savings Rate Analysis": {},
            "Insights": []
        }

        # Basic savings statistics
        analysis["Savings Overview"] = {
            "Average Monthly Savings": format_currency(
                self.data['monthly_savings'].mean()
            ),
            "Median Monthly Savings": format_currency(
                self.data['monthly_savings'].median()
            ),
            "Savings Range": (
                f"{format_currency(self.data['monthly_savings'].min())} - "
                f"{format_currency(self.data['monthly_savings'].max())}"
            )
        }

        # Savings rate analysis (if income data available)
        if 'annual_income' in self.data.columns:
            monthly_income = self.data['annual_income'] / 12
            self.data['savings_rate'] = (
                self.data['monthly_savings'] / monthly_income
            )

            analysis["Savings Rate Analysis"] = {
                "Average Savings Rate": format_percentage(
                    self.data['savings_rate'].mean()
                ),
                "Median Savings Rate": format_percentage(
                    self.data['savings_rate'].median()
                ),
                "High Savers (>20%)": (
                    f"{len(self.data[self.data['savings_rate'] > 0.2])} "
                    f"respondents"
                ),
                "Low Savers (<10%)": (
                    f"{len(self.data[self.data['savings_rate'] < 0.1])} "
                    f"respondents"
                )
            }

            # Generate insight
            high_savers_pct = (
                len(self.data[self.data['savings_rate'] > 0.2]) /
                len(self.data)
            )
            analysis["Insights"].append(
                f"{format_percentage(high_savers_pct)} of respondents "
                f"save more than 20% of their income"
            )

        return analysis

    def get_investment_analysis(self):
        """
        Analyze investment preferences and cryptocurrency adoption.

        Returns:
            dict: Investment and crypto analysis
        """
        if self.data.empty:
            return {"error": "No data available"}

        analysis = {
            "Investment Preferences": {},
            "Cryptocurrency Analysis": {},
            "Insights": []
        }

        # Investment preferences
        if 'primary_investment' in self.data.columns:
            investment_counts = self.data['primary_investment'].value_counts()
            total_investors = len(
                self.data[self.data['primary_investment'] != 'none']
            )

            analysis["Investment Preferences"]["Distribution"] = {
                inv_type.title(): (
                    f"{count} respondents "
                    f"({format_percentage(count / len(self.data))})"
                )
                for inv_type, count in investment_counts.items()
            }

            analysis["Investment Preferences"]["Summary"] = {
                "Total Active Investors": (
                    f"{total_investors} out of {len(self.data)} respondents"
                ),
                "Investment Rate": format_percentage(
                    total_investors / len(self.data)
                )
            }

        # Cryptocurrency analysis - THIS IS KEY FOR FINTECH!
        if 'owns_crypto' in self.data.columns:
            crypto_owners = self.data['owns_crypto'].sum()
            crypto_rate = crypto_owners / len(self.data)

            analysis["Cryptocurrency Analysis"] = {
                "Total Crypto Owners": (
                    f"{crypto_owners} out of {len(self.data)} respondents"
                ),
                "Crypto Adoption Rate": format_percentage(crypto_rate),
                "Non-Crypto Users": (
                    f"{len(self.data) - crypto_owners} respondents"
                )
            }

            # Generate insight
            if crypto_rate > 0.5:
                analysis["Insights"].append(
                    "Majority of respondents own cryptocurrency"
                )
            elif crypto_rate > 0.3:
                analysis["Insights"].append(
                    "Significant cryptocurrency adoption among respondents"
                )
            else:
                analysis["Insights"].append(
                    "Limited cryptocurrency adoption among respondents"
                )

        return analysis

    def get_fintech_adoption_analysis(self):
        """
        Analyze fintech service adoption patterns.

        Returns:
            dict: Fintech adoption analysis
        """
        if self.data.empty:
            return {"error": "No data available"}

        analysis = {
            "Mobile Banking": {},
            "Digital Adoption Patterns": {},
            "Insights": []
        }

        # Mobile banking analysis
        if 'uses_mobile_banking' in self.data.columns:
            mobile_users = self.data['uses_mobile_banking'].sum()
            adoption_rate = mobile_users / len(self.data)

            analysis["Mobile Banking"] = {
                "Total Users": (
                    f"{mobile_users} out of {len(self.data)} respondents"
                ),
                "Adoption Rate": format_percentage(adoption_rate),
                "Non-Users": (
                    f"{len(self.data) - mobile_users} respondents"
                )
            }

            # Generate insight
            if adoption_rate > 0.8:
                analysis["Insights"].append(
                    "Very high mobile banking adoption"
                )
            elif adoption_rate > 0.6:
                analysis["Insights"].append(
                    "Good mobile banking adoption rate"
                )
            else:
                analysis["Insights"].append(
                    "Room for improvement in mobile banking adoption"
                )

        # Combined digital adoption (mobile banking + crypto)
        if ('uses_mobile_banking' in self.data.columns and
                'owns_crypto' in self.data.columns):
            tech_enthusiasts = self.data[
                (self.data['uses_mobile_banking']) &
                (self.data['owns_crypto'])
            ]

            # Calculate percentage
            enthusiast_count = len(tech_enthusiasts)
            enthusiast_pct = format_percentage(
                enthusiast_count / len(self.data)
            )

            analysis["Digital Adoption Patterns"] = {
                "Tech Enthusiasts (Both)": (
                    f"{enthusiast_count} respondents ({enthusiast_pct})"
                )
            }

        return analysis

    def get_financial_literacy_analysis(self):
        """
        Analyze financial literacy scores and correlations.

        Returns:
            dict: Financial literacy analysis
        """
        if (self.data.empty or
                'financial_literacy_score' not in self.data.columns):
            return {"error": "No financial literacy data available"}

        analysis = {
            "Literacy Overview": {},
            "Score Distribution": {},
            "Correlations": {},
            "Insights": []
        }

        # Basic literacy statistics
        analysis["Literacy Overview"] = {
            "Average Score": (
                f"{self.data['financial_literacy_score'].mean():.1f}/10"
            ),
            "Median Score": (
                f"{self.data['financial_literacy_score'].median():.1f}/10"
            ),
            "Score Range": (
                f"{self.data['financial_literacy_score'].min():.0f} - "
                f"{self.data['financial_literacy_score'].max():.0f}"
            )
        }

        # Score distribution - categorize people
        high_literacy = len(
            self.data[self.data['financial_literacy_score'] >= 8]
        )
        medium_literacy = len(self.data[
            (self.data['financial_literacy_score'] >= 6) &
            (self.data['financial_literacy_score'] < 8)
        ])
        low_literacy = len(
            self.data[self.data['financial_literacy_score'] < 6]
        )

        analysis["Score Distribution"] = {
            "High Literacy (8-10)": (
                f"{high_literacy} respondents "
                f"({format_percentage(high_literacy / len(self.data))})"
            ),
            "Medium Literacy (6-7)": (
                f"{medium_literacy} respondents "
                f"({format_percentage(medium_literacy / len(self.data))})"
            ),
            "Low Literacy (<6)": (
                f"{low_literacy} respondents "
                f"({format_percentage(low_literacy / len(self.data))})"
            )
        }

        # Correlations with other factors
        correlations = {}

        if 'annual_income' in self.data.columns:
            correlation = self.data['financial_literacy_score'].corr(
                self.data['annual_income']
            )
            correlations["Income"] = (
                f"{correlation:.3f} "
                f"{'(positive)' if correlation > 0 else '(negative)'}"
            )

        if 'monthly_savings' in self.data.columns:
            correlation = self.data['financial_literacy_score'].corr(
                self.data['monthly_savings']
            )
            correlations["Savings"] = (
                f"{correlation:.3f} "
                f"{'(positive)' if correlation > 0 else '(negative)'}"
            )

        if 'emergency_fund_months' in self.data.columns:
            correlation = self.data['financial_literacy_score'].corr(
                self.data['emergency_fund_months']
            )
            correlations["Emergency Fund"] = (
                f"{correlation:.3f} "
                f"{'(positive)' if correlation > 0 else '(negative)'}"
            )

        analysis["Correlations"] = correlations

        # Generate insights
        avg_score = self.data['financial_literacy_score'].mean()
        if avg_score >= 8:
            analysis["Insights"].append(
                "High overall financial literacy among respondents"
            )
        elif avg_score >= 6:
            analysis["Insights"].append(
                "Moderate financial literacy levels"
            )
        else:
            analysis["Insights"].append(
                "Financial education opportunities exist"
            )

        return analysis

    def get_comprehensive_report(self):
        """
        Generate a comprehensive analysis report combining all analyses.

        Returns:
            dict: Complete analysis report
        """
        report = {
            "Executive Summary": {},
            "Key Findings": [],
            "Detailed Analysis": {}
        }

        # Generate all individual analyses
        spending_analysis = self.get_spending_analysis()
        savings_analysis = self.get_savings_analysis()
        investment_analysis = self.get_investment_analysis()
        fintech_analysis = self.get_fintech_adoption_analysis()
        literacy_analysis = self.get_financial_literacy_analysis()

        # Executive summary - the big picture
        if not self.data.empty:
            report["Executive Summary"] = {
                "Total Respondents": len(self.data),
                "Average Age": (
                    f"{self.data['age'].mean():.1f} years"
                    if 'age' in self.data.columns else "N/A"
                ),
                "Average Income": (
                    format_currency(self.data['annual_income'].mean())
                    if 'annual_income' in self.data.columns else "N/A"
                ),
                "Average Monthly Savings": (
                    format_currency(self.data['monthly_savings'].mean())
                    if 'monthly_savings' in self.data.columns else "N/A"
                )
            }

        # Collect key findings from all analyses
        for analysis in [spending_analysis, savings_analysis,
                         investment_analysis, fintech_analysis,
                         literacy_analysis]:
            if 'Insights' in analysis:
                report["Key Findings"].extend(analysis["Insights"])

        # Add detailed analyses
        report["Detailed Analysis"] = {
            "Spending Patterns": spending_analysis,
            "Savings Behavior": savings_analysis,
            "Investment Preferences": investment_analysis,
            "Fintech Adoption": fintech_analysis,
            "Financial Literacy": literacy_analysis
        }

        return report