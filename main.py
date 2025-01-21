import streamlit as st
from utils.data_parser import WealthSimpleParser

# Page configuration
st.set_page_config(
    page_title="Upload Data",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize components
parser = WealthSimpleParser()

def main():
    st.title("Upload Data") 

    # Introduction section
    st.markdown("""
    ## Welcome to AI Investment Analyzer! 📊

    This advanced analytics platform helps Wealthsimple users gain deeper insights into their investment portfolio through:

    - 📈 **Real-time Performance Tracking**: Monitor your portfolio's performance with interactive charts
    - 🤖 **AI-Powered Analysis**: Get intelligent insights about your trading patterns
    - 📊 **Advanced Visualizations**: View your data through comprehensive charts and metrics
    - 💬 **Interactive Chat Analysis**: Ask questions about your portfolio and get AI-powered responses

    ### How to Use
    1. Copy your Wealthsimple transaction history
    2. Paste it in the text box below
    3. Click "Process Data" to analyze
    4. Navigate to Dashboard or AI Chat Analysis for insights
    """)

    # Initialize session state for tracking app state
    if 'data_processed' not in st.session_state:
        st.session_state.data_processed = False
    if 'data_confirmed' not in st.session_state:
        st.session_state.data_confirmed = False

    # Main content area for data input
    st.write("### Upload Your Data")
    st.write("Paste your Wealthsimple transaction history below:")

    raw_data = st.text_area(
        "Transaction Data",
        height=300,
        help="Copy and paste your Wealthsimple transaction history here"
    )

    analyze_button = st.button("Process Data")

    # Process data when button is clicked
    if analyze_button and raw_data:
        try:
            csv_content, transactions_df = parser.api.convert_to_csv(raw_data)
            st.session_state.data_processed = True
            st.session_state.data_confirmed = True  # Auto-confirm when processing succeeds
            st.session_state.current_csv = csv_content
            st.session_state.current_df = transactions_df
            st.success("Data processed successfully! You can now navigate to the Dashboard or AI Chat Analysis pages.")

        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            st.info("Please ensure your data is in the correct Wealthsimple format")
            st.session_state.data_processed = False
            st.session_state.data_confirmed = False

    # Show welcome message if no data processed
    if not st.session_state.data_processed:
        st.info("Please paste your transaction data above and click 'Process Data' to begin")

    # Hide streamlit default menu
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

if __name__ == "__main__":
    main()