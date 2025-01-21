import streamlit as st
from components.dashboard import Dashboard
from utils.data_parser import WealthSimpleParser

st.set_page_config(page_title="Investment Dashboard", page_icon="📊", layout="wide")

# Initialize components
parser = WealthSimpleParser()
dashboard = Dashboard()

def main():
    st.title("Investment Dashboard")

    if not st.session_state.get('data_confirmed', False):
        st.warning("Please upload and confirm your data on the home page first")
        return

    # Calculate metrics for the dashboard
    metrics = parser.calculate_portfolio_metrics(st.session_state.current_df)
    
    # Render dashboard
    dashboard.render(st.session_state.current_df, metrics)

if __name__ == "__main__":
    main()
