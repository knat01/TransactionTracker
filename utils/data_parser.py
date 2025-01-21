import pandas as pd
from datetime import datetime
import re
from utils.api import DeepSeekAPI

class WealthSimpleParser:
    def __init__(self):
        self.api = DeepSeekAPI()

    def parse_transactions(self, raw_text):
        """Parse Wealthsimple transaction history from raw text."""
        try:
            # Get CSV content and DataFrame from API
            csv_content, df = self.api.convert_to_csv(raw_text)

            # Basic validation of the DataFrame
            if df is None or df.empty:
                raise ValueError("No data was parsed from the input")

            # Convert date strings to datetime objects
            df['date'] = pd.to_datetime(df['date'])

            # Ensure transaction_type is uppercase
            df['transaction_type'] = df['transaction_type'].str.upper()

            # Ensure amount is numeric
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

            # Final validation
            required_columns = ['date', 'security', 'transaction_type', 'amount']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            return df

        except Exception as e:
            print(f"Error in parse_transactions: {str(e)}")
            raise Exception(f"Failed to parse transactions: {str(e)}")

    def calculate_portfolio_metrics(self, df):
        """Calculate key portfolio metrics from transaction data."""
        try:
            # Verify required columns exist
            required_cols = ['transaction_type', 'amount', 'security']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns for metrics calculation: {missing_cols}")

            metrics = {
                'total_invested': abs(df[df['transaction_type'] == 'BUY']['amount'].sum()),
                'total_sold': abs(df[df['transaction_type'] == 'SELL']['amount'].sum()),
                'num_transactions': len(df),
                'unique_securities': df['security'].nunique(),
            }

            return metrics

        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            raise Exception(f"Failed to calculate metrics: {str(e)}")