# Gemini-Powered Travel Assistant

This project is a travel assistant powered by Gemini, providing information and recommendations for different travel destinations.

## Backend

The backend of this project is built using Flask, a micro web framework for Python. It interacts with Gemini to fetch information and recommendations for the provided travel destinations.

### Installation

1. Navigate to the `backend/` directory in your terminal.
2. Ensure you have Poetry installed and initialized in your project.
3. Install dependencies by running:
poetry install
   

### Running the Backend

To start the Flask server for the backend:
poetry run python app.py


## Frontend

The frontend of this project is built using Streamlit, an open-source Python library that makes it easy to create web apps for machine learning and data science. It provides a user-friendly interface for users to interact with the travel assistant.

### Installation

1. Open a new terminal window or tab.
2. Navigate to the `frontend/` directory in your terminal.
3. Ensure you have Poetry installed and initialized in your project.
4. Install dependencies by running:

poetry install


### Running the Frontend

To start the Streamlit server for the frontend:

poetry run streamlit run index.py


Once both the backend and frontend servers are running, you can access the Gemini-Powered Travel Assistant in your web browser. Enter a place name in the provided input field and click the "Explore" button to receive information and recommendations for the selected destination.

Enjoy exploring with Gemini!

#### Runnoing on the local machine for webhook
 ngrok http http://localhost:5000
