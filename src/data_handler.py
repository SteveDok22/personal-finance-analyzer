"""
Data Handler Module for Personal Finance Survey Analyzer.

This module handles CSV file loading, data validation, and preprocessing
for the personal finance survey analysis application.
"""

import pandas as pd
import os
from src.utils import (
    handle_file_error, display_success_message, display_error_message
)


class DataHandler:
    """Handles data loading, validation, and preprocessing operations."""

    def __init__(self):
        """Initialize the DataHandler."""
        self.data = None
        self.original_data = None
        self.data_info = {}

    def load_csv(self, file_path):
        """
        Load CSV file and perform initial validation.

        Args:
            file_path (str): Path to the CSV file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                display_error_message(f"File not found: {file_path}")
                return False

            # Load the CSV file
            self.data = pd.read_csv(file_path)
            self.original_data = self.data.copy()

            # Validate the loaded data
            if self._validate_data_structure():
                self._generate_data_info()
                display_success_message(
                    f"Successfully loaded {len(self.data)} records")
                return True
            else:
                return False

        except Exception as e:
            handle_file_error(e, file_path)
            return False

    def _validate_data_structure(self):
        """
        Validate that the CSV has required columns.

        Returns:
            bool: True if data structure is valid
        """
        required_columns = [
            'respondent_id', 'age', 'annual_income', 'monthly_savings',
            'uses_mobile_banking', 'owns_crypto', 'primary_investment'
        ]

        missing_columns = [
            col for col in required_columns if col not in self.data.columns]

        if missing_columns:
            display_error_message(
                f"Missing required columns: {missing_columns}")
            return False

        # Check if data is not empty
        if len(self.data) == 0:
            display_error_message("CSV file is empty")
            return False

        # Validate data types and clean data
        self._clean_data()

        return True

    def _clean_data(self):
        """Clean and preprocess the data."""
        try:
            # Clean numeric columns
            numeric_columns = [
                'age',
                'annual_income',
                'monthly_savings',
                'financial_literacy_score']
            for col in numeric_columns:
                if col in self.data.columns:
                    self.data[col] = pd.to_numeric(
                        self.data[col], errors='coerce')

            # Clean spending columns if they exist
            spending_columns = [
                col for col in self.data.columns
                if 'spending' in col.lower()
            ]
            for col in spending_columns:
                self.data[col] = pd.to_numeric(
                    self.data[col], errors='coerce'
                )

            # Clean yes/no columns - convert to True/False
            yes_no_columns = ['uses_mobile_banking', 'owns_crypto']
            for col in yes_no_columns:
                if col in self.data.columns:
                    self.data[col] = self.data[col].str.lower().map(
                        {'yes': True, 'no': False})

            # Remove rows with critical missing data
            critical_columns = ['age', 'annual_income']
            self.data = self.data.dropna(subset=critical_columns)

        except Exception as e:
            display_error_message(f"Error cleaning data: {str(e)}")

    def _generate_data_info(self):
        """Generate summary information about the loaded data."""
        self.data_info = {
            'total_records': len(self.data),
            'columns_count': len(self.data.columns),
            'numeric_columns': list(
                self.data.select_dtypes(
                    include=['int64', 'float64']
                ).columns
            ),
            'categorical_columns': list(
                self.data.select_dtypes(
                    include=['object', 'bool']
                ).columns
            ),
            'age_range': (
                self.data['age'].min(), self.data['age'].max()
            ) if 'age' in self.data.columns else None,
            'income_range': (
                self.data['annual_income'].min(),
                self.data['annual_income'].max()
            ) if 'annual_income' in self.data.columns else None
        }

    def get_data_summary(self):
        """
        Get a comprehensive summary of the loaded data.

        Returns:
            dict: Dictionary containing data summary information
        """
        if self.data is None:
            return {"error": "No data loaded"}

        summary = {
            "Dataset Overview": {
                "Total Respondents": len(self.data),
                "Number of Columns": len(self.data.columns),
                "Age Range": (
                    f"{self.data['age'].min():.0f} - "
                    f"{self.data['age'].max():.0f} years"
                    if 'age' in self.data.columns else "N/A"
                ),
                "Income Range": (
                    f"${self.data['annual_income'].min():,.0f} - "
                    f"${self.data['annual_income'].max():,.0f}"
                    if 'annual_income' in self.data.columns else "N/A"
                )
            },
            "Demographics": {
                "Average Age": (
                    f"{self.data['age'].mean():.1f} years"
                    if 'age' in self.data.columns else "N/A"
                ),
                "Median Income": (
                    f"${self.data['annual_income'].median():,.0f}"
                    if 'annual_income' in self.data.columns else "N/A"
                ),
                "Average Savings": (
                    f"${self.data['monthly_savings'].mean():,.0f}"
                    if 'monthly_savings' in self.data.columns else "N/A"
                )
            }
        }

        # Technology Adoption
        tech_adoption = {}
        if 'uses_mobile_banking' in self.data.columns:
            mobile_pct = (
                self.data['uses_mobile_banking'].sum() /
                len(self.data) * 100
            )
            tech_adoption["Mobile Banking Users"] = f"{mobile_pct:.1f}%"
        else:
            tech_adoption["Mobile Banking Users"] = "N/A"

        if 'owns_crypto' in self.data.columns:
            crypto_pct = (
                self.data['owns_crypto'].sum() /
                len(self.data) * 100
            )
            tech_adoption["Crypto Owners"] = f"{crypto_pct:.1f}%"
        else:
            tech_adoption["Crypto Owners"] = "N/A"

        summary["Technology Adoption"] = tech_adoption

        # Add investment preferences if available
        if 'primary_investment' in self.data.columns:
            investment_counts = self.data['primary_investment'].value_counts()
            summary["Investment Preferences"] = {
                inv_type.title(): (
                    f"{count} ({count / len(self.data) * 100:.1f}%)"
                )
                for inv_type, count in investment_counts.head().items()
            }

        return summary

    def filter_data(self, **kwargs):
        """
        Filter data based on provided criteria.

        Args:
            **kwargs: Filter criteria (e.g., min_age=25, max_income=100000)

        Returns:
            pd.DataFrame: Filtered data
        """
        if self.data is None:
            return pd.DataFrame()

        filtered_data = self.data.copy()

        try:
            # Age filters
            if 'min_age' in kwargs:
                filtered_data = filtered_data[
                    filtered_data['age'] >= kwargs['min_age']
                ]
            if 'max_age' in kwargs:
                filtered_data = filtered_data[
                    filtered_data['age'] <= kwargs['max_age']
                ]

            # Income filters
            if 'min_income' in kwargs:
                filtered_data = filtered_data[
                    filtered_data['annual_income'] >= kwargs['min_income']
                ]
            if 'max_income' in kwargs:
                filtered_data = filtered_data[
                    filtered_data['annual_income'] <= kwargs['max_income']
                ]

            # Boolean filters
            if 'uses_mobile_banking' in kwargs:
                filtered_data = filtered_data[
                    filtered_data['uses_mobile_banking'] ==
                    kwargs['uses_mobile_banking']
                ]
            if 'owns_crypto' in kwargs:
                filtered_data = filtered_data[
                    filtered_data['owns_crypto'] == kwargs['owns_crypto']
                ]

            # Investment type filter
            if 'investment_type' in kwargs:
                filtered_data = filtered_data[
                    filtered_data['primary_investment'] ==
                    kwargs['investment_type']
                ]

        except Exception as e:
            display_error_message(f"Error filtering data: {str(e)}")
            return self.data.copy()

        return filtered_data

    def get_data_validation_report(self):
        """
        Generate a data validation report.

        Returns:
            dict: Validation report with potential issues
        """
        if self.data is None:
            return {"error": "No data loaded"}

        report = {
            "Data Quality Issues": [],
            "Recommendations": []
        }

        # Check for missing values in critical columns
        critical_columns = ['age', 'annual_income', 'monthly_savings']
        for col in critical_columns:
            if col in self.data.columns:
                missing_pct = (
                    self.data[col].isnull().sum() /
                    len(self.data)
                ) * 100
                if missing_pct > 0:
                    report["Data Quality Issues"].append(
                        f"{col}: {missing_pct:.1f}% missing values"
                    )

        # Check for unrealistic values
        if 'age' in self.data.columns:
            if (
                (self.data['age'] < 18).any() or
                (self.data['age'] > 100).any()
            ):
                report["Data Quality Issues"].append(
                    "Age values outside realistic range (18-100)"
                )

        if 'annual_income' in self.data.columns:
            if (self.data['annual_income'] < 0).any():
                report["Data Quality Issues"].append(
                    "Negative income values found"
                )

        # Generate recommendations
        if len(report["Data Quality Issues"]) == 0:
            report["Recommendations"].append("Data quality looks good!")
        else:
            report["Recommendations"].append(
                "Consider cleaning data before analysis"
            )
            report["Recommendations"].append(
                "Review and handle missing values appropriately"
            )

        return report

    def export_cleaned_data(self, output_path):
        """
        Export cleaned data to CSV.

        Args:
            output_path (str): Path for output file

        Returns:
            bool: True if successful
        """
        try:
            if self.data is None:
                display_error_message("No data to export")
                return False

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            self.data.to_csv(output_path, index=False)
            display_success_message(f"Data exported to {output_path}")
            return True

        except Exception as e:
            display_error_message(f"Error exporting data: {str(e)}")
            return False