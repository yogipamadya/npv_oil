import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Function to calculate the cash flow for a given year
def cash_flow(year, max_production_rate, build_up_years, plateau_years, total_produced, total_recoverable_reserves, oil_price_per_barrel, operating_cost_per_barrel, tax_rate, government_take_percentage, decommissioning_cost, years, decline_rate):
    decline_rate_per_year = decline_rate
    remaining_oil = total_recoverable_reserves - total_produced

    if year <= build_up_years:
        production_rate = min(max_production_rate * (year / build_up_years), remaining_oil)
    elif year <= build_up_years + plateau_years:
        production_rate = min(max_production_rate, remaining_oil)
    else:
        decline_years = year - (build_up_years + plateau_years)
        production_rate = min(max_production_rate * ((1 - decline_rate_per_year) ** decline_years), remaining_oil)

    revenue = production_rate * oil_price_per_barrel
    cost = production_rate * operating_cost_per_barrel
    gross_profit = revenue - cost
    tax = gross_profit * tax_rate
    government_take = revenue * government_take_percentage
    net_cash_flow = gross_profit - tax - government_take

    if year == years:
        net_cash_flow -= decommissioning_cost

    return net_cash_flow, production_rate, revenue, cost, gross_profit, tax, government_take

# Function to calculate NPV
def calculate_npv(years, max_production_rate, build_up_years, plateau_years, total_recoverable_reserves, initial_investment, discount_rate, oil_price_per_barrel, operating_cost_per_barrel, tax_rate, government_take_percentage, decommissioning_cost, decline_rate):
    npv = -initial_investment
    total_produced = 0

    for year in range(1, years + 1):
        cf, _, _, _, _, _, _ = cash_flow(year, max_production_rate, build_up_years, plateau_years, total_produced, total_recoverable_reserves, oil_price_per_barrel, operating_cost_per_barrel, tax_rate, government_take_percentage, decommissioning_cost, years, decline_rate)
        total_produced += cf
        npv += cf / (1 + discount_rate) ** year

    return npv

# Function to calculate annual variables
def calculate_annual_variables(years, max_production_rate, build_up_years, plateau_years, total_recoverable_reserves, oil_price_per_barrel, operating_cost_per_barrel, tax_rate, government_take_percentage, decommissioning_cost, decline_rate):
    annual_data = []
    total_produced = 0

    for year in range(1, years + 1):
        net_cash_flow, production_rate, revenue, cost, gross_profit, tax, government_take = cash_flow(year, max_production_rate, build_up_years, plateau_years, total_produced, total_recoverable_reserves, oil_price_per_barrel, operating_cost_per_barrel, tax_rate, government_take_percentage, decommissioning_cost, years, decline_rate)
        total_produced += production_rate
        annual_data.append({
            'Year': year,
            'Production Rate (Barrels)': production_rate,
            'Revenue (USD)': revenue,
            'Operating Cost (USD)': cost,
            'Gross Profit (USD)': gross_profit,
            'Tax (USD)': tax,
            'Government Take (USD)': government_take,
            'Net Cash Flow (USD)': net_cash_flow
        })

    return pd.DataFrame(annual_data)

# Main function for Streamlit app
def main():
    st.set_page_config(layout='wide')
    st.title("Oil Production NPV Quick Screening")
    st.write('''This tool makes it easier for you by quickly checking if the asset is worth buying''')
    st.write("_This tool is auto-run, just alter your input parameters_")

    # Sidebar for input parameters
    with st.sidebar:
        st.write("## Input Parameters")
        initial_investment = st.number_input('Initial Investment (USD)', value=1000000)
        oil_price_per_barrel = st.number_input('Oil Price per Barrel (USD)', min_value=1, value=70)
        operating_cost_per_barrel = st.number_input('Operating Cost per Barrel (USD)', min_value=1, value=35)
        discount_rate = st.number_input('Discount Rate', min_value=0.0, max_value=1.0, value=0.10)
        tax_rate = st.number_input('Tax Rate', min_value=0.0, max_value=1.0, value=0.15)
        government_take_percentage = st.number_input('Government Take Percentage', min_value=0.0, max_value=1.0, value=0.25)
        ooip = st.number_input('Original Oil in Place (Barrels)', min_value=1000, value=12000000)
        recovery_rate = st.number_input('Recovery Rate', min_value=0.0, max_value=1.0, value=0.30)
        decommissioning_cost = st.number_input('Decommissioning Cost (USD)', min_value=0, value=500000)
        years = st.number_input('Total Project Life (Years)', min_value=1, max_value=100, value=20)
        max_production_rate = st.number_input('Maximum Production Rate (Barrels per Year)', min_value=0, value=125000)
        build_up_years = st.number_input('Build Up Years', min_value=0, max_value=years, value=3)
        plateau_years = st.number_input('Plateau Years', min_value=0, max_value=years, value=6)
        decline_rate = st.number_input('Decline Rate', min_value=0.0, max_value=1.0, value=0.10)

    total_recoverable_reserves = ooip * recovery_rate
    npv = calculate_npv(years, max_production_rate, build_up_years, plateau_years, total_recoverable_reserves, initial_investment, discount_rate, oil_price_per_barrel, operating_cost_per_barrel, tax_rate, government_take_percentage, decommissioning_cost, decline_rate)
    st.markdown('---')


    annual_variables_df = calculate_annual_variables(years, max_production_rate, build_up_years, plateau_years, total_recoverable_reserves, oil_price_per_barrel, operating_cost_per_barrel, tax_rate, government_take_percentage, decommissioning_cost, decline_rate)
    st.dataframe(annual_variables_df.round(2))
    st.write(f"### Calculated NPV: ${npv:,.2f}")
    # Calculate the total produced oil
    total_produced_oil = annual_variables_df['Production Rate (Barrels)'].sum()
    for a in annual_variables_df.columns:
        if a != 'Year':
            st.write(f"Total {a} = {annual_variables_df[f'{a}'].sum().round(1):,}")
    
    for column in annual_variables_df.columns:
        if column != 'Year':
            # Create a line chart for the current column
            fig = px.line(annual_variables_df, x='Year', y=column, title=f'Yearly {column}')
            fig.update_layout(yaxis_title=column, xaxis_title='Year')
            fig.update_layout(yaxis_range=[0, (annual_variables_df[f'{column}'].max())*1.15])
            
            # Display the chart in Streamlit
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()


