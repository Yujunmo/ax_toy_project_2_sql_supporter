# 내용 : 입력 받은 쿼리에 db link 를 반영
# 구현 : predefiend workflow, adaptive agent 
# 히스토리 : db link 주입기 페이지 자유도는 높지만 속도가 느림.
# 이번 페이지는 다소 기능은 제한되지만 속도감 개선

from langchain_openai import  ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START,END
from pydantic import BaseModel, Field
from typing import List
from modules.agents.table_extractor import graph as table_list_extractor
import streamlit as st
#load_dotenv()

LLM = ChatOpenAI(model='gpt-5.4' , api_key = st.secrets["OPENAI_API_KEY"])
SMALL_LLM = ChatOpenAI(model='gpt-5.4-mini', api_key = st.secrets["OPENAI_API_KEY"])

class AgentState(TypedDict):
    router_result : Literal['LLM', 'sql']
    db_link : str
    sql : str
    table_list : List[str]
    answer : str

class RouteType(BaseModel):
    target: Literal['sql', 'LLM'] = Field(description='The target for the query to answer')


def router(state:AgentState) -> Literal['LLM','sql']:

    structured_router_LLM = SMALL_LLM.with_structured_output(RouteType)

    router_system_prompt = """
    Your are an expert at routing a user's question to 'sql' or 'LLM'.
    if you think the question is not related to sql, route to LLM.
    """

    router_prompt = ChatPromptTemplate.from_messages(
        [
            ('system',router_system_prompt), # 페르소나, 역할 
            ('user',f" {{sql}}") # 인풋 변수
        ]
    )

    router_chain = router_prompt | structured_router_LLM 
    rs_route = router_chain.invoke({'sql': state['sql']})

    print(f"{rs_route=}")
    return rs_route.target

def call_LLM(state:AgentState) -> AgentState:
    # sql 반영과 관련 없는 질의 처리 노드 
    print("call_LLM called")
    
    user_request = '아래 요청내용이 sql에 db link를 반영하는 것과 관련이 없으면, 관련해서 다시 질문해달라고 요청해주세요.\
        별도로 사용자에게 추가로 무언가를 해주겠다고 제안하지 마세요.'
    user_request += state['sql'] + " " + state['db_link']
    
    answer = LLM.invoke(user_request)
        
    return {'answer' : answer.content , 'router_result' : "LLM"} 



def table_name_extractor(state:AgentState) -> AgentState:
    # 테이블 리스트 추출하는 노드
    print("table_name_extractor called")

    result = table_list_extractor.invoke({'query' : state['sql']})
    return {'table_list' : result['branch_A_answer'], 'router_result' : "LINK_INSERTER" }


def db_link_inserter(state:AgentState) -> AgentState:
    # 링크 주입 노드
    print("db_link_inserter called")

    # 사용자가 입력한 db link가 '@'로 시작하지 않으면 붙여주기
    if '@' not in state.get('db_link'):
        state['db_link'] = '@' + state.get('db_link')


    state['answer'] = state['sql']
    for table in state['table_list']:
        state['answer'] = state['answer'].replace(table, f"{table} {state['db_link']}")
    
    return {'answer' : state['answer']}


graph_builder = StateGraph(AgentState)

graph_builder.add_node('call_LLM',call_LLM)
graph_builder.add_node('table_name_extractor', table_name_extractor)
graph_builder.add_node('db_link_inserter',db_link_inserter)
graph_builder.add_conditional_edges(
    START,
    router,
    {
        'LLM':'call_LLM',
        'sql' : 'table_name_extractor',
    }
)
graph_builder.add_edge('table_name_extractor','db_link_inserter')
graph_builder.add_edge('db_link_inserter', END)

graph = graph_builder.compile()