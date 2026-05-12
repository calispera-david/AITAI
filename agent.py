# AGENT MODULE

import tools
from langchain.agents import create_agent
from langchain_ollama import ChatOllama

agent = 0
history = 0
def initAgent():
    global agent, history
    agent = create_agent(
        model = ChatOllama(model = "llama3.2"),
        tools = [tools.get_data],
        system_prompt = "You are an assistant which is tasked with preprocessing data from a given dataset. You currently have no tools to do that, only to retrieve data from the file. DO NOT HALLUCINATE STEPS YOU TOOK. You only have the given tools at your disposal. Do not assume anything, use the tools you are given to be sure of anything. Worst case scenario ask the user for more information"
    )
    history = {"messages" : []}

def invoke(userInput):
    global agent,history
    history["messages"].append({"role": "user", "content": userInput})
    result = agent.invoke(history)
    history["messages"].append({"role": "assistant", "content": result["messages"][-1].content})
    return result["messages"]