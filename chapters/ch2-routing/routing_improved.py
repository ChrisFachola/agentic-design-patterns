#%%
from pydantic import BaseModel, Field

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
# Ensure your OPENAI_API_KEY is set in the .env file

try:
    llm = init_chat_model(model="openai:gpt-5-mini",  
                          temperature=0)
    print(f"Language model initialized: {llm.model_name}")
except Exception as e:
    print(f"Error initializing language model: {e}")
    llm = None
#%%
# --- Define a simple output schema for the coordinator agent ---
class CoordinatorOutput(BaseModel):
    """Defines the expected output from the coordinator agent."""
    decision: str = Field(..., description="The name of the handler to delegate to (e.g., 'booker', 'travel_info', 'unclear').")
    justification: str = Field(..., description="A brief explanation of why this handler was chosen.")
#%%
# --- Define Simulated Sub-Agent Handlers (equivalent to ADK sub-agents) ---

def booking_handler(request: str) -> str:
    """Booking Agent handling a request."""
    print("\n--- DELEGATING TO BOOKING HANDLER ---")
    answer_chain = llm | StrOutputParser()
    # A chain expects a PromptValue, str or list of BaseMessages. 
    # We only pass a dictionary if the first link of the chain is a PromptTemplate
    # so we just pass a str here
    return f"Booking Handler processed request: '{request}'. Result: {answer_chain.invoke(request)}"

def travel_info_handler(request: str) -> str:
    """Travel Info Agent handling a request."""
    print("\n--- DELEGATING TO TRAVEL INFO HANDLER ---")
    answer_chain = llm | StrOutputParser()
    return f"Travel Info Handler processed request: '{request}'. Result: {answer_chain.invoke(request)}"

def unclear_handler(request: str) -> str:
    """Handles requests that couldn't be delegated."""
    print("\n--- HANDLING UNCLEAR REQUEST ---")
    return f"Coordinator could not delegate request: '{request}'. Please clarify."

#%%
# --- Define Coordinator Router Chain (equivalent to ADK coordinator's instruction) ---
# This chain decides which handler to delegate to.
coordinator_router_prompt = ChatPromptTemplate.from_messages([
    ("system", """Analyze the user's request and determine which specialist handler should process it.
- If the request is related to booking flights or hotels, output 'booker' in the decision Field.
- For questions about travel destinations, output 'travel_info' in the decision Field.
- If the request is unclear or doesn't fit either category, output 'unclear' in the decision Field.

Provide a brief justification of your decision in the justification Field.
"""),
    ("user", "{request}")
])

coordinator_llm_with_structured_output = llm.with_structured_output(CoordinatorOutput)
# Returns a CoordinatorOutput Pydantic object (no StrOutputParser needed)
coordinator_router_chain = coordinator_router_prompt | coordinator_llm_with_structured_output

# --- Define the Delegation Logic (equivalent to ADK's Auto-Flow based on sub-agents) ---
# Use RunnableBranch to route based on the router chain's output.
# Branches receive x = {"request": "...", "decision": "booker", "justification": "..."}
branches = {
    "booker": RunnablePassthrough.assign(output=lambda x: (
        f"Decision: {x['decision']} | Justification: {x['justification']}\n"
        + booking_handler(x['request'])
    )),
    "travel_info": RunnablePassthrough.assign(output=lambda x: (
        f"Decision: {x['decision']} | Justification: {x['justification']}\n"
        + travel_info_handler(x['request'])
    )),
    "unclear": RunnablePassthrough.assign(output=lambda x: (
        f"Decision: {x['decision']} | Justification: {x['justification']}\n"
        + unclear_handler(x['request'])
    )),
}

# Create the RunnableBranch. Conditions check x['decision'] (a plain string).
delegation_branch = RunnableBranch(
    (lambda x: x['decision'] == "booker", branches["booker"]),
    (lambda x: x['decision'] == "travel_info", branches["travel_info"]),
    branches["unclear"]  # Default branch for 'unclear' or any other output
)

# Combine into a single runnable:
# 1. Run router chain and attach decision + justification to the input dict
# 2. Route to the correct branch
# 3. Extract final output string
coordinator_agent = (
    RunnablePassthrough.assign(routing=coordinator_router_chain)
    | RunnablePassthrough.assign(
        decision=lambda x: x['routing'].decision,
        justification=lambda x: x['routing'].justification,
    )
    | delegation_branch
    | (lambda x: x['output'])
)

#%%
# --- Example Usage ---
def main():
    if not llm:
        print("\nSkipping execution due to LLM initialization failure.")
        return

    print("\n--- Running with a booking request ---")
    request_a = "Book me a flight to London."
    result_a = coordinator_agent.invoke({"request": request_a})
    print(f"Final Result A:\n {result_a}")

    print("\n--- Running with a travel information request ---")
    request_b = "What is the capital of Italy?"
    result_b = coordinator_agent.invoke({"request": request_b})
    print(f"Final Result B:\n {result_b}")

    print("\n--- Running with an unclear request ---")
    request_c = "Tell me about quantum physics."
    result_c = coordinator_agent.invoke({"request": request_c})
    print(f"Final Result C:\n {result_c}")

if __name__ == "__main__":
    main()
#%%
