import streamlit as st
from components.chat import ChatInterface

st.set_page_config(page_title="AI Chat Analysis", page_icon="💬", layout="wide")

# Initialize chat interface
chat = ChatInterface()

def main():
    st.title("AI Chat Analysis")

    if not st.session_state.get('data_confirmed', False):
        st.warning("Please upload and confirm your data on the home page first")
        return

    # Render chat interface
    chat.render(st.session_state.current_df)

if __name__ == "__main__":
    main()
