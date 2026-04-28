from .prompt import final_answer_description
# langchain
from langchain.tools import tool


# Get final answer.
@tool("final_answer", description=final_answer_description)
async def final_answer() -> None:
    return None
