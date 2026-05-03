import re

# From page_1/funcs.py
def verification(original_sql: str, link_sql: str, db_link: list) -> bool:
    """DB link가 추가된 SQL을 원본과 대조하여 정상인지 검증"""
    original_sql = re.sub(r'\s+', '', original_sql)
    for link in db_link:
        link_sql = link_sql.replace(link, '')
    link_sql = re.sub(r'\s+', '', link_sql)
    return link_sql == original_sql


def verification_2(original_sql: str, link_sql: str) -> bool:
    """DB link 정보 없이 단순 공백 제거 후 비교 (LLM 경로용)"""
    original_sql = re.sub(r'\s+', '', original_sql)
    link_sql = re.sub(r'\s+', '', link_sql)
    return link_sql == original_sql


# From page_2/funcs.py (renamed to avoid conflict)
def verification_simple(original_sql: str, link_sql: str, db_link: str) -> bool:
    """DB link가 추가된 SQL과 원본을 대조. DB link 제거시 동일하면 정상"""
    if '@' not in db_link[0]:
        db_link = '@' + db_link

    original_sql = re.sub(r'\s+', '', original_sql)
    link_sql = link_sql.replace(db_link, '')
    link_sql = re.sub(r'\s+', '', link_sql)
    return link_sql == original_sql
