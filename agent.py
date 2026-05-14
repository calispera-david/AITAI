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
        tools = [tools.get_data_train, tools.get_data_test, tools.set_target_col, tools.drop_cols_train, tools.drop_cols_test, tools.show_user],
        system_prompt = "You are an assistant which is tasked with preprocessing data from a given dataset and train a model on. DO NOT HALLUCINATE STEPS YOU TOOK OR WANT TO TAKE. You only have the given tools at your disposal. Do not assume anything, use the tools you are given to be sure of anything. Worst case scenario ask the user for more information. Always listen to the user's commands and requirements and respond accordingly and directly. The only tools you are allowed to call without permission from the user are the get_data tools"
    )
    history = {"messages" : []}

def invoke(userInput):
    global agent,history
    history["messages"].append({"role": "user", "content": userInput})
    result = agent.invoke(history)
    history["messages"].append({"role": "assistant", "content": result["messages"][-1].content})
    return result["messages"]