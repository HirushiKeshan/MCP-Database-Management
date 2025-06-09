#!/usr/bin/env python3
"""
Dynamic MCP Database Agent - Clean and Accurate
Uses live schema to generate intelligent SQL via local LLM
"""

import os
import json
import requests
import mysql.connector
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class SimpleMCPAgent:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'company')
        }
        self.llm_url = f"{os.getenv('OLLAMA_HOST', 'http://localhost:11434')}/api/generate"
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.schema = self._get_table_info()

    def _get_table_info(self):
        """Read real table schema from DB"""
        try:
            with mysql.connector.connect(**self.db_config) as conn:
                cursor = conn.cursor()
                cursor.execute("DESCRIBE employees")
                columns = cursor.fetchall()
                if not columns:
                    raise Exception("No columns found in employees table")

                schema = {
                    'table': 'employees',
                    'columns': [col[0] for col in columns],
                    'structure': ', '.join([f"{col[0]}({col[1]})" for col in columns])
                }
                logging.info(f"📋 Detected columns: {', '.join(schema['columns'])}")
                return schema
        except Exception as e:
            logging.error(f"❌ Schema detection failed: {e}")
            raise RuntimeError("Could not read schema. Please ensure the 'employees' table exists.")

    def ask_llm(self, prompt):
        """Query local LLM with structured prompt"""
        try:
            response = requests.post(
                self.llm_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=30
            )
            return response.json().get('response', '').strip()
        except Exception as e:
            logging.error(f"LLM request failed: {e}")
            return ""

    def execute_sql(self, sql, params=None):
        try:
            with mysql.connector.connect(**self.db_config) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(sql, params or ())
                if sql.strip().upper().startswith('SELECT'):
                    return {'type': 'select', 'data': cursor.fetchall()}
                else:
                    conn.commit()
                    return {'type': 'modify', 'rows_affected': cursor.rowcount}
        except mysql.connector.Error as e:
            return {'type': 'error', 'message': str(e)}

    def process_user_request(self, user_input):
        prompt = f"""
You are a helpful SQL assistant.

Database Info:
- Table: {self.schema['table']}
- Columns: {', '.join(self.schema['columns'])}
- Structure: {self.schema['structure']}

User Request: "{user_input}"

Reply in EXACTLY this JSON format:
{{
  "action": "SELECT|INSERT|UPDATE|DELETE|HELP",
  "sql": "SQL statement or null",
  "explanation": "Brief reasoning",
  "needs_data": false
}}

Rules:
- Use ORDER BY id for SELECTs.
- Use LIKE '%term%' for searches.
- For INSERT, set needs_data = true if values are missing.
"""

        llm_response = self.ask_llm(prompt)
        try:
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            result = json.loads(llm_response[json_start:json_end])

            action = result.get('action', '').upper()

            if action == 'HELP':
                return f"💡 {result.get('explanation')}"

            if result.get('needs_data'):
                return self._collect_data_for_insert()

            sql = result.get('sql')
            if not sql:
                return "❌ No SQL generated"

            db_result = self.execute_sql(sql)

            if db_result['type'] == 'error':
                return f"❌ Database Error: {db_result['message']}"

            if db_result['type'] == 'select':
                return self._format_select_results(db_result['data'])

            if db_result['type'] == 'modify':
                rows = db_result['rows_affected']
                return f"✅ {rows} record(s) {action.lower()}d." if rows else "⚠️ No rows affected"

        except json.JSONDecodeError:
            return "❌ Failed to parse LLM response"
        except Exception as e:
            return f"❌ Error: {e}"

    def _collect_data_for_insert(self):
        """Collect only real schema fields from user"""
        print("\n📝 Adding new employee:")
        try:
            insertable = [col for col in self.schema['columns'] if col not in ('id', 'hire_date')]
            data = {}

            for field in insertable:
                value = input(f"Enter {field}: ").strip()
                if not value:
                    return "❌ All fields are required"
                data[field] = value

            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            sql = f"INSERT INTO employees ({columns}) VALUES ({placeholders})"
            result = self.execute_sql(sql, tuple(data.values()))

            if result['type'] == 'error':
                return f"❌ Insert failed: {result['message']}"
            return f"✅ Employee {data.get('name', '')} added!"

        except KeyboardInterrupt:
            return "❌ Insert cancelled"

    def _format_select_results(self, data):
        if not data:
            return "📋 No records found"

        output = f"📋 Found {len(data)} record(s):\n" + "-" * 50 + "\n"
        for i, row in enumerate(data, 1):
            line = " | ".join([f"{k}: {v}" for k, v in row.items()])
            output += f"{i}. {line}\n"
        return output

    def test_connections(self):
        print("🔍 Testing connections...")
        try:
            result = self.execute_sql("SELECT COUNT(*) as count FROM employees")
            if result['type'] == 'select':
                print(f"✅ Database OK: {result['data'][0]['count']} employees")
            else:
                print(f"❌ Database: {result.get('message', 'error')}")
                return False
        except Exception as e:
            print(f"❌ DB Test Failed: {e}")
            return False

        try:
            test = self.ask_llm("Reply with only OK")
            if "OK" in test.upper():
                print(f"✅ LLM OK: {self.model}")
            else:
                print("⚠️ LLM responded, but not as expected")
        except Exception as e:
            print(f"❌ LLM Test Failed: {e}")
            return False

        return True

def main():
    print("🤖 Dynamic MCP Database Agent")
    print("=" * 40)

    agent = SimpleMCPAgent()
    if not agent.test_connections():
        print("❌ Connection test failed. Check your `.env` and DB.")
        return

    print("\n💬 Ask anything. Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("🗣️ You: ").strip()
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            if user_input:
                response = agent.process_user_request(user_input)
                print(f"\n🤖 {response}")
        except KeyboardInterrupt:
            print("\n👋 Exiting.")
            break
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()
