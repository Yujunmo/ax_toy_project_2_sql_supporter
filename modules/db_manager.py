import sqlite3
import os
from typing import List, Dict, Optional
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data_migration.db')

def init_db():
    """SQLite 데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 마이그레이션 작업 기록 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS migration_jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_sql TEXT NOT NULL,
            extracted_tables TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            notes TEXT
        )
    ''')

    # 마이그레이션 상세 정보 테이블 (각 테이블별 이관 내역)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS migration_details (
            detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            table_name TEXT NOT NULL,
            delete_sql TEXT,
            insert_sql TEXT,
            executed_at TIMESTAMP,
            execution_status TEXT DEFAULT 'pending',
            affected_rows INTEGER,
            error_message TEXT,
            FOREIGN KEY (job_id) REFERENCES migration_jobs(job_id)
        )
    ''')

    # 데이터 검증 결과 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS migration_validation (
            validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            table_name TEXT NOT NULL,
            source_count INTEGER,
            target_count INTEGER,
            validation_passed BOOLEAN,
            validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES migration_jobs(job_id)
        )
    ''')

    # 포트폴리오 주식 마스터 정보
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pfo_stck_ma (
            mncm_code TEXT NOT NULL,
            proc_date TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            itms_code TEXT NOT NULL,
            itms_name TEXT,
            hold_qty REAL,
            avg_buy_price REAL,
            close_price REAL,
            eval_amt REAL,
            buy_amt REAL,
            profit_loss REAL,
            currency_code TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, proc_date, fund_code, itms_code)
        )
    ''')

    # 포트폴리오 펀드 정보 히스토리
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pfo_fund_infr_ht (
            mncm_code TEXT NOT NULL,
            proc_date TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            fund_name TEXT,
            fund_type TEXT,
            fund_status TEXT,
            setting_date TEXT,
            maturity_date TEXT,
            nav_amt REAL,
            base_price REAL,
            currency_code TEXT,
            manager_id TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, proc_date, fund_code)
        )
    ''')

    # 이관 대상 테이블: 포트폴리오 주식 마스터 (타겟)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pfo_stck_ma_t (
            mncm_code TEXT NOT NULL,
            proc_date TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            itms_code TEXT NOT NULL,
            itms_name TEXT,
            hold_qty REAL,
            avg_buy_price REAL,
            close_price REAL,
            eval_amt REAL,
            buy_amt REAL,
            profit_loss REAL,
            currency_code TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, proc_date, fund_code, itms_code)
        )
    ''')

    # 이관 대상 테이블: 포트폴리오 펀드 정보 히스토리 (타겟)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pfo_fund_infr_ht_t (
            mncm_code TEXT NOT NULL,
            proc_date TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            fund_name TEXT,
            fund_type TEXT,
            fund_status TEXT,
            setting_date TEXT,
            maturity_date TEXT,
            nav_amt REAL,
            base_price REAL,
            currency_code TEXT,
            manager_id TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, proc_date, fund_code)
        )
    ''')

    # 분류 수익률 및 기준가 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pfo_clfd_revs_stpr_ma (
            mncm_code TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            proc_date TEXT NOT NULL,
            revs_stpr REAL,
            bm_stpr REAL,
            rnrt REAL,
            bm_rnrt REAL,
            currency_code TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, fund_code, proc_date)
        )
    ''')

    # 분류 MIP 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pfo_clfd_mip_ma (
            mncm_code TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            proc_date TEXT NOT NULL,
            nav_amt REAL,
            prdy_nav_amt REAL,
            tast_amt REAL,
            debt_amt REAL,
            cash_amt REAL,
            stock_amt REAL,
            currency_code TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, fund_code, proc_date)
        )
    ''')

    # 신탁 펀드 정보 기본정보
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tru_fund_infr_bs (
            mncm_code TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            fund_name TEXT,
            firt_stup_date TEXT,
            trm_date TEXT,
            trmt_dncd TEXT,
            trst_dncd TEXT,
            fund_type TEXT,
            currency_code TEXT,
            manager_id TEXT,
            risk_grade TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, fund_code)
        )
    ''')

    # 신탁 종목 히스토리
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tru_stck_itms_ht (
            proc_date TEXT NOT NULL,
            itms_code TEXT NOT NULL,
            itms_name TEXT,
            prdy_acqs_amt REAL,
            prdy_hold_stcn REAL,
            incr_acqs_amt REAL,
            dcrs_acqs_amt REAL,
            incr_stcn REAL,
            dcrs_stcn REAL,
            close_price REAL,
            hold_qty REAL,
            eval_amt REAL,
            upd_dtm TEXT,
            PRIMARY KEY (proc_date, itms_code)
        )
    ''')

    # 이관 대상 테이블: 분류 수익률 및 기준가 (타겟)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pfo_clfd_revs_stpr_ma_t (
            mncm_code TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            proc_date TEXT NOT NULL,
            revs_stpr REAL,
            bm_stpr REAL,
            rnrt REAL,
            bm_rnrt REAL,
            currency_code TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, fund_code, proc_date)
        )
    ''')

    # 이관 대상 테이블: 분류 MIP 마스터 (타겟)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pfo_clfd_mip_ma_t (
            mncm_code TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            proc_date TEXT NOT NULL,
            nav_amt REAL,
            prdy_nav_amt REAL,
            tast_amt REAL,
            debt_amt REAL,
            cash_amt REAL,
            stock_amt REAL,
            currency_code TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, fund_code, proc_date)
        )
    ''')

    # 이관 대상 테이블: 신탁 펀드 정보 기본정보 (타겟)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tru_fund_infr_bs_t (
            mncm_code TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            fund_name TEXT,
            firt_stup_date TEXT,
            trm_date TEXT,
            trmt_dncd TEXT,
            trst_dncd TEXT,
            fund_type TEXT,
            currency_code TEXT,
            manager_id TEXT,
            risk_grade TEXT,
            upd_dtm TEXT,
            PRIMARY KEY (mncm_code, fund_code)
        )
    ''')

    # 이관 대상 테이블: 신탁 종목 히스토리 (타겟)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tru_stck_itms_ht_t (
            proc_date TEXT NOT NULL,
            itms_code TEXT NOT NULL,
            itms_name TEXT,
            prdy_acqs_amt REAL,
            prdy_hold_stcn REAL,
            incr_acqs_amt REAL,
            dcrs_acqs_amt REAL,
            incr_stcn REAL,
            dcrs_stcn REAL,
            close_price REAL,
            hold_qty REAL,
            eval_amt REAL,
            upd_dtm TEXT,
            PRIMARY KEY (proc_date, itms_code)
        )
    ''')

    conn.commit()
    conn.close()

def create_migration_job(source_sql: str, extracted_tables: List[str]) -> int:
    """새로운 마이그레이션 작업 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables_json = json.dumps(extracted_tables)
    cursor.execute('''
        INSERT INTO migration_jobs (source_sql, extracted_tables)
        VALUES (?, ?)
    ''', (source_sql, tables_json))

    job_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return job_id

