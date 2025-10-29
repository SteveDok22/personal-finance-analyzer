"""
Data Visualizer Module for Personal Finance Survey Analyzer.

This module handles creating charts and visualizations for the analysis results
using matplotlib and seaborn libraries.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from src.utils import create_directory_if_not_exists, display_success_message, display_error_message


class DataVisualizer:
    """Handles data visualization and chart generation."""
    
    def __init__(self, data):
        """
        Initialize the visualizer with survey data.
        
        Args:
            data (pd.DataFrame): Survey data to visualize
        """
        self.data = data.copy() if data is not None else pd.DataFrame()
        self.setup_style()
        
    def setup_style(self):
        """Set up matplotlib and seaborn styling."""
        plt.style.use('default')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
        
    def create_spending_charts(self, save_path=None):
        """
        Create visualizations for spending analysis.
        
        Args:
            save_path (str): Optional path to save charts
            
        Returns:
            bool: True if successful
        """
        if self.data.empty:
            display_error_message("No data available for visualization")
            return False
        
        try:
            # Find spending columns
            spending_cols = [col for col in self.data.columns if 'spending' in col.lower()]
            
            if not spending_cols:
                display_error_message("No spending data found")
                return False
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Personal Finance - Spending Analysis', fontsize=16, fontweight='bold')
            
            # 1. Spending by category (pie chart)
            spending_totals = {
                col.replace('monthly_spending_', '').replace('_', ' ').title(): self.data[col].sum() 
                for col in spending_cols
            }
            
            axes[0, 0].pie(spending_totals.values(), labels=spending_totals.keys(), autopct='%1.1f%%')
            axes[0, 0].set_title('Spending Distribution by Category')
            
            # 2. Average spending by category (bar chart)
            avg_spending = {
                col.replace('monthly_spending_', '').replace('_', ' ').title(): self.data[col].mean() 
                for col in spending_cols
            }
            
            categories = list(avg_spending.keys())
            values = list(avg_spending.values())
            
            bars = axes[0, 1].bar(categories, values, color=sns.color_palette("husl", len(categories)))
            axes[0, 1].set_title('Average Monthly Spending by Category')
            axes[0, 1].set_ylabel('Amount ($)')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.01, 
                               f'${value:.0f}', ha='center', va='bottom')
            
            # 3. Spending vs Age (scatter plot)
            if 'age' in self.data.columns:
                total_spending = self.data[spending_cols].sum(axis=1)
                axes[1, 0].scatter(self.data['age'], total_spending, alpha=0.6)
                axes[1, 0].set_title('Total Spending vs Age')
                axes[1, 0].set_xlabel('Age')
                axes[1, 0].set_ylabel('Total Monthly Spending ($)')
                
                # Add trend line
                z = np.polyfit(self.data['age'], total_spending, 1)
                p = np.poly1d(z)
                axes[1, 0].plot(self.data['age'], p(self.data['age']), "r--", alpha=0.8)
            
            # 4. Spending distribution (histogram)
            total_spending = self.data[spending_cols].sum(axis=1)
            axes[1, 1].hist(total_spending, bins=10, alpha=0.7, edgecolor='black')
            axes[1, 1].set_title('Distribution of Total Monthly Spending')
            axes[1, 1].set_xlabel('Total Monthly Spending ($)')
            axes[1, 1].set_ylabel('Number of Respondents')
            
            plt.tight_layout()
            
            # Save if path provided
            if save_path:
                create_directory_if_not_exists(os.path.dirname(save_path))
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                display_success_message(f"Spending charts saved to {save_path}")
            
            plt.show()
            return True
            
        except Exception as e:
            display_error_message(f"Error creating spending charts: {str(e)}")
            return False
    
    def create_savings_charts(self, save_path=None):
        """
        Create visualizations for savings analysis.
        
        Args:
            save_path (str): Optional path to save charts
            
        Returns:
            bool: True if successful
        """
        if self.data.empty or 'monthly_savings' not in self.data.columns:
            display_error_message("No savings data available")
            return False
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Personal Finance - Savings Analysis', fontsize=16, fontweight='bold')
            
            # 1. Savings distribution
            axes[0, 0].hist(self.data['monthly_savings'], bins=12, alpha=0.7, edgecolor='black', color='green')
            axes[0, 0].set_title('Distribution of Monthly Savings')
            axes[0, 0].set_xlabel('Monthly Savings ($)')
            axes[0, 0].set_ylabel('Number of Respondents')
            
            # 2. Savings vs Income (scatter plot)
            if 'annual_income' in self.data.columns:
                axes[0, 1].scatter(self.data['annual_income'], self.data['monthly_savings'], alpha=0.6, color='green')
                axes[0, 1].set_title('Savings vs Annual Income')
                axes[0, 1].set_xlabel('Annual Income ($)')
                axes[0, 1].set_ylabel('Monthly Savings ($)')
                
                # Add trend line
                z = np.polyfit(self.data['annual_income'], self.data['monthly_savings'], 1)
                p = np.poly1d(z)
                axes[0, 1].plot(self.data['annual_income'], p(self.data['annual_income']), "r--", alpha=0.8)
            
            # 3. Savings rate by age groups
            if 'annual_income' in self.data.columns and 'age' in self.data.columns:
                monthly_income = self.data['annual_income'] / 12
                savings_rate = self.data['monthly_savings'] / monthly_income
                
                age_groups = pd.cut(self.data['age'], bins=[0, 30, 40, 50, 100], labels=['<30', '30-40', '40-50', '50+'])
                avg_savings_rate = savings_rate.groupby(age_groups).mean()
                
                bars = axes[1, 0].bar(range(len(avg_savings_rate)), avg_savings_rate.values, 
                                     color='lightgreen', edgecolor='darkgreen')
                axes[1, 0].set_title('Average Savings Rate by Age Group')
                axes[1, 0].set_ylabel('Savings Rate')
                axes[1, 0].set_xticks(range(len(avg_savings_rate)))
                axes[1, 0].set_xticklabels(avg_savings_rate.index)
                
                # Add percentage labels
                for bar, value in zip(bars, avg_savings_rate.values):
                    axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
                                   f'{value:.1%}', ha='center', va='bottom')
            
            # 4. Emergency fund analysis
            if 'emergency_fund_months' in self.data.columns:
                fund_categories = ['<3 months', '3-6 months', '6+ months']
                fund_counts = [
                    len(self.data[self.data['emergency_fund_months'] < 3]),
                    len(self.data[(self.data['emergency_fund_months'] >= 3) & (self.data['emergency_fund_months'] < 6)]),
                    len(self.data[self.data['emergency_fund_months'] >= 6])
                ]
                
                colors = ['red', 'orange', 'green']
                axes[1, 1].pie(fund_counts, labels=fund_categories, autopct='%1.1f%%', colors=colors)
                axes[1, 1].set_title('Emergency Fund Adequacy')
            
            plt.tight_layout()
            
            if save_path:
                create_directory_if_not_exists(os.path.dirname(save_path))
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                display_success_message(f"Savings charts saved to {save_path}")
            
            plt.show()
            return True
            
        except Exception as e:
            display_error_message(f"Error creating savings charts: {str(e)}")
            return False
        
    def create_investment_charts(self, save_path=None):
        """
        Create visualizations for investment and crypto analysis.
        
        Args:
            save_path (str): Optional path to save charts
            
        Returns:
            bool: True if successful
        """
        if self.data.empty:
            display_error_message("No data available")
            return False
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Personal Finance - Investment & Cryptocurrency Analysis', fontsize=16, fontweight='bold')
            
            # 1. Investment preferences
            if 'primary_investment' in self.data.columns:
                investment_counts = self.data['primary_investment'].value_counts()
                
                axes[0, 0].pie(investment_counts.values, labels=investment_counts.index, autopct='%1.1f%%')
                axes[0, 0].set_title('Investment Preferences Distribution')
            
            # 2. Crypto ownership
            if 'owns_crypto' in self.data.columns:
                crypto_counts = self.data['owns_crypto'].value_counts()
                colors = ['lightcoral', 'lightblue']
                
                axes[0, 1].pie(crypto_counts.values, labels=['Owns Crypto', 'No Crypto'], 
                              autopct='%1.1f%%', colors=colors)
                axes[0, 1].set_title('Cryptocurrency Ownership')
            
            # 3. Investment preference by age
            if 'primary_investment' in self.data.columns and 'age' in self.data.columns:
                age_groups = pd.cut(self.data['age'], bins=[0, 30, 40, 50, 100], labels=['<30', '30-40', '40-50', '50+'])
                investment_age_crosstab = pd.crosstab(age_groups, self.data['primary_investment'])
                
                investment_age_crosstab.plot(kind='bar', ax=axes[1, 0], width=0.8)
                axes[1, 0].set_title('Investment Preferences by Age Group')
                axes[1, 0].set_xlabel('Age Group')
                axes[1, 0].set_ylabel('Number of Respondents')
                axes[1, 0].legend(title='Investment Type', bbox_to_anchor=(1.05, 1), loc='upper left')
                axes[1, 0].tick_params(axis='x', rotation=45)
            
            # 4. Crypto ownership vs Mobile banking
            if 'owns_crypto' in self.data.columns and 'uses_mobile_banking' in self.data.columns:
                tech_adoption = pd.crosstab(self.data['uses_mobile_banking'], self.data['owns_crypto'])
                
                tech_adoption.plot(kind='bar', ax=axes[1, 1], width=0.6)
                axes[1, 1].set_title('Technology Adoption Patterns')
                axes[1, 1].set_xlabel('Uses Mobile Banking')
                axes[1, 1].set_ylabel('Number of Respondents')
                axes[1, 1].legend(title='Owns Crypto', labels=['No', 'Yes'])
                axes[1, 1].tick_params(axis='x', rotation=0)
            
            plt.tight_layout()
            
            if save_path:
                create_directory_if_not_exists(os.path.dirname(save_path))
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                display_success_message(f"Investment charts saved to {save_path}")
            
            plt.show()
            return True
            
        except Exception as e:
            display_error_message(f"Error creating investment charts: {str(e)}")
            return False
    
    def create_financial_literacy_charts(self, save_path=None):
        """
        Create visualizations for financial literacy analysis.
        
        Args:
            save_path (str): Optional path to save charts
            
        Returns:
            bool: True if successful
        """
        if self.data.empty or 'financial_literacy_score' not in self.data.columns:
            display_error_message("No financial literacy data available")
            return False
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Personal Finance - Financial Literacy Analysis', fontsize=16, fontweight='bold')
            
            # 1. Score distribution
            axes[0, 0].hist(self.data['financial_literacy_score'], bins=10, alpha=0.7, 
                           edgecolor='black', color='purple')
            axes[0, 0].set_title('Financial Literacy Score Distribution')
            axes[0, 0].set_xlabel('Literacy Score (1-10)')
            axes[0, 0].set_ylabel('Number of Respondents')
            
            # 2. Literacy vs Income correlation
            if 'annual_income' in self.data.columns:
                axes[0, 1].scatter(self.data['financial_literacy_score'], self.data['annual_income'], 
                                  alpha=0.6, color='purple')
                axes[0, 1].set_title('Financial Literacy vs Income')
                axes[0, 1].set_xlabel('Financial Literacy Score')
                axes[0, 1].set_ylabel('Annual Income ($)')
                
                # Add trend line
                z = np.polyfit(self.data['financial_literacy_score'], self.data['annual_income'], 1)
                p = np.poly1d(z)
                axes[0, 1].plot(self.data['financial_literacy_score'], 
                               p(self.data['financial_literacy_score']), "r--", alpha=0.8)
            
            # 3. Literacy by age groups
            if 'age' in self.data.columns:
                age_groups = pd.cut(self.data['age'], bins=[0, 30, 40, 50, 100], labels=['<30', '30-40', '40-50', '50+'])
                literacy_by_age = self.data.groupby(age_groups)['financial_literacy_score'].mean()
                
                bars = axes[1, 0].bar(range(len(literacy_by_age)), literacy_by_age.values, 
                                     color='mediumpurple', edgecolor='darkviolet')
                axes[1, 0].set_title('Average Financial Literacy by Age Group')
                axes[1, 0].set_ylabel('Average Literacy Score')
                axes[1, 0].set_xticks(range(len(literacy_by_age)))
                axes[1, 0].set_xticklabels(literacy_by_age.index)
                
                # Add score labels
                for bar, value in zip(bars, literacy_by_age.values):
                    axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                                   f'{value:.1f}', ha='center', va='bottom')
            
            # 4. Literacy categories
            high_literacy = len(self.data[self.data['financial_literacy_score'] >= 8])
            medium_literacy = len(self.data[(self.data['financial_literacy_score'] >= 6) & 
                                          (self.data['financial_literacy_score'] < 8)])
            low_literacy = len(self.data[self.data['financial_literacy_score'] < 6])
            
            categories = ['Low (<6)', 'Medium (6-7)', 'High (8-10)']
            counts = [low_literacy, medium_literacy, high_literacy]
            colors = ['red', 'orange', 'green']
            
            axes[1, 1].pie(counts, labels=categories, autopct='%1.1f%%', colors=colors)
            axes[1, 1].set_title('Financial Literacy Categories')
            
            plt.tight_layout()
            
            if save_path:
                create_directory_if_not_exists(os.path.dirname(save_path))
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                display_success_message(f"Financial literacy charts saved to {save_path}")
            
            plt.show()
            return True
            
        except Exception as e:
            display_error_message(f"Error creating financial literacy charts: {str(e)}")
            return False
    
    def create_comprehensive_dashboard(self, save_path=None):
        """
        Create a comprehensive dashboard with key metrics.
        
        Args:
            save_path (str): Optional path to save the dashboard
            
        Returns:
            bool: True if successful
        """
        if self.data.empty:
            display_error_message("No data available")
            return False
        
        try:
            fig = plt.figure(figsize=(20, 16))
            fig.suptitle('Personal Finance Survey - Comprehensive Dashboard', fontsize=20, fontweight='bold')
            
            # Create a grid of subplots
            gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
            
            # 1. Age distribution
            ax1 = fig.add_subplot(gs[0, 0])
            if 'age' in self.data.columns:
                ax1.hist(self.data['age'], bins=8, alpha=0.7, edgecolor='black')
                ax1.set_title('Age Distribution')
                ax1.set_xlabel('Age')
                ax1.set_ylabel('Count')
            
            # 2. Income distribution
            ax2 = fig.add_subplot(gs[0, 1])
            if 'annual_income' in self.data.columns:
                ax2.hist(self.data['annual_income'], bins=8, alpha=0.7, edgecolor='black', color='green')
                ax2.set_title('Income Distribution')
                ax2.set_xlabel('Annual Income ($)')
                ax2.set_ylabel('Count')
            
            # 3. Savings vs Income
            ax3 = fig.add_subplot(gs[0, 2:])
            if 'annual_income' in self.data.columns and 'monthly_savings' in self.data.columns:
                ax3.scatter(self.data['annual_income'], self.data['monthly_savings'], alpha=0.6)
                ax3.set_title('Monthly Savings vs Annual Income')
                ax3.set_xlabel('Annual Income ($)')
                ax3.set_ylabel('Monthly Savings ($)')
            
            # 4. Investment preferences
            ax4 = fig.add_subplot(gs[1, 0])
            if 'primary_investment' in self.data.columns:
                investment_counts = self.data['primary_investment'].value_counts()
                ax4.pie(investment_counts.values, labels=investment_counts.index, autopct='%1.1f%%')
                ax4.set_title('Investment Preferences')
            
            # 5. Technology adoption
            ax5 = fig.add_subplot(gs[1, 1])
            if 'uses_mobile_banking' in self.data.columns and 'owns_crypto' in self.data.columns:
                mobile_banking = self.data['uses_mobile_banking'].sum()
                crypto_owners = self.data['owns_crypto'].sum()
                
                categories = ['Mobile Banking', 'Crypto Ownership']
                values = [mobile_banking, crypto_owners]
                
                ax5.bar(categories, values, color=['blue', 'orange'])
                ax5.set_title('Technology Adoption')
                ax5.set_ylabel('Number of Users')
            
            # 6. Spending breakdown
            ax6 = fig.add_subplot(gs[1, 2:])
            spending_cols = [col for col in self.data.columns if 'spending' in col.lower()]
            if spending_cols:
                spending_totals = {
                    col.replace('monthly_spending_', '').replace('_', ' ').title(): self.data[col].sum() 
                    for col in spending_cols
                }
                
                categories = list(spending_totals.keys())
                values = list(spending_totals.values())
                
                ax6.bar(categories, values, color=sns.color_palette("husl", len(categories)))
                ax6.set_title('Total Spending by Category')
                ax6.set_ylabel('Total Amount ($)')
                ax6.tick_params(axis='x', rotation=45)
            
            # 7. Financial literacy scores
            ax7 = fig.add_subplot(gs[2, :2])
            if 'financial_literacy_score' in self.data.columns:
                ax7.hist(self.data['financial_literacy_score'], bins=10, alpha=0.7, 
                        edgecolor='black', color='purple')
                ax7.set_title('Financial Literacy Score Distribution')
                ax7.set_xlabel('Literacy Score (1-10)')
                ax7.set_ylabel('Count')
            
            # 8. Emergency fund adequacy
            ax8 = fig.add_subplot(gs[2, 2:])
            if 'emergency_fund_months' in self.data.columns:
                fund_categories = ['<3 months', '3-6 months', '6+ months']
                fund_counts = [
                    len(self.data[self.data['emergency_fund_months'] < 3]),
                    len(self.data[(self.data['emergency_fund_months'] >= 3) & (self.data['emergency_fund_months'] < 6)]),
                    len(self.data[self.data['emergency_fund_months'] >= 6])
                ]
                
                colors = ['red', 'orange', 'green']
                ax8.pie(fund_counts, labels=fund_categories, autopct='%1.1f%%', colors=colors)
                ax8.set_title('Emergency Fund Adequacy')
            
            # 9. Summary statistics table
            ax9 = fig.add_subplot(gs[3, :])
            ax9.axis('off')
            
            # Create summary statistics
            summary_data = []
            if not self.data.empty:
                summary_data = [
                    ['Total Respondents', len(self.data)],
                    ['Average Age', f"{self.data['age'].mean():.1f} years" if 'age' in self.data.columns else 'N/A'],
                    ['Average Income', f"${self.data['annual_income'].mean():,.0f}" if 'annual_income' in self.data.columns else 'N/A'],
                    ['Average Savings', f"${self.data['monthly_savings'].mean():.0f}" if 'monthly_savings' in self.data.columns else 'N/A'],
                    ['Mobile Banking Adoption', f"{(self.data['uses_mobile_banking'].sum()/len(self.data)*100):.1f}%" if 'uses_mobile_banking' in self.data.columns else 'N/A'],
                    ['Crypto Ownership', f"{(self.data['owns_crypto'].sum()/len(self.data)*100):.1f}%" if 'owns_crypto' in self.data.columns else 'N/A']
                ]
            
            if summary_data:
                table = ax9.table(cellText=summary_data, 
                                 colLabels=['Metric', 'Value'],
                                 cellLoc='center',
                                 loc='center',
                                 bbox=[0.2, 0.2, 0.6, 0.6])
                table.auto_set_font_size(False)
                table.set_fontsize(12)
                table.scale(1.2, 1.5)
                ax9.set_title('Key Statistics Summary', fontsize=14, fontweight='bold')
            
            if save_path:
                create_directory_if_not_exists(os.path.dirname(save_path))
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                display_success_message(f"Dashboard saved to {save_path}")
            
            plt.show()
            return True
            
        except Exception as e:
            display_error_message(f"Error creating dashboard: {str(e)}")
            return False
    
    def export_all_charts(self, base_path="exports/charts"):
        """
        Export all chart types to files.
        
        Args:
            base_path (str): Base directory for saving charts
            
        Returns:
            bool: True if all exports successful
        """
        try:
            create_directory_if_not_exists(base_path)
            
            success_count = 0
            total_charts = 5
            
            # Export individual chart types
            if self.create_spending_charts(f"{base_path}/spending_analysis.png"):
                success_count += 1
            
            if self.create_savings_charts(f"{base_path}/savings_analysis.png"):
                success_count += 1
            
            if self.create_investment_charts(f"{base_path}/investment_analysis.png"):
                success_count += 1
            
            if self.create_financial_literacy_charts(f"{base_path}/literacy_analysis.png"):
                success_count += 1
            
            if self.create_comprehensive_dashboard(f"{base_path}/comprehensive_dashboard.png"):
                success_count += 1
            
            if success_count == total_charts:
                display_success_message(f"All {total_charts} chart files exported to {base_path}")
                return True
            else:
                display_error_message(f"Only {success_count}/{total_charts} charts exported successfully")
                return False
                
        except Exception as e:
            display_error_message(f"Error exporting charts: {str(e)}")
            return False    