from langchain.agents import create_agent
from langchain.messages import HumanMessage, ToolMessage
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from .tools import NOTEBOT_TOOLS
from dotenv import load_dotenv
from langchain.agents.middleware import HumanInTheLoopMiddleware, wrap_tool_call, ToolCallRequest, ToolRetryMiddleware
from collections.abc import Callable
from langgraph.types import Command
import warnings
warnings.filterwarnings("ignore",message=".*streaming protocol.*")

load_dotenv()

@wrap_tool_call
def log_tool(request: ToolCallRequest, handler: Callable[[ToolCallRequest], ToolMessage | Command],) -> ToolMessage | Command:
    print(f"Executing tool: {request.tool_call['name']}")
    print(f"Arguments: {request.tool_call['args']}")
    try:
        result = handler(request)
        print(f"Tool result:{result.content[:40]}...")
        return result
    except Exception as e:
        print(f"Tool failed: {e}")
        raise

model = ChatOllama(
    model="qwen3.5:4b-mlx",
    reasoning=False,
    temperature=0.0,
    top_p=0.5
)

agent = create_agent(
    model=model,
    system_prompt="You are a NoteBot",
    tools=NOTEBOT_TOOLS,
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                'save_note':True,
                'delete_note':{
                    "allowed_decisions":['approve','reject']
                }
            }
        ),
        ToolRetryMiddleware(
            max_retries=9,
            backoff_factor=1.1
        ),
        log_tool,
    ]
)

config = {"configurable": {"thread_id": "test0"}}
msg=input("Enter: ")
while(msg):
    res = agent.stream_events({"messages":[HumanMessage(msg)]},version='v3',config=config)
    for message in res.messages:
        for chunk in message.text:
            print(chunk,end="",flush=True)
    if res.interrupted:
        print(res.interrupts[-1].value['action_requests'][-1]['description'])
        print("\n")
    msg=input("\nEnter: ")
