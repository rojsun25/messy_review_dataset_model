from dataclasses import dataclass
from typing import Dict, List, Optional

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

from src_agents.agent_context import Context, PipelineState
from src_agents.agent_tools_ingest import ingest_latest
from src_agents.agent_tools_clean import clean
from src_agents.agent_tools_transform import transform
from src_agents.agent_tools_save import save


SYSTEM_PROMPT = """You are a Databricks pipeline orchestration agent.

Process: model training dataset

You MUST execute tools strictly in this order:
1) ingest_latest
2) clean
3) transform
4) save

Do not skip steps.
"""


@dataclass
class ResponseFormat:
    process_name: str
    parameters_used: Dict[str, str]
    steps_taken: List[str]
    output_location: Optional[str]


model = init_chat_model("claude-sonnet-4-5-20250929", temperature=0)
checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[ingest_latest, clean, transform, save],
    context_schema=Context,
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer,
)

context = Context(
    user_id="1",
    input_folder=dbutils.widgets.get("input_file_path"),
    raw_folder=dbutils.widgets.get("raw_file_path"),
    output_folder=dbutils.widgets.get("output_file_path"),
)

state = PipelineState()
config = {"configurable": {"thread_id": "model_training_dataset_v1"}}

response = agent.invoke(
    {
        "messages": [{"role": "user", "content": "Build the model training dataset"}],
        "state": state,
    },
    config=config,
    context=context,
)

print(response["structured_response"])
