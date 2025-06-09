🧠 Dynamic MCP Database Agent
An intelligent, locally running database agent that uses LLaMA 3.2 via Ollama and MySQL to dynamically convert natural language queries into SQL commands. Built with Python and designed for fast prototyping using the FastMCP framework.

📌 Features
🔍 Natural language to SQL translation

🧠 LLaMA 3.2 model integration via Ollama

🗃️ Auto-detection of MySQL table schema

➕ Dynamic data insertion with user prompts

🔄 Support for SELECT, INSERT, UPDATE, DELETE queries

🔒 Uses environment variables for secure configuration

🧪 Connection testing for DB and LLM before execution

⚙️ Requirements
`Python 3.9+`

MySQL Server running locally or in Docker

Ollama running locally with llama3.2 pulled

.env file for credentials

🔧 Installation & Setup
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/HirushiKeshan/MCP-Database-Management.git
cd MCP-Database-Management
2. Set Up Python Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt
3. Set Up .env File
Create a .env file in the root directory:

ini
Copy
Edit
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=company

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
4. Start Ollama & Pull Model
Make sure Ollama is installed: https://ollama.com

bash
Copy
Edit
ollama pull llama3:instruct
5. Create the MySQL Table
Run this in MySQL Workbench or terminal:

sql
Copy
Edit
CREATE DATABASE IF NOT EXISTS company;
USE company;

CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(100),
    department VARCHAR(100),
    salary DECIMAL(10,2),
    hire_date DATE DEFAULT CURRENT_DATE
);
💡 Add some sample data if you'd like.

🚀 Running the Agent
Start the agent from the terminal:

bash
Copy
Edit
python Dynamic_MCP_Agent.py
💬 Usage
Once the agent is running, you can type natural language questions like:

"Show all employees in the Sales department"

"Add a new employee named Alice as a Designer in Product with salary 75000"

"Update salary of employee Alice to 90000"

"Delete employees in Marketing"

The agent will:

Send your query to the local LLaMA 3.2 model

Parse the LLM's structured JSON response

Execute the resulting SQL on your MySQL database

Show formatted results or confirmation

📊 Example Output
text
Copy
Edit
🗣️ You: show all employees in engineering

🧠 Raw LLM Response:
{
  "action": "SELECT",
  "sql": "SELECT * FROM employees WHERE department='engineering';",
  "needs_data": false,
  "response": "Fetching all employees in the engineering department."
}

🤖 📋 Found 3 record(s):
1. id: 1 | name: Alex | role: Engineer | department: engineering | salary: 75000.00 | hire_date: 2023-05-20
2. ...
🧪 Built-In Validations
✅ Tests database connection before starting

✅ Tests LLM connectivity using a sample prompt

❌ Fails gracefully if schema is invalid or LLM misbehaves

🛠️ Customization
🧩 Add More Tables
You can adapt the schema reading logic to support more tables. Currently, it works with a single table employees.

🧠 Use Custom Prompt Template
Edit the prompt section in process_user_request() for a different style or JSON structure.

🧼 TODO & Improvements
 Add unit tests

 Extend support for multiple tables

 Web UI interface (Streamlit/Gradio)

 Export SQL logs

