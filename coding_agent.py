import os
import getpass
import subprocess

from dotenv import load_dotenv
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.toolsets import FunctionToolset
from rich.console import Console

load_dotenv()

LLM_URL = os.getenv('LLM_URL')
LLM_MODEL = os.getenv('LLM_MODEL')
LLM_API_KEY = os.getenv('LLM_API_KEY')


# Define the model
model = OllamaModel(
    model_name=LLM_MODEL,
    provider=OllamaProvider(
        base_url=LLM_URL,
        api_key=LLM_API_KEY
    )
)

# Executors
def execute_read(path: str) -> str:
    """Read a file from the filesystem."""
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error: {e}"


def execute_write(file_path: str, content: str) -> str:
    """Create or overwrite a file."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return f"Wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"Error: {e}"


def execute_edit(file_path: str, old_str: str, new_str: str) -> str:
    """Find and replace text in a file."""
    try:
        path = Path(file_path)
        content = path.read_text()
        new_content = content.replace(old_str, new_str)
        path.write_text(new_content)
        return "Edit successful"
    except Exception as e:
        return f"Error: {e}"


def execute_bash(command: str) -> str:
    """Execute a shell command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout + result.stderr
        return output if output.strip() else "(no output)"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    console = Console()
    # Create a function tool set
    coding_tools = FunctionToolset([execute_read, execute_write, execute_edit, execute_bash])
    # Define agent
    agent = Agent(model=model, toolsets=[coding_tools])

    # Example prompt: write a python script that prints hello world, save it to hello.py, and run it

    # Initialize chat history
    message_history = []

    # Initialize conversation with a personalized greeting message
    username = getpass.getuser()
    greeting = f"Hello {username}, how can I help you?"
    console.print(f"[blue]Assistant:[/blue] {greeting}")

    while True:
        console.print(f"[green]User:[/green] ", end="")
        user_input = console.input()
        if user_input.lower() in ['quit', 'exit']:
            console.print("[dim]Goodbye![/dim]")
            break
        
        # Run the agent with existing history
        with console.status("[dim]Thinking...[/dim]", spinner="arc"):
            result = agent.run_sync(user_input, message_history=message_history)
        
        # Update history with the new prompt output
        message_history = result.all_messages()
        console.print(f"[blue]Assistant:[/blue] {result.output}")
