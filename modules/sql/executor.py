import sqlite3
import os
from typing import Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data_migration.db')

def execute_sql(sql: str) -> Tuple[bool, str, int]:
    """
    SQL 문을 실행하고 결과를 반환

    Args:
        sql: 실행할 SQL 문

    Returns:
        (성공 여부, 메시지, 영향받은 행 수)
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # SQL 실행
        cursor.execute(sql)
        conn.commit()

        # 영향받은 행 수 가져오기
        affected_rows = cursor.rowcount

        # 성공 메시지
        message = f"SQL 실행 완료 (영향받은 행: {affected_rows})"
        return True, message, affected_rows

    except Exception as e:
        error_message = f"SQL 실행 오류: {str(e)}"
        return False, error_message, 0

    finally:
        if conn:
            conn.close()


def execute_multiple_statements(sql: str) -> Tuple[bool, str, int]:
    """
    여러 SQL 문을 실행 (DELETE와 INSERT 등)

    Args:
        sql: 실행할 SQL 문 (여러 문장 포함 가능)

    Returns:
        (성공 여부, 메시지, 영향받은 행 수)
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        total_rows = 0

        # SQL을 `;`로 분리
        statements = [s.strip() for s in sql.split(';') if s.strip()]

        for statement in statements:
            cursor.execute(statement)
            total_rows += cursor.rowcount

        conn.commit()

        # 성공 메시지
        message = f"SQL 실행 완료 (총 영향받은 행: {total_rows})"
        return True, message, total_rows

    except Exception as e:
        error_message = f"SQL 실행 오류: {str(e)}"
        return False, error_message, 0

    finally:
        if conn:
            conn.close()
