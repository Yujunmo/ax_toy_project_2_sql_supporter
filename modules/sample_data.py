import sqlite3
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data_migration.db')

# 샘플 데이터 정의
SAMPLE_STOCKS = [
    # 국내 주식
    {"itms_code": "005930", "itms_name": "삼성전자", "currency": "KRW", "base_price": 70000, "volatility": 0.02},
    {"itms_code": "000660", "itms_name": "SK하이닉스", "currency": "KRW", "base_price": 180000, "volatility": 0.025},
    {"itms_code": "051910", "itms_name": "LG화학", "currency": "KRW", "base_price": 730000, "volatility": 0.022},
    {"itms_code": "005380", "itms_name": "현대차", "currency": "KRW", "base_price": 250000, "volatility": 0.018},
    {"itms_code": "035720", "itms_name": "카카오", "currency": "KRW", "base_price": 67000, "volatility": 0.03},

    # 해외 주식 (미국)
    {"itms_code": "AAPL", "itms_name": "Apple Inc.", "currency": "USD", "base_price": 195.5, "volatility": 0.015},
    {"itms_code": "MSFT", "itms_name": "Microsoft Corp.", "currency": "USD", "base_price": 420.3, "volatility": 0.012},
    {"itms_code": "NVDA", "itms_name": "NVIDIA Corp.", "currency": "USD", "base_price": 875.4, "volatility": 0.035},
    {"itms_code": "TSLA", "itms_name": "Tesla Inc.", "currency": "USD", "base_price": 245.2, "volatility": 0.04},
    {"itms_code": "GOOGL", "itms_name": "Alphabet Inc.", "currency": "USD", "base_price": 165.8, "volatility": 0.018},
]

SAMPLE_FUNDS = [
    {"fund_code": "FND001", "fund_name": "K-Tech 성장펀드", "fund_type": "주식", "manager_id": "PM001"},
    {"fund_code": "FND002", "fund_name": "Global 주식혼합펀드", "fund_type": "혼합", "manager_id": "PM002"},
    {"fund_code": "FND003", "fund_name": "글로벌 기술주펀드", "fund_type": "주식", "manager_id": "PM003"},
]

