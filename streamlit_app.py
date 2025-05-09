import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Load planetary degree data from the Excel file
df_planets = pd.read_excel('eph530n.xlsx')

# Convert 'Date' column to datetime format
df_planets['Date'] = pd.to_datetime(df_planets['Date'], format='%d-%m-%Y')

# Streamlit app interface
st.title('Planetary Degrees and Nifty index OHLC Chart')

index_options = {
    'Nifty 100': '^CNX100',
    'Nifty 200': '^CNX200',
    'Nifty 50': '^NSEI',
    'Nifty 500': '^CRSLDX',
    'Nifty Auto': '^CNXAUTO',
    'Nifty Bank': '^NSEBANK',
    'Nifty Commodities': '^CNXCMDT',
    'Nifty Consumer Durables': 'NIFTY_CONSR_DURBL.NS',
    'Nifty CPSE': 'NIFTYCPSE',
    'Nifty Energy': '^CNXENERGY',
    'Nifty Financial Services': 'NIFTY_FIN_SERVICES',
    'Nifty FMCG': '^CNXFMCG',
    'Nifty Healthcare Index': 'NIFTY_HEALTHCARE',
    'Nifty Infrastructure': '^CNXINFRA',
    'Nifty IT': '^CNXIT',
    'Nifty Media': '^CNXMEDIA',
    'Nifty Metal': '^CNXMETAL',
    'Nifty Microcap 250': 'NIFTY_MICROCAP250.NS',
    'Nifty MNC': '^CNXMNC',
    'Nifty Next 50': '^NSMIDCAP',
    'Nifty Oil & Gas': 'NIFTY_OIL_AND_GAS.NS',
    'Nifty Pharma': '^CNXPHARMA',
    'Nifty Private Bank': 'NIFTY_PVT_BANK.NS',
    'Nifty PSE': '^CNXPSE',
    'Nifty PSU Bank': '^CNXPSUBANK',
    'Nifty Realty': '^CNXREALTY',
    'Nifty Smallcap 100': '^CNXSC',
    'Nifty Total Market': 'NIFTY_TOTAL_MKT.NS',
}

# Sidebar: user inputs for date range
st.sidebar.subheader("Select Index and Date Range")
selected_index = st.sidebar.selectbox("Select Index", list(index_options.keys()))
selected_symbol = index_options[selected_index]

start_date = st.sidebar.date_input("Start Date", datetime(2018, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.today())

# Filter planetary data to match selected date range
df_planets = df_planets[(df_planets['Date'] >= pd.to_datetime(start_date)) & (df_planets['Date'] <= pd.to_datetime(end_date))]


# Error handling: end date should be after start date
if start_date > end_date:
    st.sidebar.error("End date must be after start date.")

# Sidebar: frequency selection
data_choice = st.sidebar.radio('Select the frequency of Nifty 50 data:', ('Daily', 'Weekly'))

# Determine interval based on selection
interval = '1d' if data_choice == 'Daily' else '1wk'

# Fetch Nifty 50 OHLC data
nifty_data = yf.download(
    selected_symbol,
    start=start_date.strftime('%Y-%m-%d'),
    end=end_date.strftime('%Y-%m-%d'),
    interval=interval, multi_level_index=False
)

# Ensure index is datetime
nifty_data.index = pd.to_datetime(nifty_data.index)

# Filter planetary data to match Nifty index dates if weekly
if data_choice == 'Weekly':
    df_planets = df_planets[df_planets['Date'].isin(nifty_data.index)]

# Merge Close prices into planetary data for display purposes
df_planets = pd.merge(df_planets, nifty_data[['Close']], left_on='Date', right_index=True, how='left')


# Plotting
fig = go.Figure()

# Add planetary degrees
planets = ['venus', 'mercury', 'sun', 'saturn', 'mars', 'rahu']
colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']

for planet, color in zip(planets, colors):
    fig.add_trace(go.Scatter(
        x=df_planets['Date'],
        y=df_planets[planet],
        mode='lines',
        name=planet.capitalize(),
        line=dict(color=color)
    ))

# Add candlestick plot for Nifty 50
fig.add_trace(go.Candlestick(
    x=nifty_data.index,
    open=nifty_data['Open'],
    high=nifty_data['High'],
    low=nifty_data['Low'],
    close=nifty_data['Close'],
    name='Nifty 50',
    yaxis='y2'
))

fig.update_layout(
    title=f'Planetary Degrees and Nifty index Candlestick Chart ({data_choice} Data)',
    xaxis_title='Date',
    yaxis_title='Planetary Degrees',
    xaxis=dict(
        rangeslider=dict(visible=False),
        type='date'
    ),
    yaxis2=dict(
        title='Price',
        overlaying='y',
        side='right',
        showgrid=False
    ),
    legend=dict(x=0.01, y=0.99),
    dragmode='zoom',
    hovermode="x unified"
)

# Show plot
st.plotly_chart(fig)
