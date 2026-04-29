import asyncio
# nonebot
from nonebot import logger
# langchain
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
# project dependencies
from .tools import final_answer, final_answer_flag
from .prompt import agent_system_prompt
from .data_structure import StreamingMessage
from .tool_process import add_timeout_to_tool


# Supported content type for transmission
SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

# Memory saver
memory_saver = MemorySaver()

# Agent
class agent:
    def __init__(self, llm_model_name: str, llm_api_key: str, llm_base_url: str):
        # Base llm
        self.llm = ChatOpenAI(
            model=llm_model_name,
            api_key=llm_api_key,
            base_url=llm_base_url,
        )
        # MCP client
        self.mcp_client = None
        # Agent
        self.agent = None
        # Initialization management
        self.asyncio_lock = asyncio.Lock()
        self.initialized = False

    # Agent initialization
    async def initialize(self, mcp_url: str, api_key: str, tool_timeout_seconds: int=30):
        async with self.asyncio_lock:
            if self.initialized:
                return
            try:
                self.mcp_client = MultiServerMCPClient(
                    {
                        "exa": {
                            "url": mcp_url,
                            "headers": {
                                "x-api-key": api_key
                            },
                            "transport": "streamable-http",
                            "timeout": 60
                        }
                    }
                )
                # Get llm tools from mcp
                tools = await self.mcp_client.get_tools()
            except:
                logger.info("Cannot find mcp server")
                tools = []
            tools.append(final_answer)
            # Add web search tool
            self.agent = create_agent(
                self.llm,
                tools,
                checkpointer=memory_saver,
                system_prompt=agent_system_prompt
            )
            logger.info("Agent initialization finished")
            self.initialized = True

    # Test invoke
    async def test_invoke(self, prompt: str):
        logger.info("Start testing")
        # Load Messages history
        messages = []
        messages.append(HumanMessage(content=prompt))
        chat_history = {
            "messages": messages
        }
        # Invoke agent
        result = await self.agent.ainvoke(chat_history)
        return result

    # Streaming
    async def streaming(self, prompt: str, context_id: str, tool_timeout_seconds: int=30):
        logger.info("Start streaming")
        try:
            # Configuration
            config = {'configurable': {'thread_id': context_id}}
            # Setting messages
            messages = []
            messages.append(HumanMessage(content=prompt))
            chat_history = {
                "messages": messages
            }
            # Response record
            enter_final_answer = False
            async for chunk in asyncio.wait_for(
                    self.agent.astream(chat_history, config=config),
                    timeout=tool_timeout_seconds
            ):
                for step, data in chunk.items():
                    if data['messages'][0].content == final_answer_flag:
                        enter_final_answer = True
                    if not enter_final_answer:
                        yield StreamingMessage(
                            step=step,
                            content=data['messages'][0].content,
                            done=False
                        )
                    elif enter_final_answer and step == "model":
                        yield StreamingMessage(
                            step="finish",
                            content=data['messages'][0].content,
                            done=True
                        )
        except Exception as e:
            # Error handling
            logger.error(f"Error occurred while streaming: {e}")
            yield StreamingMessage(
                step="error",
                content=f"Sorry, I have encountered an error {e}",
                done=True
            )
