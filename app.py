import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Custom CSS for button colors ---
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #4CAF50; /* Green */
        color: white;
    }
    div.stButton:nth-of-type(2) > button {
        background-color: #2196F3; /* Blue */
        color: white;
    }
    div.stButton:nth-of-type(3) > button {
        background-color: #9E9E9E; /* Gray */
        color: white;
    }
    div.stButton:nth-of-type(4) > button {
        background-color: #FFC107; /* Yellow */
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("AI Financial Planner")
st.caption("Enter your details → run projections → get AI suggestions.")

# --- User Input ---
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name", "JON SNOW")
    annual_income = st.number_input("Annual Income", value=60000, step=1000)
    horizon = st.number_input("Horizon (years)", value=10, step=1)
with col2:
    age = st.number_input("Age", value=30, step=1)
    monthly_savings = st.number_input("Monthly Savings", value=1000, step=100)
    current_savings = st.number_input("Current Savings", value=10000, step=500)

inflation = st.number_input("Inflation (annual)", value=0.03, format="%.2f")

risk = st.radio("Risk profile",
    ["Conservative", "Moderate", "Aggressive"], 
    index=1,
    horizontal=True
    )

# --- Quick Summary Sidebar ---
st.sidebar.subheader("Quick summary")
st.sidebar.write(f"**{name}**")
st.sidebar.write(f"Age: {age} • Savings: {current_savings}")
st.sidebar.write("### Projection snapshot")
st.sidebar.write(f"Horizon: {horizon} yrs")
st.sidebar.write(f"Monthly savings: {monthly_savings}")
st.sidebar.write(f"Risk: {risk.lower()}")

# --- Risk-based returns & allocations ---
if risk == "Conservative":
    est_return = 0.04
    allocation = {"Equities": 20, "Bonds": 60, "Cash": 20}
elif risk == "Moderate":
    est_return = 0.06
    allocation = {"Equities": 40, "Bonds": 40, "Cash": 20}
else:
    est_return = 0.08
    allocation = {"Equities": 60, "Bonds": 30, "Cash": 10}

st.write(f"Estimated annual return: **{est_return*100:.2f}%** • Inflation: **{inflation*100:.2f}%**")

# --- Action Buttons (horizontal + custom colors) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    save = st.button("Save & Project")
with col2:
    mc = st.button("Monte Carlo")
with col3:
    export = st.button("Export CSV")
with col4:
    ai_suggestion = st.button("AI Suggestion")

# --- Projection Calculation ---
def future_values(pv, pmt, r, n):
    values = []
    balance = pv
    for year in range(1, n+1):
        for _ in range(12):
            balance = balance * (1 + r/12) + pmt
        values.append(balance)
    return values

projection = None
if save:
    yearly_projection = future_values(current_savings, monthly_savings, est_return, horizon)
    projection = yearly_projection[-1]
    st.success(f"Projected Savings in {horizon} years: ${projection:,.2f}")

    # --- Line Chart ---
    fig, ax = plt.subplots()
    ax.plot(range(1, horizon+1), yearly_projection, marker="o")
    ax.set_title("Savings Growth Over Time")
    ax.set_xlabel("Years")
    ax.set_ylabel("Projected Savings ($)")
    st.pyplot(fig)

    # --- Pie Chart ---
    fig2, ax2 = plt.subplots()
    ax2.pie(allocation.values(), labels=allocation.keys(), autopct='%1.1f%%', startangle=90)
    ax2.set_title("Portfolio Allocation")
    st.pyplot(fig2)

# --- Monte Carlo ---
if mc:
    sims = 500
    monthly_r = est_return / 12
    results = np.zeros((sims, horizon*12))

    for s in range(sims):
        value = current_savings
        for m in range(horizon*12):
            r = np.random.normal(monthly_r, 0.15/12)
            value = value * (1 + r) + monthly_savings
            results[s, m] = value

    yearly_results = results[:, 11::12]
    median = np.percentile(yearly_results, 50, axis=0)
    p10 = np.percentile(yearly_results, 10, axis=0)
    p90 = np.percentile(yearly_results, 90, axis=0)

    years = np.arange(1, horizon+1)
    fig, ax = plt.subplots()
    ax.plot(years, median, label="Median Outcome", color="blue")
    ax.fill_between(years, p10, p90, color="blue", alpha=0.2, label="10th–90th Percentile")
    ax.set_title("Monte Carlo Simulation (500 runs)")
    ax.set_xlabel("Years")
    ax.set_ylabel("Portfolio Value ($)")
    ax.legend()
    st.pyplot(fig)

# --- Export CSV ---
if export and projection:
    df = pd.DataFrame({
        "Name": [name],
        "Age": [age],
        "Final Projection": [projection]
    })
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "financial_projection.csv", "text/csv")

# --- AI Suggestion ---
if ai_suggestion:
    st.subheader("AI Suggestion")
    st.markdown(f"""
    ### Personal Financial Plan for {name}
    1. **Allocation Strategy**:
       - **Equities ({allocation['Equities']}%)**: Diversified index funds or ETFs for growth.  
       - **Bonds ({allocation['Bonds']}%)**: Government & corporate bonds for stability.  
       - **Cash ({allocation['Cash']}%)**: High-yield savings or money market for liquidity.  

    2. **Savings Goal**: Stay consistent with monthly contributions of ${monthly_savings:,}.
    
    3. **Risk Profile**: As a {risk.lower()} investor, balance growth and stability.
    
    4. **Review Cycle**: Rebalance annually to maintain allocation.
    """)
