import re

def verification(original_sql :str, link_sql : str, db_link : str ) -> bool:
    # db link 가 추가된 sql 과 원본과 대조. db link 제거시 동일하면 정상, 다르면 비정상

    if '@' not in db_link[0]:
        db_link = '@' + db_link

    original_sql = re.sub(r'\s+', '', original_sql)

    link_sql = link_sql.replace(db_link, '')
    link_sql = re.sub(r'\s+', '', link_sql) 

    return link_sql == original_sql
