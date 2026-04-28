from .prompt import final_answer_description
# langchain
from langchain.tools import tool

final_answer_flag = "Tool-calling session finished"


# Get final answer.
@tool("final_answer", description=final_answer_description)
async def final_answer() -> str:
    return final_answer_flag
