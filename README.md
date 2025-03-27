# ChatBot

## Installation

### 1. Install Dependencies
Run the following command to install all required dependencies:
```sh
pip install -r requirements.txt
```

## Running the Server

### 2. Start the Server
Execute the following command to start the chatbot server:
```sh
python ing.py --api
```

## Data Ingestion

### 3. Ingest Data Using Postman
To send content and source data to the database, use Postman (or any API tool) and follow these steps:

- **Endpoint:**
  ```http
  POST http://localhost:8000/ingest
  ```

- **Headers:**
  ```
  Content-Type: application/json
  ```

- **Payload Format (JSON):**
  ```json
  {
    "content": "Your text content here",
    "source": "Source information here"
  }
  ```