def get_migration_job(job_id: int) -> Optional[Dict]:
    """마이그레이션 작업 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM migration_jobs WHERE job_id = ?', (job_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None

def list_migration_jobs(limit: int = 10) -> List[Dict]:
    """최근 마이그레이션 작업 목록 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM migration_jobs
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def add_migration_detail(job_id: int, table_name: str, delete_sql: str = None, insert_sql: str = None) -> int:
    """마이그레이션 상세 정보 추가"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO migration_details (job_id, table_name, delete_sql, insert_sql)
        VALUES (?, ?, ?, ?)
    ''', (job_id, table_name, delete_sql, insert_sql))

    detail_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return detail_id

def update_migration_detail_status(detail_id: int, status: str, affected_rows: int = None, error_msg: str = None):
    """마이그레이션 상세 정보 상태 업데이트"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE migration_details
        SET execution_status = ?, executed_at = CURRENT_TIMESTAMP, affected_rows = ?, error_message = ?
        WHERE detail_id = ?
    ''', (status, affected_rows, error_msg, detail_id))

    conn.commit()
    conn.close()

def update_migration_job_status(job_id: int, status: str, notes: str = None):
    """마이그레이션 작업 상태 업데이트"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE migration_jobs
        SET status = ?, notes = ?
        WHERE job_id = ?
    ''', (status, notes, job_id))

    conn.commit()
    conn.close()

