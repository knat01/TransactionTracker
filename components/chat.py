import streamlit as st
from utils.api import DeepSeekAPI

class ChatInterface:
    def __init__(self):
        self.api = DeepSeekAPI()

    def render(self, transactions_df):
        """Render the chat interface"""
        st.header("AI Analysis Chat", divider="red")

        # Create a container for all chat content
        chat_container = st.container()

        # Initialize or get chat history from session state
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

            # Generate initial analysis
            with st.spinner("Analyzing portfolio..."):
                initial_analysis = self.api.analyze_portfolio(transactions_df)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": initial_analysis
                })

        # Use the container to manage chat layout
        with chat_container:
            # Messages container
            messages_container = st.container()

            # Chat input at the bottom
            input_container = st.container()

            # Display all messages in the messages container
            with messages_container:
                for message in st.session_state.chat_messages:
                    with st.chat_message(message["role"]):
                        # Format numerical values and calculations
                        content = message["content"]
                        if message["role"] == "assistant" and any(keyword in content.lower() for keyword in ["profit", "calculation", "breakdown"]):
                            st.markdown(f"""
                                <div style='font-size: 16px; line-height: 1.6;'>
                                    {content}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(content)

            # Handle new messages
            with input_container:
                if prompt := st.chat_input("Ask about your portfolio...", key="chat_input"):
                    # Add user message
                    st.session_state.chat_messages.append({
                        "role": "user",
                        "content": prompt
                    })

                    # Display user message
                    with messages_container:
                        with st.chat_message("user"):
                            st.markdown(prompt)

                        # Generate and display AI response
                        with st.chat_message("assistant"):
                            response_placeholder = st.empty()

                            try:
                                with st.spinner("Thinking..."):
                                    context = transactions_df.to_string()
                                    response = self.api.chat_response(prompt, context)

                                    # Update response and chat history
                                    formatted_response = response.replace("$", "\\$")  # Escape dollar signs for markdown
                                    response_placeholder.markdown(f"""
                                        <div style='font-size: 16px; line-height: 1.6;'>
                                            {formatted_response}
                                        </div>
                                        """, unsafe_allow_html=True)
                                    st.session_state.chat_messages.append({
                                        "role": "assistant",
                                        "content": formatted_response
                                    })
                            except Exception as e:
                                error_message = f"Error generating response: {str(e)}"
                                response_placeholder.error(error_message)