def insert_sample_data():
    """샘플 데이터 삽입"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    mncm_code = "E3069"
    start_date = datetime(2026, 3, 1)
    end_date = datetime(2026, 4, 30)

    current_date = start_date
    day_count = 0

    while current_date <= end_date:
        # 주말 제외
        if current_date.weekday() < 5:  # 월-금 (0-4)
            proc_date = current_date.strftime("%Y%m%d")
            day_count += 1

            # 펀드별 포트폴리오 생성
            for fund in SAMPLE_FUNDS:
                fund_code = fund["fund_code"]

                # 펀드 정보 삽입 (히스토리)
                nav_base = 100000000 + (day_count * 500000)  # 시간에 따라 증가
                nav_variance = (day_count % 10) * 1000000 - 5000000  # -500만~500만 변동
                nav_amt = nav_base + nav_variance

                base_price = 10000 + (day_count * 50) + ((day_count % 5) * 200 - 400)

                cursor.execute('''
                    INSERT OR REPLACE INTO pfo_fund_infr_ht
                    (mncm_code, proc_date, fund_code, fund_name, fund_type, fund_status,
                     setting_date, maturity_date, nav_amt, base_price, currency_code, manager_id, upd_dtm)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    mncm_code,
                    proc_date,
                    fund_code,
                    fund["fund_name"],
                    fund["fund_type"],
                    "운용중",
                    "20200101",
                    "99991231",
                    nav_amt,
                    base_price,
                    "KRW",
                    fund["manager_id"],
                    current_date.strftime("%Y-%m-%d %H:%M:%S")
                ))

                # 각 펀드에 포함된 종목들
                stocks_in_fund = SAMPLE_STOCKS[:(len(SAMPLE_STOCKS)//2 if fund_code == "FND002" else len(SAMPLE_STOCKS))]

                for idx, stock in enumerate(stocks_in_fund):
                    itms_code = stock["itms_code"]

                    # 변동성을 고려한 주가
                    price_change = (day_count % 20) * stock["volatility"] * 100 - (stock["volatility"] * 50)
                    current_price = stock["base_price"] * (1 + price_change / 100)

                    # 평균 매입 가격 (현재가와 비슷하게)
                    avg_buy_price = current_price * (0.98 + (day_count % 5) * 0.002)

                    # 보유 수량 (종목별로 다르게)
                    if stock["currency"] == "KRW":
                        hold_qty = 100 + (idx * 50) + (day_count % 10) * 5
                    else:
                        hold_qty = 50 + (idx * 10) + (day_count % 10) * 2

                    # 금액 계산
                    eval_amt = current_price * hold_qty
                    buy_amt = avg_buy_price * hold_qty
                    profit_loss = eval_amt - buy_amt

                    cursor.execute('''
                        INSERT OR REPLACE INTO pfo_stck_ma
                        (mncm_code, proc_date, fund_code, itms_code, itms_name, hold_qty,
                         avg_buy_price, close_price, eval_amt, buy_amt, profit_loss, currency_code, upd_dtm)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        mncm_code,
                        proc_date,
                        fund_code,
                        itms_code,
                        stock["itms_name"],
                        hold_qty,
                        round(avg_buy_price, 2),
                        round(current_price, 2),
                        round(eval_amt, 2),
                        round(buy_amt, 2),
                        round(profit_loss, 2),
                        stock["currency"],
                        current_date.strftime("%Y-%m-%d %H:%M:%S")
                    ))

        current_date += timedelta(days=1)

    conn.commit()
    conn.close()

    print(f"✅ 샘플 데이터 삽입 완료")
    print(f"   운용사코드: {mncm_code}")
    print(f"   기간: 2026-03-01 ~ 2026-04-30 (거래일 기준 {day_count}일)")
    print(f"   펀드: {len(SAMPLE_FUNDS)}개")
    print(f"   종목: {len(SAMPLE_STOCKS)}개")

def insert_sample_data_new_tables():
    """새로운 4개 테이블에 샘플 데이터 삽입 (E3069, 2026-03-01 ~ 04)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    mncm_code = 'E3069'

    # 신탁 펀드 정보 (tru_fund_infr_bs)
    funds = [
        ('F001', 'KODEX 200 추적', '20200101', None, 'Y', 'F', 'KRW', 'MGR001', 'A'),
        ('F002', '삼성 성장 펀드', '20210301', None, 'Y', 'F', 'KRW', 'MGR002', 'B'),
        ('F003', '미래에셋 안정성장', '20190615', None, 'Y', 'F', 'KRW', 'MGR003', 'A'),
        ('F004', 'KB글로벌 선진국', '20220101', None, 'Y', 'F', 'USD', 'MGR004', 'C'),
    ]

    # 신탁 종목
    items = [
        ('088160', '삼성전자'),
        ('000660', 'SK하이닉스'),
        ('035420', 'NAVER'),
        ('035720', '카카오'),
        ('051910', 'LG화학'),
        ('005490', 'POSCO'),
        ('096770', 'SK이노베이션'),
        ('207940', '삼성바이오로직스'),
    ]

    # 펀드 정보 삽입
    for fund_code, fund_name, setup_date, term_date, term_yn, fund_type, curr, mgr_id, risk in funds:
        cursor.execute('''
            INSERT OR REPLACE INTO tru_fund_infr_bs
            (mncm_code, fund_code, fund_name, firt_stup_date, trm_date, trmt_dncd, trst_dncd, fund_type, currency_code, manager_id, risk_grade, upd_dtm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (mncm_code, fund_code, fund_name, setup_date, term_date, term_yn, fund_type, curr, mgr_id, risk, '202603041500'))

    # 처리일자별 데이터 생성
    start_date = datetime(2026, 3, 1)
    end_date = datetime(2026, 3, 4)
    base_nav = 500000000

    current_date = start_date
    date_idx = 0

    while current_date <= end_date:
        proc_date = current_date.strftime('%Y%m%d')

        # pfo_clfd_revs_stpr_ma
        base_returns = [0.85, 1.23, 0.92, -0.45]
        for i, (fund_code, _, _, _, _, _, _, _, _) in enumerate(funds):
            revs_stpr = 10000 + (date_idx * 100) + (i * 50)
            bm_stpr = 9500 + (date_idx * 90) + (i * 40)
            rnrt = base_returns[i] + (date_idx * 0.1)
            bm_rnrt = base_returns[i] * 0.95

            cursor.execute('''
                INSERT INTO pfo_clfd_revs_stpr_ma
                (mncm_code, fund_code, proc_date, revs_stpr, bm_stpr, rnrt, bm_rnrt, currency_code, upd_dtm)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (mncm_code, fund_code, proc_date, revs_stpr, bm_stpr, rnrt, bm_rnrt, 'KRW', f'{proc_date}1530'))

        # pfo_clfd_mip_ma
        for i, (fund_code, _, _, _, _, _, _, _, _) in enumerate(funds):
            nav_amt = base_nav + (date_idx * 10000000) + (i * 5000000)
            prdy_nav_amt = nav_amt * 0.99
            tast_amt = nav_amt * 1.05
            debt_amt = nav_amt * 0.02
            cash_amt = nav_amt * 0.1
            stock_amt = nav_amt * 0.88

            cursor.execute('''
                INSERT INTO pfo_clfd_mip_ma
                (mncm_code, fund_code, proc_date, nav_amt, prdy_nav_amt, tast_amt, debt_amt, cash_amt, stock_amt, currency_code, upd_dtm)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (mncm_code, fund_code, proc_date, nav_amt, prdy_nav_amt, tast_amt, debt_amt, cash_amt, stock_amt, 'KRW', f'{proc_date}1530'))

        # tru_stck_itms_ht
        base_prices = {
            '088160': 70000 + date_idx * 1000,
            '000660': 130000 + date_idx * 2000,
            '035420': 385000 + date_idx * 1500,
            '035720': 52000 + date_idx * 800,
            '051910': 780000 + date_idx * 3000,
            '005490': 68000 + date_idx * 1200,
            '096770': 185000 + date_idx * 2500,
            '207940': 950000 + date_idx * 4000,
        }

        for i, (item_code, item_name) in enumerate(items):
            base_price = base_prices[item_code]
            close_price = base_price * (1 + (0.02 - (i % 3) * 0.01))

            prdy_acqs_amt = 100000000 + (i * 5000000)
            prdy_hold_stcn = 10000 + (i * 500)
            incr_acqs_amt = 5000000 + (date_idx * 100000)
            dcrs_acqs_amt = 2000000 + (date_idx * 50000)
            incr_stcn = 500 + (date_idx * 10)
            dcrs_stcn = 200 + (date_idx * 5)
            hold_qty = prdy_hold_stcn + incr_stcn - dcrs_stcn
            eval_amt = hold_qty * close_price

            cursor.execute('''
                INSERT INTO tru_stck_itms_ht
                (proc_date, itms_code, itms_name, prdy_acqs_amt, prdy_hold_stcn,
                 incr_acqs_amt, dcrs_acqs_amt, incr_stcn, dcrs_stcn,
                 close_price, hold_qty, eval_amt, upd_dtm)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (proc_date, item_code, item_name, prdy_acqs_amt, prdy_hold_stcn,
                  incr_acqs_amt, dcrs_acqs_amt, incr_stcn, dcrs_stcn,
                  close_price, hold_qty, eval_amt, f'{proc_date}1530'))

        current_date += timedelta(days=1)
        date_idx += 1

    conn.commit()
    conn.close()

    print(f"✅ 새로운 테이블 샘플 데이터 삽입 완료")
    print(f"   운용사코드: {mncm_code}")
    print(f"   기간: 2026-03-01 ~ 2026-03-04 (4일)")
    print(f"   • pfo_clfd_revs_stpr_ma: 16건")
    print(f"   • pfo_clfd_mip_ma: 16건")
    print(f"   • tru_fund_infr_bs: 4건")
    print(f"   • tru_stck_itms_ht: 32건")

