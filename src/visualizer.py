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