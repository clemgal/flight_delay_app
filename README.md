# flight_delay_app

#  Flight Delay Explorer

**Flight Delay Explorer** is an interactive Streamlit dashboard that helps users understand flight delays in the United States.  
By selecting a **departure airport** and an **airline**, users can explore delay rates, total flights, and the main causes of delays—backed by real historical data.

The goal of the app is to help travelers (and analysts) **travel smarter with data**.

---

## Features

-  Select an **airport + airline duo**
-  Key Performance Indicators (KPIs):
  - Delay rate (≥ 15 minutes)
  - Total number of flights
  - Total number of delayed flights
-  Breakdown of **delay causes**:
  - Airline issues
  - Weather
  - Air traffic / NAS
  - Security
  - Late inbound aircraft
-  Interactive **Altair bar chart** (counts or minutes)
-  Optional animated chart rendering
-  Toggle between **chart view** and **table view**
-  Clean, modern UI with custom styling

---

##  Project Structure

```text
flight-delay-explorer/
│
├── app.py                     
│
├── pages/
│   └── 1_Airport_Glossary.py  
│
├── src/
│   ├── __init__.py
│   ├── load_data.py           
│   └── processing.py          
│
├── assets/
│   └── high-flying-plane.jpg  
│
├── data/
│   └── ...                   
│
├── notebooks/
│   └── data_exploration.ipynb 
│
├── requirements.txt
├── README.md
├── .gitignore
└── .vscode/                   

For this app, you need to pip install requirements.txt 