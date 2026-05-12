import agent

agent.initAgent()
userInput = input("User: ")
while(not userInput == ""):
    answers = agent.invoke(userInput)
    print("AGENT: ",answers[-1].content)
    userInput = input("User: ")