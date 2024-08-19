import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import plotly.graph_objs as go

st.title("Loan Repayments Calculator")

# Currency Selection
currency = st.selectbox("Select Currency", ("USD", "INR", "AED"))

# Conversion rates (You can update these with real-time data if needed)
conversion_rates = {
    "USD": 1,
    "INR": 83,  # Example conversion rate: 1 USD = 83 INR
    "AED": 3.67,  # Example conversion rate: 1 USD = 3.67 AED
}

# Currency symbols
currency_symbols = {
    "USD": "$",
    "INR": "₹",
    "AED": "د.إ",
}

# Conversion factor based on selected currency
conversion_rate = conversion_rates[currency]
currency_symbol = currency_symbols[currency]

st.write("### Input Data")
col1, col2 = st.columns(2)
home_value = col1.number_input(f"Home Value ({currency_symbol})", min_value=0, value=500000 * conversion_rate)
deposit = col1.number_input(f"Deposit ({currency_symbol})", min_value=0, value=100000 * conversion_rate)
interest_rate = col2.number_input("Interest Rate (in %)", min_value=0.0, value=5.5)
loan_term = col2.number_input("Loan Term (in years)", min_value=1, value=30)

# Calculate the repayments.
loan_amount = home_value - deposit
monthly_interest_rate = (interest_rate / 100) / 12
number_of_payments = loan_term * 12
monthly_payment = (
    loan_amount
    * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
    / ((1 + monthly_interest_rate) ** number_of_payments - 1)
)

# Display the repayments.
total_payments = monthly_payment * number_of_payments
total_interest = total_payments - loan_amount

st.write("### Repayments")
col1, col2, col3 = st.columns(3)
col1.metric(label="Monthly Repayments", value=f"{currency_symbol}{monthly_payment:,.2f}")
col2.metric(label="Total Repayments", value=f"{currency_symbol}{total_payments:,.0f}")
col3.metric(label="Total Interest", value=f"{currency_symbol}{total_interest:,.0f}")

# Create a data-frame with the payment schedule.
schedule = []
remaining_balance = loan_amount
total_interest_paid = 0

for i in range(1, number_of_payments + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance -= principal_payment
    total_interest_paid += interest_payment
    year = math.ceil(i / 12)  # Calculate the year into the loan
    schedule.append(
        [
            i,
            monthly_payment,
            principal_payment,
            interest_payment,
            remaining_balance,
            total_interest_paid,
            year,
        ]
    )

df = pd.DataFrame(
    schedule,
    columns=["Month", "Payment", "Principal", "Interest", "Remaining Balance", "Total Interest Paid", "Year"],
)

# Group by year to get the minimum remaining balance and total interest paid by year.
yearly_data = df.groupby("Year").agg({
    "Remaining Balance": "min",
    "Total Interest Paid": "max"
}).reset_index()

# Plot using Plotly for interactive chart with hover data.
fig = go.Figure()

fig.add_trace(go.Bar(
    x=yearly_data["Year"],
    y=yearly_data["Remaining Balance"],
    name="Remaining Balance",
    hovertext=[f"Interest Remaining: {currency_symbol}{int(total_interest - interest):,}<br>Total Repayment Remaining: {currency_symbol}{int(balance + total_interest - interest):,}" 
           for interest, balance in zip(yearly_data["Total Interest Paid"], yearly_data["Remaining Balance"])],
    hoverinfo="text",
    marker_color='lightsalmon'
))

# Update layout for better visualization.
fig.update_layout(
    title="Payment Schedule by Year",
    xaxis_title="Year",
    yaxis_title=f"Amount ({currency_symbol})",
    barmode='group',
    hovermode='x unified'
)

st.write("### Payment Schedule")
st.plotly_chart(fig)
