from typing import List, Dict, Optional, Tuple
from modules.db.manager import get_table_pk_columns


def build_where_clause(
    table_name: str,
    mncm_code: str,
    fund_code: str,
    itms_code: str,
    start_date: str,
    end_date: str
) -> str:
    """
    테이블의 PK와 입력값을 매칭하여 WHERE 조건 동적 생성

    Args:
        table_name: 원본 테이블명
        mncm_code: 운용사코드
        fund_code: 펀드코드
        itms_code: 종목코드
        start_date: 시작일자 (YYYYMMDD)
        end_date: 종료일자 (YYYYMMDD)

    Returns:
        WHERE 조건 문자열
    """
    # 테이블의 PK 컬럼 조회
    pk_columns = get_table_pk_columns(table_name)

    # 입력값 맵핑
    input_values = {
        'mncm_code': mncm_code if mncm_code else None,
        'fund_code': fund_code if fund_code else None,
        'itms_code': itms_code if itms_code and itms_code.strip() else None,
        'proc_date': (start_date, end_date) if start_date and end_date else None
    }

    where_conditions = []

    for pk_col in pk_columns:
        if pk_col == 'proc_date' and input_values['proc_date']:
            start, end = input_values['proc_date']
            where_conditions.append(f"proc_date BETWEEN '{start}' AND '{end}'")
        elif pk_col in input_values and input_values[pk_col]:
            where_conditions.append(f"{pk_col} = '{input_values[pk_col]}'")

    return " AND ".join(where_conditions) if where_conditions else "1=1"


def generate_sql_statements(
    extracted_tables: List[str],
    mncm_code: str,
    fund_code: str,
    itms_code: str,
    start_date: str,
    end_date: str
) -> List[Dict[str, str]]:
    """
    추출된 테이블 기반으로 DELETE/INSERT SQL 자동 생성
    테이블별 PK 스키마를 참고하여 동적으로 WHERE 조건 생성

    Args:
        extracted_tables: 추출된 테이블 목록
        mncm_code: 운용사코드
        fund_code: 펀드코드
        itms_code: 종목코드 (선택사항)
        start_date: 시작일자 (YYYYMMDD)
        end_date: 종료일자 (YYYYMMDD)

    Returns:
        각 테이블별 DELETE/INSERT SQL이 포함된 딕셔너리 리스트
    """
    sql_list = []

    for table in extracted_tables:
        # 타겟 테이블명 (원본_t)
        target_table = f"{table}_t"

        # WHERE 조건 동적 생성 (테이블 스키마 기반)
        where_clause = build_where_clause(
            table_name=table,
            mncm_code=mncm_code,
            fund_code=fund_code,
            itms_code=itms_code,
            start_date=start_date,
            end_date=end_date
        )

        # DELETE SQL 생성
        delete_sql = f"""DELETE FROM {target_table}
WHERE {where_clause};"""

        # INSERT SQL 생성
        insert_sql = f"""INSERT INTO {target_table}
SELECT * FROM {table}
WHERE {where_clause};"""

        sql_list.append({
            'table_name': table,
            'target_table': target_table,
            'delete_sql': delete_sql,
            'insert_sql': insert_sql
        })
    return sql_list


def format_sql_for_display(sql_statements: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Display용으로 SQL 문을 포맷팅

    Args:
        sql_statements: generate_sql_statements에서 반환된 결과

    Returns:
        Display 용도로 포맷팅된 데이터
    """
    display_list = []

    for stmt in sql_statements:
        display_list.append({
            '테이블': stmt['table_name'],
            '타겟': stmt['target_table'],
            'DELETE 문': stmt['delete_sql'],
            'INSERT 문': stmt['insert_sql']
        })

    return display_list
