"""
Utility functions for the Personal Finance Survey Analyzer.

This module contains helper functions used across the application
for input validation, screen management, and common operations.
"""

import os
import sys


def clear_screen():
    """Clear the terminal screen for better user experience."""
    os.system('cls' if os.name == 'nt' else 'clear')


def validate_choice(choice, min_val, max_val):
    """
    Validate user menu choice.

    Args:
        choice (str): User input choice
        min_val (int): Minimum valid value
        max_val (int): Maximum valid value

    Returns:
        bool: True if choice is valid, False otherwise
    """
    try:
        choice_int = int(choice)
        return min_val <= choice_int <= max_val
    except ValueError:
        return False


def validate_yes_no(user_input):
    """
    Validate yes/no user input.

    Args:
        user_input (str): User input string

    Returns:
        bool or None: True for yes, False for no, None for invalid
    """
    user_input = user_input.strip().lower()
    if user_input in ['yes', 'y', '1']:
        return True
    elif user_input in ['no', 'n', '0']:
        return False
    else:
        return None


def format_currency(amount):
    """
    Format numeric value as currency.

    Args:
        amount (float): Numeric amount

    Returns:
        str: Formatted currency string
    """
    try:
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def format_percentage(value, decimal_places=1):
    """
    Format numeric value as percentage.

    Args:
        value (float): Numeric value (0-1 for percentage)
        decimal_places (int): Number of decimal places

    Returns:
        str: Formatted percentage string
    """
    try:
        return f"{value * 100:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "0.0%"


def print_section_header(title, width=50):
    """
    Print a formatted section header.

    Args:
        title (str): Header title
        width (int): Total width of the header
    """
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width)


def print_subsection_header(title, width=40):
    """
    Print a formatted subsection header.

    Args:
        title (str): Header title
        width (int): Total width of the header
     """
    print("\n" + "-" * width)
    print(f"{title}")
    print("-" * width)


def safe_divide(numerator, denominator, default=0):
    """
    Safely divide two numbers, handling division by zero.

    Args:
        numerator (float): Numerator value
        denominator (float): Denominator value
        default (float): Default value if division by zero

    Returns:
        float: Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (ValueError, TypeError):
        return default


def display_success_message(message):
    """Display a success message with checkmark."""
    print(f"✅ {message}")


def display_error_message(message):
    """Display an error message with X mark."""
    print(f"❌ {message}")


def display_loading_message(message="Loading..."):
    """Display a loading message."""
    print(f"⏳ {message}")


def wait_for_user():
    """Wait for user to press Enter before continuing."""
    input("\nPress Enter to continue...")


def handle_file_error(error, filename):
    """
    Handle file-related errors with user-friendly messages.

    Args:
        error (Exception): The exception that occurred
        filename (str): Name of the file being processed
    """
    if isinstance(error, FileNotFoundError):
        print(f"❌ File not found: {filename}")
        print("Please check that the file exists and try again.")
    elif isinstance(error, PermissionError):
        print(f"❌ Permission denied accessing: {filename}")
        print("Please check file permissions and try again.")
    else:
        print(f"❌ Error processing file {filename}: {str(error)}")


def create_directory_if_not_exists(directory_path):
    """
    Create directory if it doesn't exist.

    Args:
        directory_path (str): Path to directory

    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return True
    except OSError as e:
        print(f"Error creating directory {directory_path}: {e}")
        return False