def extend_tru_stck_itms_ht():
    """tru_stck_itms_ht를 3월 5일 ~ 4월 30일까지 확장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    items = [
        ('088160', '삼성전자'),
        ('000660', 'SK하이닉스'),
        ('035420', 'NAVER'),
        ('035720', '카카오'),
        ('051910', 'LG화학'),
        ('005490', 'POSCO'),
        ('096770', 'SK이노베이션'),
        ('207940', '삼성바이오로직스'),
    ]

    base_prices = {
        '088160': 71400,
        '000660': 132300,
        '035420': 386500,
        '035720': 52800,
        '051910': 789000,
        '005490': 69200,
        '096770': 187500,
        '207940': 958000,
    }

    start_date = datetime(2026, 3, 5)
    end_date = datetime(2026, 4, 30)

    current_date = start_date
    date_idx = 4

    while current_date <= end_date:
        proc_date = current_date.strftime('%Y%m%d')

        for i, (item_code, item_name) in enumerate(items):
            base_price = base_prices[item_code]
            close_price = base_price * (1 + (0.02 - (i % 3) * 0.01)) + (date_idx * 100)

            prdy_acqs_amt = 100000000 + (i * 5000000)
            prdy_hold_stcn = 10000 + (i * 500)
            incr_acqs_amt = 5000000 + (date_idx * 100000)
            dcrs_acqs_amt = 2000000 + (date_idx * 50000)
            incr_stcn = 500 + (date_idx * 10)
            dcrs_stcn = 200 + (date_idx * 5)
            hold_qty = prdy_hold_stcn + incr_stcn - dcrs_stcn
            eval_amt = hold_qty * close_price

            cursor.execute('''
                INSERT INTO tru_stck_itms_ht
                (proc_date, itms_code, itms_name, prdy_acqs_amt, prdy_hold_stcn,
                 incr_acqs_amt, dcrs_acqs_amt, incr_stcn, dcrs_stcn,
                 close_price, hold_qty, eval_amt, upd_dtm)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (proc_date, item_code, item_name, prdy_acqs_amt, prdy_hold_stcn,
                  incr_acqs_amt, dcrs_acqs_amt, incr_stcn, dcrs_stcn,
                  close_price, hold_qty, eval_amt, f'{proc_date}1530'))

        current_date += timedelta(days=1)
        date_idx += 1

    conn.commit()
    conn.close()

    print(f"✅ tru_stck_itms_ht 데이터 확장 완료")
    print(f"   기간: 2026-03-05 ~ 2026-04-30 (57일)")
    print(f"   추가 레코드: 456건 (57일 × 8종목)")
    print(f"   전체 tru_stck_itms_ht: 488건")

if __name__ == "__main__":
    insert_sample_data()
    insert_sample_data_new_tables()
    extend_tru_stck_itms_ht()
