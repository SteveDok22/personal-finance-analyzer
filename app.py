"""
Personal Finance Survey Analyzer - Streamlit Web Application
A web-based application for analyzing personal finance survey data.
"""

import streamlit as st
import pandas as pd
import os
from src.data_handler import DataHandler
from src.analyzer import FinanceAnalyzer
from src.visualizer import DataVisualizer
from src.utils import format_currency, format_percentage

# Page configuration
st.set_page_config(
    page_title="Personal Finance Survey Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.data = None
    st.session_state.data_handler = None
    st.session_state.analyzer = None
    st.session_state.visualizer = None


def load_data_from_upload(uploaded_file):
    """Load data from uploaded CSV file."""
    try:
        df = pd.read_csv(uploaded_file)
        data_handler = DataHandler()
        data_handler.data = df
        data_handler.original_data = df.copy()
        
        if data_handler._validate_data_structure():
            data_handler._generate_data_info()
            st.session_state.data = data_handler.data
            st.session_state.data_handler = data_handler
            st.session_state.analyzer = FinanceAnalyzer(data_handler.data)
            st.session_state.visualizer = DataVisualizer(data_handler.data)
            st.session_state.data_loaded = True
            return True, f"✅ Successfully loaded {len(df)} records!"
        else:
            return False, "❌ Data validation failed."
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def load_sample_data():
    """Load sample data."""
    try:
        sample_path = 'data/sample_survey.csv'
        if os.path.exists(sample_path):
            data_handler = DataHandler()
            if data_handler.load_csv(sample_path):
                st.session_state.data = data_handler.data
                st.session_state.data_handler = data_handler
                st.session_state.analyzer = FinanceAnalyzer(data_handler.data)
                st.session_state.visualizer = DataVisualizer(data_handler.data)
                st.session_state.data_loaded = True
                return True, f"✅ Loaded {len(data_handler.data)} records!"
        return False, "❌ Sample file not found."
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def main():
    """Main application."""
    st.markdown('<h1 class="main-header">💰 Personal Finance Survey Analyzer</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome!
    Analyze personal finance survey data to gain insights into spending, savings, investments, and financial literacy.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("📂 Data Management")
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        
        if uploaded_file:
            if st.button("📥 Load File"):
                success, msg = load_data_from_upload(uploaded_file)
                st.success(msg) if success else st.error(msg)
                if success:
                    st.rerun()
        
        st.markdown("---")
        
        if st.button("📊 Load Sample Data"):
            success, msg = load_sample_data()
            st.success(msg) if success else st.error(msg)
            if success:
                st.rerun()
        
        st.markdown("---")
        
        if st.session_state.data_loaded:
            st.success(f"✅ {len(st.session_state.data)} records loaded")
        else:
            st.warning("⚠️ No data loaded")
        
        st.markdown("---")
        
        analysis_option = st.radio(
            "Choose Analysis:",
            ["📊 Data Summary", "💳 Spending", "💰 Savings", "📈 Investments", "🎓 Literacy", "📄 Complete Report"]
        )
    
    # Main content
    if not st.session_state.data_loaded:
        st.info("👈 Please load data from the sidebar to begin analysis")
        return
    
    if analysis_option == "📊 Data Summary":
        st.subheader("📊 Data Summary")
        summary = st.session_state.data_handler.get_data_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### Dataset Overview")
            for k, v in summary.get("Dataset Overview", {}).items():
                st.metric(k, v)
        with col2:
            st.markdown("### Demographics")
            for k, v in summary.get("Demographics", {}).items():
                st.metric(k, v)
        with col3:
            st.markdown("### Technology")
            for k, v in summary.get("Technology Adoption", {}).items():
                st.metric(k, v)
    
    elif analysis_option == "💳 Spending":
        st.subheader("💳 Spending Analysis")
        analysis = st.session_state.analyzer.get_spending_analysis()
        
        if "error" not in analysis:
            col1, col2, col3 = st.columns(3)
            overview = analysis.get("Spending Overview", {})
            with col1:
                st.metric("Avg Spending", overview.get("Average Total Spending", "N/A"))
            with col2:
                st.metric("Median Spending", overview.get("Median Total Spending", "N/A"))
            with col3:
                st.metric("Range", overview.get("Spending Range", "N/A"))
            
            if "Insights" in analysis:
                for insight in analysis["Insights"]:
                    st.info(insight)
            
            st.markdown("### 📊 Visualizations")
            fig = st.session_state.visualizer.create_spending_charts(save_path=None)
            if fig:
                st.pyplot(fig)
    
    elif analysis_option == "💰 Savings":
        st.subheader("💰 Savings Analysis")
        analysis = st.session_state.analyzer.get_savings_analysis()
        
        if "error" not in analysis:
            col1, col2, col3 = st.columns(3)
            overview = analysis.get("Savings Overview", {})
            with col1:
                st.metric("Avg Savings", overview.get("Average Monthly Savings", "N/A"))
            with col2:
                st.metric("Median Savings", overview.get("Median Monthly Savings", "N/A"))
            with col3:
                st.metric("Range", overview.get("Savings Range", "N/A"))
            
            if "Insights" in analysis:
                for insight in analysis["Insights"]:
                    st.info(insight)
            
            st.markdown("### 📊 Visualizations")
            fig = st.session_state.visualizer.create_savings_charts(save_path=None)
            if fig:
                st.pyplot(fig)
    
    elif analysis_option == "📈 Investments":
        st.subheader("📈 Investment Analysis")
        analysis = st.session_state.analyzer.get_investment_analysis()
        
        if "error" not in analysis:
            if "Cryptocurrency Analysis" in analysis:
                crypto = analysis["Cryptocurrency Analysis"]
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Crypto Owners", crypto.get("Total Crypto Owners", "N/A"))
                with col2:
                    st.metric("Adoption Rate", crypto.get("Crypto Adoption Rate", "N/A"))
            
            if "Insights" in analysis:
                for insight in analysis["Insights"]:
                    st.info(insight)
            
            st.markdown("### 📊 Visualizations")
            fig = st.session_state.visualizer.create_investment_charts(save_path=None)
            if fig:
                st.pyplot(fig)
    
    elif analysis_option == "🎓 Literacy":
        st.subheader("🎓 Financial Literacy")
        analysis = st.session_state.analyzer.get_financial_literacy_analysis()
        
        if "error" not in analysis:
            col1, col2, col3 = st.columns(3)
            overview = analysis.get("Literacy Overview", {})
            with col1:
                st.metric("Avg Score", overview.get("Average Score", "N/A"))
            with col2:
                st.metric("Median Score", overview.get("Median Score", "N/A"))
            with col3:
                st.metric("Range", overview.get("Score Range", "N/A"))
            
            if "Insights" in analysis:
                for insight in analysis["Insights"]:
                    st.info(insight)
            
            st.markdown("### 📊 Visualizations")
            fig = st.session_state.visualizer.create_financial_literacy_charts(save_path=None)
            if fig:
                st.pyplot(fig)
    
    elif analysis_option == "📄 Complete Report":
        st.subheader("📄 Comprehensive Report")
        report = st.session_state.analyzer.get_comprehensive_report()
        
        st.markdown("## Executive Summary")
        cols = st.columns(len(report.get("Executive Summary", {})))
        for idx, (k, v) in enumerate(report.get("Executive Summary", {}).items()):
            with cols[idx]:
                st.metric(k, v)
        
        st.markdown("## Key Findings")
        for i, finding in enumerate(report.get("Key Findings", []), 1):
            st.success(f"{i}. {finding}")
        
        st.markdown("## Dashboard")
        fig = st.session_state.visualizer.create_comprehensive_dashboard(save_path=None)
        if fig:
            st.pyplot(fig)


if __name__ == "__main__":
    main()