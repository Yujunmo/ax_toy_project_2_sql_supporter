# 내용 : 사용자 질의에서 테이블 리스트를 추출 
# 히스토리 : Parallel Workflow, ReAct로 최초구현
# 속도이슈 발생. ReAct는 느려서 predefined workflow로 변경하고, LLM은 gpt-5.4-nano 작은 모델로 변경

from langchain_openai import  ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START,END
from pydantic import BaseModel, Field
from typing import List
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent 
import ast

LLM = ChatOpenAI(model='gpt-5.4-nano' )
#SMALL_LLM = ChatOpenAI(model='gpt-5.4-mini')
#FAST_LLM = ChatOpenAI(model='gpt-5.4-nano')

load_dotenv()

class AgentState(TypedDict):
    query : str
    branch_A_answer : List[str]
    branch_B_answer : List[str]
    verification : bool

class Table(BaseModel):
    table_name: str = Field(description="테이블 이름")

class TableList(BaseModel):
    tables: List[Table] = Field(description="테이블 목록")

def table_extract_node(state: AgentState) -> list[Table]:
    branch = state.get('branch')

    table_extract_prompt = f'''아래 [query]는 사용자 질의입니다. 질의에서 테이블 리스트를 추출해서 반환해주세요.
    테이블 이름만 추출해서 중복없이 반환해주세요. sql 문법 오류가 발견되어도 상관 없습니다.
    [query]
    {state['query']}
    '''

    result = LLM.with_structured_output(TableList).invoke(table_extract_prompt)
    
    # Table 객체 리스트 → 문자열 리스트로 변환
    return {f'branch_{branch}_answer': [table.table_name for table in result.tables]}
    

# 검증 노드
def verification_node(state:AgentState) -> AgentState:
    print('verification_node called...')
    
    print(f'branch_A_answer: {state["branch_A_answer"]}')
    print(f'branch_B_answer: {state["branch_B_answer"]}')

    return {'verification': sorted(state['branch_A_answer']) == sorted(state['branch_B_answer'])}

def router_node(state:AgentState) :
    return state['verification']

def dummy_start_node(state:AgentState)-> AgentState:
    # START 로 분기처리 안되서 더미 노드 만듦
    return state
    

# 그래프 생성
graph_builder = StateGraph(AgentState)
graph_builder.add_node('dummy_start_node', dummy_start_node)
graph_builder.add_node('table_extract_node_1', lambda state : table_extract_node({**state, 'branch':'A'}))
graph_builder.add_node('table_extract_node_2', lambda state : table_extract_node({**state, 'branch':'B'}))
graph_builder.add_node('verification_node' , verification_node)

graph_builder.add_edge(START,'dummy_start_node')
graph_builder.add_edge('dummy_start_node','table_extract_node_1')
graph_builder.add_edge('dummy_start_node','table_extract_node_2')
graph_builder.add_edge('table_extract_node_1','verification_node')
graph_builder.add_edge('table_extract_node_2','verification_node')
graph_builder.add_conditional_edges(
    'verification_node',
    router_node,
    {
        True: END,
        False: 'dummy_start_node'

    }
)

graph = graph_builder.compile()
