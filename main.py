from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END, START

from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

load_dotenv()

gen_model = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite')
model = ChatGoogleGenerativeAI(model='gemini-2.5-pro')

# define the state
import operator
from typing import TypedDict, Annotated, List

class agentState(TypedDict):
    user_scenario : str
    gen_poem : Annotated[List[str], operator.add]

    iteration : int
    gen_score : Annotated[List[int], operator.add]
    feedback : Annotated[List[str], operator.add]


from pydantic import BaseModel, Field
from typing import Literal

class poemSchema(BaseModel):
    feedback : str = Field(description="This indicates the things that needs to be improved in the poem")
    score : int = Field(description="The score is generated based on the poem's content out of 10")

pyparser = PydanticOutputParser(pydantic_object=poemSchema)

# define the functions
generator_prompt = PromptTemplate(
    template= """
        your a famous, professional and trained poet (typically writes a whole poem in 15-20 lines).
        just return the poem no need to add anything.
        based on the given scenario write a meaningfull poem by mentiong the tone at the end of each sentence in a braces
                for example :   Eighteen seasons, a desert of hope, (a sigh escaped).
                                Dust motes danced on a screen, a silent scope, (my heart ached).
                                Each near miss a phantom, a cruel, echoing jest, (despair lingered).
                                Then the final whistle, put my soul to the test, (anxiety tightened).
                                The scoreboard flashed, a blinding, glorious light, (a gasp escaped). 

        scenario -> {scenario}
    """,
    input_variables= ['scenario']
)
def generator(state : agentState):
    print("entering generator")
    input = state['user_scenario']
    chain = generator_prompt | gen_model
    response = chain.invoke({
        "scenario" : input
    })
    return {'gen_poem':[response.content], 'iteration' : 1}

import time
evaluator_prompt = PromptTemplate(
    template= """
        you are an excellent poem evaluator.
        you are strict evaluator who gives low score only at first iteration ,inorder to make sure that the iterations may lead to better version of it
        you evaluate the poems by considering common/simple(daily conversation words) words used, human emotions, rhyming, and the simplicity in the poem.
        you belive that more the simple words used in the poem and more the emotion showed in the poem makes it valuable and great poem.

        you evaluate the poem's based on the scenario and the generated poem.the below provides with poem and scenario.
        scenario -> {scenario},
        iteration -> {iteration},
        poem -> {poem}\n\n,

        {format}
    """,
    input_variables= ['scenario', 'poem', 'iteration'],
    partial_variables= {
        'format' : pyparser.get_format_instructions()
    }
)

def evaluator(state : agentState):
    time.sleep(15)
    print(f"entering valuator loop {state['iteration']}")
    scenario = state['user_scenario']
    poem = state['gen_poem']

    chain = evaluator_prompt | model | pyparser
    response = chain.invoke({
        "scenario" : scenario,
        "poem" : poem,
        'iteration' : state['iteration']
    })
    print(f"-----------score : {response.score}")
    return {'feedback' : [response.feedback], 'gen_score' : [response.score]} 

optimizer_prompt = PromptTemplate(
    template= """
        you are an excellent at re-writting the poem based on the feedback, 
        you always keep the tone as it is before usually tones are mentioned in the braces, check the below example
          example : Eighteen seasons, a desert of hope, (a sigh escaped). 
                    Dust motes danced on a screen, a silent scope, (my heart ached).
                    Each near miss a phantom, a cruel, echoing jest, (despair lingered).
                    Then the final whistle, put my soul to the test, (anxiety tightened).
                    The scoreboard flashed, a blinding, glorious light, (a gasp escaped). 
            in the above example the tone are : (a sigh escaped), (my heart ached), (despair lingered), (anxiety tightened), (a gasp escaped).

        you always tries to improve the poem without altering the context and tone of the already written poem and always return the tone as it is within the brackets as itis.
        you just tweaks a little bit based on the feedback.
        just give poem no need to add anything.
        
        the below are the available poem and the feedback :\n
        poem -> {poem}\n
        feedback -> {feedback}
    """,
    input_variables= ['poem', 'feedback']
)

def optimizer(state : agentState):
    print("entering optimizer")
    chain = optimizer_prompt | gen_model
    response = chain.invoke({
        "poem" : state['gen_poem'],
        "feedback" : state['feedback']
    })
    
    return {'gen_poem': [response.content], 'iteration' : state['iteration']+1}

def score_route(state : agentState) -> Literal["optimizer", END]:
    if state['gen_score'][-1] >= 7 or state['iteration'] >= 5:
        return END
    else:
        return "optimizer"
    
# define the graph
graph = StateGraph(agentState)

# define nodes
graph.add_node("generator", generator)
graph.add_node("evaluator", evaluator)
graph.add_node("optimizer", optimizer)

# define node edges
graph.add_edge(START, "generator")
graph.add_edge("generator", "evaluator")
graph.add_conditional_edges("evaluator", score_route)
graph.add_edge("optimizer", "evaluator")
graph.add_edge("evaluator", END)

# compile graph
workflow = graph.compile()

initial_state = {
    "user_scenario" : "My fav cricket club won the trophy for the first time in 18 seasons, i'm literally full of tears"
}

final_state = workflow.invoke(initial_state)

print(final_state)