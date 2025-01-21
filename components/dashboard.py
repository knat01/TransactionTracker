import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class Dashboard:
    def __init__(self):
        self.colors = ['#FF4B4B', '#0068C9', '#FF8B4B', '#29B09D', '#F7DC6F']

    def render(self, transactions_df, metrics):
        """Render the dashboard with enhanced charts and metrics"""
        st.header("Portfolio Dashboard", divider="red")

        # Display key metrics
        self._render_metrics(metrics)

        # Top section: Monthly Performance and Asset Allocation
        col1, col2 = st.columns(2)
        with col1:
            self._render_monthly_performance(transactions_df)
        with col2:
            self._render_asset_allocation(transactions_df)

        # Middle section: Transaction Analysis
        st.subheader("Transaction Analysis")
        col3, col4 = st.columns(2)
        with col3:
            self._render_transaction_frequency(transactions_df)
        with col4:
            self._render_profit_loss_chart(transactions_df)

        # Bottom section: Transaction History and Top Performers
        col5, col6 = st.columns(2)
        with col5:
            self._render_transaction_history(transactions_df)
        with col6:
            self._render_top_performers(transactions_df)

    def _calculate_profit_loss(self, df):
        """Calculate profit/loss using FIFO method for accurate gains/losses"""
        results = {}

        for security in df['security'].unique():
            security_trades = df[df['security'] == security].sort_values('date')
            buy_queue = []
            total_profit = 0

            for _, trade in security_trades.iterrows():
                if trade['transaction_type'] == 'BUY':
                    buy_queue.append((abs(trade['amount']), trade['date']))
                elif trade['transaction_type'] == 'SELL':
                    sell_amount = abs(trade['amount'])
                    sell_date = trade['date']

                    while sell_amount > 0 and buy_queue:
                        buy_amount, buy_date = buy_queue.pop(0)

                        if buy_amount <= sell_amount:
                            # Complete sell of this buy lot
                            profit = sell_amount - buy_amount
                            total_profit += profit
                            sell_amount -= buy_amount
                        else:
                            # Partial sell
                            profit = sell_amount - (buy_amount * (sell_amount / buy_amount))
                            total_profit += profit
                            # Put remaining amount back in queue
                            remaining = buy_amount - sell_amount
                            buy_queue.insert(0, (remaining, buy_date))
                            sell_amount = 0

            results[security] = total_profit

        return results

    def _render_metrics(self, metrics):
        """Display enhanced key portfolio metrics"""
        st.subheader("Key Metrics")

        cols = st.columns(4)

        with cols[0]:
            st.metric(
                "Total Invested",
                f"${metrics.get('total_invested', 0):,.2f}",
                help="Total amount invested in buying securities"
            )

        with cols[1]:
            st.metric(
                "Total Realized",
                f"${metrics.get('total_sold', 0):,.2f}",
                help="Total amount received from selling securities"
            )

        with cols[2]:
            total_profit = metrics.get('total_sold', 0) - metrics.get('total_invested', 0)
            st.metric(
                "Net Profit/Loss",
                f"${total_profit:,.2f}",
                delta=f"{(total_profit / metrics.get('total_invested', 1) * 100):.1f}%" if metrics.get('total_invested', 0) > 0 else "0%",
                help="Total realized profit or loss from all transactions"
            )

        with cols[3]:
            st.metric(
                "Active Securities",
                f"{metrics.get('unique_securities', 0)}",
                help="Number of different securities in portfolio"
            )

    def _render_monthly_performance(self, df):
        """Create monthly cumulative profit chart"""
        st.header("Monthly Performance", divider="red")

        # Convert date to datetime and sort
        df['date'] = pd.to_datetime(df['date'])
        df_sorted = df.sort_values('date')

        # Calculate daily P/L and cumulative sum
        df_sorted['profit_loss'] = df_sorted.apply(
            lambda x: -x['amount'] if x['transaction_type'] == 'SELL' else 0, axis=1
        )
        df_sorted['cumulative_pl'] = df_sorted['profit_loss'].cumsum()

        # Create figure
        fig = go.Figure()

        # Add main trace with improved styling
        fig.add_trace(
            go.Scatter(
                x=df_sorted['date'],
                y=df_sorted['cumulative_pl'],
                mode='lines',
                line=dict(
                    color='#29B09D',  # Teal color matching screenshot
                    width=2,
                    shape='spline'  # Smooth curve
                ),
                hovertemplate="<b>%{x|%b %d, %Y}</b><br>" +
                             "$%{y:,.2f}<extra></extra>"  # Clean hover format
            )
        )

        # Update layout with refined styling
        fig.update_layout(
            title={
                'text': "Monthly Cumulative Profit/Loss",
                'font': dict(size=20),
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(l=60, r=30, t=60, b=60),
            xaxis=dict(
                title="Month",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(240,242,246,0.8)',
                tickformat='%b %d<br>%Y',
                tickfont=dict(size=11),
                tickangle=0,
                showline=True,
                linewidth=1,
                linecolor='rgba(240,242,246,1)'
            ),
            yaxis=dict(
                title="Cumulative Profit/Loss ($)",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(240,242,246,0.8)',
                tickprefix='$',
                tickformat=',',
                tickfont=dict(size=11),
                showline=True,
                linewidth=1,
                linecolor='rgba(240,242,246,1)'
            ),
            showlegend=False,
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor='white',
                font_size=12,
                font_family="sans-serif"
            )
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': False  # Hide the plotly mode bar
        })

    def _render_transaction_frequency(self, df):
        """Display transaction frequency analysis"""
        st.subheader("Transaction Frequency")

        # Calculate daily transaction counts
        daily_counts = df.groupby('date').size().reset_index()
        daily_counts.columns = ['date', 'count']

        fig = px.line(
            daily_counts,
            x='date',
            y='count',
            title='Daily Transaction Volume'
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Transactions",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    def _render_asset_allocation(self, df):
        """Create enhanced asset allocation pie chart"""
        st.subheader("Asset Allocation")

        # Calculate net position per security
        df['net_amount'] = df.apply(lambda x: x['amount'] if x['transaction_type'] == 'BUY' else -x['amount'], axis=1)
        allocation = df.groupby('security')['net_amount'].sum().abs()
        total = allocation.sum()

        # Calculate percentages
        allocation_pct = (allocation / total * 100).round(2)

        fig = px.pie(
            values=allocation.values,
            names=allocation.index,
            title='Portfolio Distribution'
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>" +
                          "Amount: $%{value:,.2f}<br>" +
                          "Percentage: %{percent:.1%}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)

    def _render_profit_loss_chart(self, df):
        """Create enhanced profit/loss visualization"""
        st.subheader("Profit/Loss by Security")

        # Calculate profit/loss using FIFO method
        pl_by_security = pd.Series(self._calculate_profit_loss(df))
        pl_by_security = pl_by_security.sort_values(ascending=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pl_by_security.index,
            y=pl_by_security.values,
            marker_color=['#FF4B4B' if x < 0 else '#29B09D' for x in pl_by_security.values]
        ))

        fig.update_layout(
            title='Security Performance (FIFO Method)',
            xaxis_title="Security",
            yaxis_title="Profit/Loss ($)",
            showlegend=False,
            xaxis_tickangle=45
        )
        st.plotly_chart(fig, use_container_width=True)

    def _render_transaction_history(self, df):
        """Display enhanced transaction history table"""
        st.subheader("Recent Transactions")

        # Get last 10 transactions with formatted values
        recent_transactions = df.sort_values('date', ascending=False).head(10).copy()
        recent_transactions['amount'] = recent_transactions['amount'].apply(lambda x: f"${abs(x):,.2f}")

        # Add styling
        st.dataframe(
            recent_transactions[['date', 'transaction_type', 'security', 'amount']],
            use_container_width=True,
            hide_index=True
        )

    def _render_top_performers(self, df):
        """Display top performing securities"""
        st.subheader("Top Gainers")

        # Calculate profit/loss using FIFO method
        security_pl = pd.Series(self._calculate_profit_loss(df))

        # Show only top gainers
        top_gainers = security_pl[security_pl > 0].sort_values(ascending=False).head(3)
        for security, profit in top_gainers.items():
            st.metric(
                security,
                f"${profit:,.2f}",
                delta="↑ profit",
                delta_color="normal"
            )