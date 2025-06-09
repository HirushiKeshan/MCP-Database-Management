import os
import asyncio
import json
import requests
import mysql.connector
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME')
        }
    
    def get_connection(self):
        return mysql.connector.connect(**self.config)
    
    def execute_query(self, query, params=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = {"affected_rows": cursor.rowcount}
            
            cursor.close()
            conn.close()
            return result
        except mysql.connector.Error as e:
            return {"error": str(e)}

class OllamaClient:
    def __init__(self):
        self.host = os.getenv('OLLAMA_HOST')
        self.model = os.getenv('OLLAMA_MODEL')
    
    def generate_response(self, prompt):
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get('response', '')
        except requests.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}"

# Initialize components
db_manager = DatabaseManager()
ollama_client = OllamaClient()

# Initialize FastMCP
mcp = FastMCP("Employee Database Assistant")

@mcp.tool()
def get_employee_by_id(employee_id: int) -> str:
    """Get employee details by ID"""
    query = "SELECT * FROM employees WHERE id = %s"
    result = db_manager.execute_query(query, (employee_id,))
    
    if isinstance(result, list) and result:
        return json.dumps(result[0], indent=2)
    elif isinstance(result, dict) and 'error' in result:
        return f"Database error: {result['error']}"
    else:
        return "Employee not found"

@mcp.tool()
def get_all_employees() -> str:
    """Get all employees from the database"""
    query = "SELECT * FROM employees"
    result = db_manager.execute_query(query)
    
    if isinstance(result, list):
        return json.dumps(result, indent=2)
    elif isinstance(result, dict) and 'error' in result:
        return f"Database error: {result['error']}"
    else:
        return "No employees found"

@mcp.tool()
def search_employees_by_name(name: str) -> str:
    """Search employees by name (partial match)"""
    query = "SELECT * FROM employees WHERE name LIKE %s"
    result = db_manager.execute_query(query, (f"%{name}%",))
    
    if isinstance(result, list):
        return json.dumps(result, indent=2)
    elif isinstance(result, dict) and 'error' in result:
        return f"Database error: {result['error']}"
    else:
        return "No employees found matching the search criteria"

@mcp.tool()
def get_employees_by_department(department: str) -> str:
    """Get employees by department"""
    query = "SELECT * FROM employees WHERE department = %s"
    result = db_manager.execute_query(query, (department,))
    
    if isinstance(result, list):
        return json.dumps(result, indent=2)
    elif isinstance(result, dict) and 'error' in result:
        return f"Database error: {result['error']}"
    else:
        return "No employees found in the specified department"

@mcp.tool()
def add_employee(name: str, email: str, department: str, salary: float) -> str:
    """Add a new employee to the database"""
    query = "INSERT INTO employees (name, email, department, salary) VALUES (%s, %s, %s, %s)"
    result = db_manager.execute_query(query, (name, email, department, salary))
    
    if isinstance(result, dict) and 'affected_rows' in result:
        return f"Employee added successfully. Affected rows: {result['affected_rows']}"
    elif isinstance(result, dict) and 'error' in result:
        return f"Database error: {result['error']}"
    else:
        return "Failed to add employee"

@mcp.tool()
def ask_ollama(question: str, context: str = "") -> str:
    """Ask Ollama LLM a question with optional context"""
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    response = ollama_client.generate_response(prompt)
    return response

@mcp.tool()
def analyze_employee_data(query_description: str) -> str:
    """Analyze employee data using Ollama LLM"""
    # First get all employee data
    employees_data = get_all_employees()
    
    # Ask Ollama to analyze the data
    prompt = f"""
    Analyze the following employee data and answer this question: {query_description}
    
    Employee Data:
    {employees_data}
    
    Please provide insights based on the data above.
    """
    
    analysis = ollama_client.generate_response(prompt)
    return analysis

if __name__ == "__main__":
    print("Starting FastMCP server with Ollama and MySQL integration...")
    print("Available tools:")
    print("- get_employee_by_id")
    print("- get_all_employees") 
    print("- search_employees_by_name")
    print("- get_employees_by_department")
    print("- add_employee")
    print("- ask_ollama")
    print("- analyze_employee_data")
    
    # Start the MCP server
    mcp.run()
