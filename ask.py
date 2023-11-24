import json
import sqlite3 
import argparse
from textwrap import dedent
from openai import OpenAI


conn = sqlite3.connect('imdb.db')
cursor = conn.cursor()
client = OpenAI()


def get_schemas() -> str:
    """
    Return table schemas in TOML formatting:
    
    [table_name]
    column_name (type) = description
    """
    with open("tables.toml", "r") as f:
        return f.read()
    

def query_result_as_markdown_table(query: str) ->  str:
    """
    Takes a SQL query, executes it, and returns its output table in markdown format

    @param query: SQL query, using SQLite syntax
    """
    try:
        cursor.execute(query)
        header = [description[0] for description in cursor.description]
        data = cursor.fetchall()
    except Exception as e:
        return f"Error while running query: {e}"
    
    if not data:
        return ""

    # Formatting the header
    header_line = '| ' + ' | '.join(header) + ' |'
    separator_line = '|---' * len(header) + '|'

    # Formatting the data
    data_lines = []
    for row in data:
        row_line = '| ' + ' | '.join(str(item) for item in row) + ' |'
        data_lines.append(row_line)

    # Joining all parts into a single string
    markdown_table = '\n'.join([header_line, separator_line] + data_lines)
    return markdown_table


system_prompt = {
    "role": "system", 
    "content": dedent(f"""You are an expert and useful BI assistant. You only use the data provided to you to reply on questions.
               The tables you can use and their descriptions are provided below in TOML format in the following way:
                
                [table_name]
                column_name (type) = description
                
                Tables:
                ```
                {get_schemas()}
                ``
                
               IMPORTANT: You can only rely on the data from these tables.""")
}

instructions = dedent("""IMPORTANT:
                      * When creating SQL queries, use SQLite syntax. Arrays are stores as TEXT with commas separating values
                      * Your response must be human-readable and understandble to the average user. 
                      * When possible, reply using lists.
                      """)

tools = [
    {
        "type": "function",
        "function": {
            "name": "query_result_as_markdown_table",
            "description": "This function takes a SQL query, runs it in the database and returns the output table in markdown format",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "the SQL query to run. Its output will be returned as a markdown table"
                    }
                },
                "required": ["query"],
            }
        }
    }
]


def ask_question(question: str, model: str, verbose: bool) -> str:
    """
    Asks GPT the user's question

    @param question: the user's question
    @para model: the OpenAI model to use
    """
    messages = [system_prompt, {"role": "user", "content": f"{question}\n{instructions}"}]

    final_message = False

    while not final_message:
        if verbose:
            print(f" -> Querying {model}")
        completion = client.chat.completions.create(model=model, temperature=0., messages=messages, tools=tools)
        assistant_message = completion.choices[0].message
        messages.append(assistant_message)
        
        if assistant_message.tool_calls:
            query = json.loads(assistant_message.tool_calls[0].function.arguments)['query']
            if verbose:
                print(f" -> Running SQL query: {query}")
            query_result = query_result_as_markdown_table(query)
            messages.append({
                "tool_call_id": assistant_message.tool_calls[0].id,
                "role": "tool",
                "name": "query_result_as_markdown_table",
                "content": query_result
            })
        else:
            final_message = True
            
    return(messages[-1].content)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-m', '--model', default='gpt-4', help='Name of OpenAI chat model to use', dest='model')
    arg_parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Enable verbose mode', dest='verbose')
    args = arg_parser.parse_args()

    print("\nWelcome! Ask as many IMDB-related questions as you would like. To exit, press Ctrl+C.")
    if args.verbose:
        print("Verbose mode on.")
    print("\n")

    while True:
        question = input("What would you like to know? ")
        response = ask_question(question, model=args.model, verbose=args.verbose)
        print(response + '\n')
