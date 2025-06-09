# server.py
from mcp.server.fastmcp import FastMCP
from mcp.tool import tool
from mysql_utils import fetch_employees_by_department

mcp = FastMCP()

@mcp.tool
def get_employees_by_department(department: str) -> str:
    """Returns a list of employee names and IDs from a given department."""
    result = fetch_employees_by_department(department)
    if isinstance(result, str):  # error string
        return result
    if not result:
        return f"No employees found in {department} department."
    return "\n".join([f"ID: {row[0]}, Name: {row[1]}, Dept: {row[2]}" for row in result])

mcp.register(get_employees_by_department)

if __name__ == "__main__":
    mcp.serve()