def get_migration_details(job_id: int) -> List[Dict]:
    """특정 작업의 마이그레이션 상세 정보 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM migration_details
        WHERE job_id = ?
        ORDER BY table_name
    ''', (job_id,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def add_validation_result(job_id: int, table_name: str, source_count: int, target_count: int, passed: bool):
    """검증 결과 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO migration_validation (job_id, table_name, source_count, target_count, validation_passed)
        VALUES (?, ?, ?, ?, ?)
    ''', (job_id, table_name, source_count, target_count, passed))

    conn.commit()
    conn.close()

def get_validation_results(job_id: int) -> List[Dict]:
    """검증 결과 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM migration_validation
        WHERE job_id = ?
        ORDER BY table_name
    ''', (job_id,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def query_table(table_name: str, limit: int = 5) -> tuple[List[Dict], str]:
    """테이블 데이터 조회 (SQL injection 방지 위해 테이블명은 화이트리스트 검증)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    allowed_tables = [
        'pfo_stck_ma',
        'pfo_fund_infr_ht',
        'pfo_stck_ma_t',
        'pfo_fund_infr_ht_t',
        'pfo_clfd_revs_stpr_ma',
        'pfo_clfd_mip_ma',
        'pfo_clfd_revs_stpr_ma_t',
        'pfo_clfd_mip_ma_t',
        'tru_fund_infr_bs',
        'tru_fund_infr_bs_t',
        'tru_stck_itms_ht',
        'tru_stck_itms_ht_t'
    ]

    if table_name not in allowed_tables:
        return [], f"테이블 '{table_name}'은 조회할 수 없습니다."

    try:
        cursor.execute(f'SELECT * FROM {table_name} ORDER BY 1 DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows], ""
    except Exception as e:
        conn.close()
        return [], f"조회 오류: {str(e)}"

def get_table_list() -> List[str]:
    """조회 가능한 테이블 목록 반환"""
    return [
        'tru_stck_itms_ht',
        'tru_stck_itms_ht_t',
        'tru_fund_infr_bs',
        'tru_fund_infr_bs_t',
        'pfo_stck_ma',
        'pfo_stck_ma_t',
        'pfo_clfd_revs_stpr_ma',
        'pfo_clfd_revs_stpr_ma_t',
        'pfo_fund_infr_ht',
        'pfo_fund_infr_ht_t',
        'pfo_clfd_mip_ma',
        'pfo_clfd_mip_ma_t'
    ]

def get_source_tables() -> List[str]:
    """원본 테이블(기존 테이블) 목록 반환"""
    return [
        'pfo_stck_ma',
        'pfo_fund_infr_ht',
        'pfo_clfd_revs_stpr_ma',
        'pfo_clfd_mip_ma',
        'tru_fund_infr_bs',
        'tru_stck_itms_ht'
    ]

def get_target_table(source_table: str) -> str:
    """원본 테이블에 대응하는 타겟 테이블명 반환"""
    return f"{source_table}_t"

def get_table_pk_columns(table_name: str) -> List[str]:
    """테이블의 PRIMARY KEY 컬럼 목록 반환"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        # pk > 0인 컬럼들을 찾아서 정렬 (pk 순서대로)
        pk_columns = [col[1] for col in columns if col[5] > 0]
        pk_columns.sort(key=lambda x: next(col[5] for col in columns if col[1] == x))

        return pk_columns
    except Exception as e:
        return []
    finally:
        conn.close()

# 앱 시작 시 DB 초기화
if __name__ != '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
