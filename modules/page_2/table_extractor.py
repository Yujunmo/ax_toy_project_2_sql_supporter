# 내용 : 사용자 질의에서 테이블 리스트를 추출 
# 구현 : Parallel Workflow, ReAct 

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

LLM = ChatOpenAI(model='gpt-5.4' )
SMALL_LLM = ChatOpenAI(model='gpt-5.4-mini')

load_dotenv()

class AgentState(TypedDict):
    query : str
    branch_A_answer : List[str]
    branch_B_answer : List[str]
    verification : bool

# 도구
# 1. sql인지 검증하는 도구
# 2. sql을 추출하는 도구
# 2. slq에서 테이블을 추출하는 도구

# 병렬 처리후 ,결과값 비교 후. 같으면 통과 안같으면 재작업

@tool
def chk_query(query:str)->bool:
    '''주어진 query에 sql이 포함되어 있는지 여부를 반환'''
    print(f'chk_query called with {query}')
    class YN(BaseModel):
        yn : bool = Field("True or False")

    chk_query_prompt = f'''아래 [query]는 사용자 질의입니다.
    질의에 데이터베이스 sql이 포함되어 있는지 체크해주세요. sql 문법 오류가 발견되어도 상관 없습니다.
    포함되어 있다면 True를 없다면 False를 반환해주세요.

    [query]
    {query}
    '''

    return LLM.with_structured_output(YN).invoke(chk_query_prompt).yn


@tool
def extract_sql(query:str)->str:
    '''주어진 query에서 sql을 추출하여 반환'''
    print(f'extract_sql called with {query}' )
    class Sql(BaseModel):
        sql : bool = Field("sql")

    query_extract_prompt = f'''아래 [query]는 사용자 질의입니다.
    질의에서 sql을 추출해주세요. sql 문법 오류가 발견되어도 상관 없습니다.

    [query]
    {query}
    '''

    return LLM.with_structured_output(Sql).invoke(query_extract_prompt).sql

@tool
def extract_tables(sql: str) -> list[str]:
    '''주어진 sql에서 테이블 리스트를 추출하여 반환'''
    print(f'extract_tables called with {sql}' )

    class Table(BaseModel):
        table_name: str = Field(description="테이블 이름")

    class TableList(BaseModel):
        tables: List[Table] = Field(description="테이블 목록")

    table_extract_prompt = f'''아래 [sql]는 사용자 질의입니다.

    [sql]
    {sql}
    '''

    result = LLM.with_structured_output(TableList).invoke(table_extract_prompt)
    
    # Table 객체 리스트 → 문자열 리스트로 변환
    return [table.table_name for table in result.tables]


# 노드 정의 
def table_extract_node(state:AgentState) -> AgentState:
    print('table_extract_node called...')
    branch = state.get('branch')

    table_extract_tools = [chk_query, extract_sql, extract_tables]
    table_extract_agent = create_react_agent(
        LLM,
        tools = table_extract_tools
    )

    persona = {"role":"system", "content" : '당신은 사용자의 질의에서 테이블 리스트를 추출하는 역할을 맡고 있습니다.\
             사용자 질의에서 sql 이 발견된다면, 테이블 리스트를 중복없이 추출하세요. 없으면 빈 리스트를 반환하세요.'}
    state['messages'] = [persona] + [HumanMessage(content=state['query'])]

    result = table_extract_agent.invoke(state)

    return {f'branch_{branch}_answer': result['messages'][-1].content}

# 검증 노드
def verification_node(state:AgentState) -> AgentState:
    print('verification_node called...')
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
