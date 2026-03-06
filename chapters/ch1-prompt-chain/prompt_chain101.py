#%%
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# For better security, load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

# Make sure your OPENAI_API_KEY is set in the .env file
#%%
# Initialize the Language Model (using ChatOpenAI is recommended)
llm = ChatOpenAI(
    model="gpt-5-nano",
    # stream_usage=True,
    # temperature=None,
    # max_tokens=None,
    # timeout=None,
    # reasoning_effort="low",
    # max_retries=2,
    # api_key="...",  # If you prefer to pass api key in directly
    # base_url="...",
    # organization="...",
    # other params...
)
# --- Prompt 1: Extract Information ---
prompt_extract = ChatPromptTemplate.from_template(
    "Extract the technical specifications from the following text:\n\n{text_input}"
)

# --- Prompt 2: Transform to JSON ---
prompt_transform = ChatPromptTemplate.from_template(
    "Transform the following specifications into a JSON object with "
    "'cpu', 'memory', and 'storage' as keys:\n\n{specifications}"
)

# --- Build the Chain using LCEL (LangcChain Expression Language) ---
# The StrOutputParser() converts the LLM's message output to a simple string.
# The | operator is LCEL's pipe — it chains components so each output becomes the next input:
extraction_chain = prompt_extract | llm | StrOutputParser()

# The full chain passes the output of the extraction chain into the 'specifications'
# variable for the transformation prompt.
full_chain = (
    {"specifications": extraction_chain}
    | prompt_transform
    | llm
    | StrOutputParser()
)
# %%
# --- Run the Chain ---
text_input = "The new laptop model features a 3.5 GHz octa-core processor, 16GB of RAM, and a 1TB NVMe SSD."

# Execute the chain with the input text dictionary.
final_result = full_chain.invoke({"text_input": text_input})

print("\n--- Final JSON Output ---")
print(final_result)
# %%
# alternative, simple chain
simple_chain = prompt_extract | llm
simple_result = simple_chain.invoke({"text_input": text_input})
print("Simple result without parsing:", simple_result)
# %%
print("Simple result parsed:", (simple_chain | StrOutputParser()).invoke({"text_input": text_input}))
# %%
# we can also make the chain a bit more modular
extraction_chain = prompt_extract | llm | StrOutputParser()
transformation_chain = prompt_transform | llm | StrOutputParser()
# The full chain passes the output of the extraction chain into the 'specifications'
# variable for the transformation prompt.
full_chain = (
    {"specifications": extraction_chain}
    | transformation_chain
)
final_result = full_chain.invoke({"text_input": text_input})
print("\n--- Final JSON Output (modular) ---")
print(final_result)
# %%
