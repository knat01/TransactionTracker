import os
import requests
import json
import pandas as pd
from io import StringIO

class DeepSeekAPI:
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"

    def convert_to_csv(self, raw_text):
        """Convert raw transaction text to CSV format using DeepSeek API"""
        prompt = """
        Convert the following transaction history into CSV format with EXACTLY these columns in this order:
        date,security,transaction_type,amount

        Required formatting:
        1. Column names must be EXACTLY as shown above (case-sensitive)
        2. date must be YYYY-MM-DD format
        3. security must be stock symbol only (e.g., AAPL instead of Apple Inc.)
        4. transaction_type must be either 'BUY' or 'SELL' only
        5. amount must be a number only (no currency symbols or commas)

        Rules:
        - Remove all currency symbols and commas from amounts
        - Remove any option/warrant details from tickers
        - Skip any cancelled or incomplete transactions
        - Each line must contain exactly these 4 columns
        - First line must be the header row exactly as shown above
        - Do not include any markdown formatting or explanations

        Here's the transaction data:
        {raw_text}

        Remember: Return ONLY the CSV data, starting with the exact header row shown above.
        """.format(raw_text=raw_text)

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek-chat",
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "max_tokens": 2000,
                "temperature": 0
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"API Error ({response.status_code}): {response.text}")

            response_data = response.json()
            csv_content = response_data['choices'][0]['message']['content'].strip()

            # Remove any markdown formatting
            if csv_content.startswith('```') and csv_content.endswith('```'):
                csv_content = csv_content[3:-3].strip()
            if csv_content.lower().startswith('csv'):
                csv_content = csv_content[3:].strip()

            # Validate the header row before parsing
            first_line = csv_content.split('\n')[0].strip()
            expected_header = "date,security,transaction_type,amount"
            if first_line != expected_header:
                raise ValueError(f"Invalid CSV header. Expected: {expected_header}, Got: {first_line}")

            # Parse CSV with pandas
            df = pd.read_csv(
                StringIO(csv_content),
                dtype={
                    'date': str,
                    'security': str,
                    'transaction_type': str,
                    'amount': float
                }
            )

            # Verify all required columns exist and match exactly
            required_columns = ['date', 'security', 'transaction_type', 'amount']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise ValueError(f"Missing required columns: {missing}")

            # Verify column order matches exactly
            if df.columns.tolist() != required_columns:
                raise ValueError("Column order does not match required format")

            return csv_content, df

        except Exception as e:
            print(f"Error in convert_to_csv: {str(e)}")
            raise Exception(f"Failed to convert transaction data: {str(e)}")

    def analyze_portfolio(self, transactions_df):
        """Send portfolio data to DeepSeek API for analysis"""
        prompt = f"""
        Analyze the following investment portfolio transactions and provide insights:

        {transactions_df.to_string()}

        Provide a clear analysis covering:
        1. Overall portfolio performance
        2. Key trends in trading patterns
        3. Risk assessment
        4. Suggestions for portfolio optimization

        Focus on actionable insights and clear metrics.
        """

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek-chat",
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.7,
                "max_tokens": 1000
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            return response.json()['choices'][0]['message']['content']

        except Exception as e:
            print(f"Error in portfolio analysis: {str(e)}")
            return f"Error analyzing portfolio: {str(e)}"

    def chat_response(self, user_question, context):
        """Get response for user questions about their portfolio"""
        prompt = f"""
        Context about the portfolio:
        {context}

        User question: {user_question}

        Provide a clear, specific answer based on the portfolio data.
        Focus on actionable insights and concrete numbers when available.
        """

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek-chat",
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.5,
                "max_tokens": 1000
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            return response.json()['choices'][0]['message']['content']

        except Exception as e:
            print(f"Error processing question: {str(e)}")
            return f"Error processing question: {str(e)}"