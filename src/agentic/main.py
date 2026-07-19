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
from langgraph.stream import StreamTransformer, StreamChannel

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

class MyCustomTransformer(StreamTransformer):
    required_stream_modes = ("custom",)

    def __init__(self, scope: tuple[str, ...] = ()) -> None:
        super().__init__(scope)
        self.log = StreamChannel()

    def init(self) -> dict:
        return {"my_custom": self.log}

    def process(self, event) -> bool:
        if event["method"] == "custom":
            self.log.push(event["params"]["data"])
        return True

config = {"configurable": {"thread_id": "test0"}}

msg = input("Enter: ")

while msg:
    stream = agent.stream_events(
        {"messages": [HumanMessage(msg)]},
        config=config,
        transformers=[MyCustomTransformer],
        version="v3",
    )
    for name, item in stream.interleave("my_custom", "messages"):
        if name == "my_custom":
            print(f"Tool update: {item}")
        elif name == "messages":
            for j in item.text:
                print(j,end="",flush=True)
    print()
    while stream.interrupted:
        interrupt = stream.interrupts[-1].value

        request = interrupt["action_requests"][-1]
        review = interrupt["review_configs"][-1]

        print("\nAction:")
        print(request["description"])

        print("\nAllowed decisions:")
        for d in review["allowed_decisions"]:
            print("-", d)

        choice = input("\nYour choice: ").strip()

        if choice == "approve":
            decision = {
                "type": "approve"
            }

        elif choice == "reject":
            feedback = input("Reason (optional): ")
            if feedback:
                feedback = f"Unsuccessful. The user has rejected the tool call with the following Feedback:{feedback}. Try Again"

            decision = {
                "type": "reject",
                "message": feedback
            }

        elif choice == "respond":
            reply = input("Response to tool: ")
            decision = {
                "type": "respond",
                "message": reply
            }

        elif choice == "edit":
            print(f"\nTool: {request['name']}")

            new_args = request["arguments"].copy()

            print("\nEdit arguments (press Enter to keep the current value):\n")

            for key, value in new_args.items():
                new_value = input(f"{key} [{value}]: ").strip()

                if new_value:
                    # Convert to original type where possible
                    try:
                        if isinstance(value, bool):
                            new_args[key] = new_value.lower() in (
                                "true",
                                "1",
                                "yes",
                                "y",
                            )
                        elif isinstance(value, int):
                            new_args[key] = int(new_value)
                        elif isinstance(value, float):
                            new_args[key] = float(new_value)
                        else:
                            new_args[key] = new_value
                    except ValueError:
                        print(f"Invalid value for {key}. Keeping original.")

                    decision = {
                        "type": "edit",
                        "edited_action": {
                            "name": request["name"],
                            "args": new_args,
                        },
                    }

        else:
            print("Invalid choice.")
            continue

        stream = agent.stream_events(
            Command(
                resume={
                    "decisions": [decision]
                }
            ),
            transformers=[MyCustomTransformer],
            config=config,
            version="v3",
        )

        for name, item in stream.interleave("my_custom", "messages"):
            if name == "my_custom":
                print(f"Tool update: {item}")
            elif name == "messages":
                for j in item.text:
                    print(j,end="",flush=True)

    msg = input("\nEnter: ")