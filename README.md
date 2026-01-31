# Flight Delay Explorer

Flight Delay Explorer is an interactive Streamlit application designed to help users understand domestic flight delays in the United States.

By selecting a departure airport and an airline, users can explore:
- delay rates,
- total flights,
- delayed flights,
- and the main causes of delays,  
based on historical data covering 2013–2023.

The goal of the application is to help travelers make smarter decisions using data.

---

## Live Demo (Public Access)

The application is publicly deployed and accessible at:

https://flight-delay-app-07ci.onrender.com

### Note about the free hosting plan
This app is hosted on Render (free tier).

- If the application is inactive for some time, the service may spin down automatically
- The first request after inactivity may take up to 30–60 seconds
- After the initial load, the application runs normally

This behavior is expected and does not indicate an error.

---

## Features

- Selection of an airport + airline pair
- Key Performance Indicators (KPIs):
  - Delay rate (≥ 15 minutes)
  - Total number of flights
  - Total number of delayed flights
- Breakdown of delay causes:
  - Airline-related issues
  - Weather conditions
  - Air traffic / NAS
  - Security
  - Late inbound aircraft
- Interactive bar charts (counts or delay minutes)
- Optional animated chart rendering
- Toggle between chart view and table view
- Clean, modern UI with custom styling

---

## Project Structure

```text
flight_delay_app/
│
├── streamlit_app.py
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
├── notebooks/
│   └── data_exploration.ipynb
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── README.md
└── .gitignore

---

The app was coded using the following best practices for Code Quality: use type hints in functions, write docstrings for all functions, follow PEP 8 style guide and use logging instead of print(). 

# Flight Delay Explorer

This project is a Streamlit application for exploring and analyzing flight delays.

The app is fully dockerized, which guarantees that it runs the same way on Windows, macOS, and Linux.

---

## Run the app with Docker

### Prerequisites
- Docker installed  
  - Windows / Mac: Docker Desktop  
  - Linux: Docker Engine

## Build the Docker image
docker build -t flight-delay-app .

## Open the app locally
http://localhost:8502

---

### Clone the repository

```bash
git clone https://github.com/clemgal/flight_delay_app.git
cd flight_delay_app


