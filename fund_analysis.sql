
SELECT
    'PFO_FUND_BASIC_ANALYSIS' AS analysis_type,
    pf.mncm_code,
    pf.fund_code,
    pf.fund_name,
    pf.fund_type,
    pf.fund_status,
    pf.setting_date,
    pf.maturity_date,
    pf.nav_amt AS current_nav,
    pf.base_price,
    pf.currency_code,
    pf.manager_id,
    CAST((pf.nav_amt - pf.base_price) AS REAL) AS nav_change,
    CASE
        WHEN pf.base_price > 0 THEN CAST(((pf.nav_amt - pf.base_price) / pf.base_price * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    COUNT(DISTINCT ps.itms_code) AS holding_items,
    ROUND(SUM(COALESCE(ps.eval_amt, 0)), 2) AS total_evaluation_amount,
    ROUND(SUM(COALESCE(ps.buy_amt, 0)), 2) AS total_buy_amount,
    ROUND(SUM(COALESCE(ps.profit_loss, 0)), 2) AS total_profit_loss,
    MAX(ps.proc_date) AS last_update_date,
    pf.upd_dtm
FROM pfo_fund_bs pf
LEFT JOIN pfo_stck_ma ps ON pf.mncm_code = ps.mncm_code
    AND pf.fund_code = ps.fund_code
    AND ps.proc_date = (
        SELECT MAX(proc_date) FROM pfo_stck_ma
        WHERE mncm_code = pf.mncm_code AND fund_code = pf.fund_code
    )
GROUP BY pf.mncm_code, pf.fund_code, pf.fund_name, pf.fund_type, pf.fund_status,
         pf.setting_date, pf.maturity_date, pf.nav_amt, pf.base_price,
         pf.currency_code, pf.manager_id, pf.upd_dtm

UNION ALL

-- 2. 포트폴리오 펀드 분류 자산 현황 분석
SELECT
    'PFO_ASSET_COMPOSITION' AS analysis_type,
    pm.mncm_code,
    pm.fund_code,
    'Asset Composition as of ' || pm.proc_date AS fund_name,
    'ASSET_ANALYSIS' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(pm.nav_amt, 2) AS current_nav,
    ROUND(pm.prdy_nav_amt, 2) AS base_price,
    pm.currency_code,
    NULL AS manager_id,
    CAST((pm.nav_amt - pm.prdy_nav_amt) AS REAL) AS nav_change,
    CASE
        WHEN pm.prdy_nav_amt > 0 THEN CAST(((pm.nav_amt - pm.prdy_nav_amt) / pm.prdy_nav_amt * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    5 AS holding_items,
    ROUND(pm.nav_amt, 2) AS total_evaluation_amount,
    ROUND(pm.tast_amt, 2) AS total_buy_amount,
    ROUND((pm.nav_amt - pm.tast_amt), 2) AS total_profit_loss,
    pm.proc_date AS last_update_date,
    pm.upd_dtm
FROM pfo_clfd_mip_ma pm
WHERE pm.proc_date = (
    SELECT MAX(proc_date) FROM pfo_clfd_mip_ma
    WHERE mncm_code = pm.mncm_code AND fund_code = pm.fund_code
)

UNION ALL

-- 3. 포트폴리오 펀드 수익률 분석 (기준지수 대비)
SELECT
    'PFO_PERFORMANCE_COMPARISON' AS analysis_type,
    pr.mncm_code,
    pr.fund_code,
    'Performance vs Benchmark as of ' || pr.proc_date AS fund_name,
    'PERFORMANCE' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    pr.revs_stpr AS current_nav,
    pr.bm_stpr AS base_price,
    pr.currency_code,
    NULL AS manager_id,
    CAST((pr.revs_stpr - pr.bm_stpr) AS REAL) AS nav_change,
    CASE
        WHEN pr.bm_stpr > 0 THEN CAST(((pr.revs_stpr - pr.bm_stpr) / pr.bm_stpr * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    1 AS holding_items,
    ROUND(pr.rnrt, 2) AS total_evaluation_amount,
    ROUND(pr.bm_rnrt, 2) AS total_buy_amount,
    ROUND((pr.rnrt - pr.bm_rnrt), 2) AS total_profit_loss,
    pr.proc_date AS last_update_date,
    pr.upd_dtm
FROM pfo_clfd_revs_stpr_ma pr
WHERE pr.proc_date = (
    SELECT MAX(proc_date) FROM pfo_clfd_revs_stpr_ma
    WHERE mncm_code = pr.mncm_code AND fund_code = pr.fund_code
)

UNION ALL

-- 4. 포트폴리오 펀드 히스토리 분석
SELECT
    'PFO_HISTORY_ANALYSIS' AS analysis_type,
    ph.mncm_code,
    ph.fund_code,
    ph.fund_name,
    ph.fund_type,
    ph.fund_status,
    ph.setting_date,
    ph.maturity_date,
    ROUND(ph.nav_amt, 2) AS current_nav,
    ROUND(ph.base_price, 2) AS base_price,
    ph.currency_code,
    ph.manager_id,
    CAST((ph.nav_amt - ph.base_price) AS REAL) AS nav_change,
    CASE
        WHEN ph.base_price > 0 THEN CAST(((ph.nav_amt - ph.base_price) / ph.base_price * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    NULL AS holding_items,
    ROUND(ph.nav_amt, 2) AS total_evaluation_amount,
    ROUND(ph.base_price, 2) AS total_buy_amount,
    ROUND((ph.nav_amt - ph.base_price), 2) AS total_profit_loss,
    ph.proc_date AS last_update_date,
    ph.upd_dtm
FROM pfo_fund_infr_ht ph

UNION ALL

-- 5. 신탁 펀드 기본 정보 분석
SELECT
    'TRU_FUND_BASIC_ANALYSIS' AS analysis_type,
    tf.mncm_code,
    tf.fund_code,
    tf.fund_name,
    tf.fund_type,
    tf.trmt_dncd AS fund_status,
    tf.firt_stup_date AS setting_date,
    tf.trm_date AS maturity_date,
    NULL AS current_nav,
    NULL AS base_price,
    tf.currency_code,
    tf.manager_id,
    NULL AS nav_change,
    NULL AS return_percentage,
    NULL AS holding_items,
    NULL AS total_evaluation_amount,
    NULL AS total_buy_amount,
    NULL AS total_profit_loss,
    NULL AS last_update_date,
    tf.upd_dtm
FROM tru_fund_infr_bs tf

UNION ALL

-- 6. 신탁 펀드 위험등급별 분석
SELECT
    'TRU_FUND_RISK_ANALYSIS' AS analysis_type,
    tf.mncm_code,
    tf.fund_code,
    'Risk Grade: ' || COALESCE(tf.risk_grade, 'UNRATED') || ' - ' || tf.fund_name AS fund_name,
    tf.fund_type,
    tf.trmt_dncd AS fund_status,
    tf.firt_stup_date AS setting_date,
    tf.trm_date AS maturity_date,
    NULL AS current_nav,
    NULL AS base_price,
    tf.currency_code,
    tf.manager_id,
    NULL AS nav_change,
    NULL AS return_percentage,
    NULL AS holding_items,
    NULL AS total_evaluation_amount,
    NULL AS total_buy_amount,
    NULL AS total_profit_loss,
    NULL AS last_update_date,
    tf.upd_dtm
FROM tru_fund_infr_bs tf
WHERE tf.risk_grade IS NOT NULL

UNION ALL

-- 7. 포트폴리오 주식 보유 상세 분석
SELECT
    'PFO_STOCK_DETAIL_ANALYSIS' AS analysis_type,
    ps.mncm_code,
    ps.fund_code,
    ps.itms_name || ' (' || ps.itms_code || ')' AS fund_name,
    'STOCK_HOLDING' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(ps.close_price, 2) AS current_nav,
    ROUND(ps.avg_buy_price, 2) AS base_price,
    ps.currency_code,
    NULL AS manager_id,
    CAST((ps.close_price - ps.avg_buy_price) AS REAL) AS nav_change,
    CASE
        WHEN ps.avg_buy_price > 0 THEN CAST(((ps.close_price - ps.avg_buy_price) / ps.avg_buy_price * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    ps.hold_qty AS holding_items,
    ROUND(ps.eval_amt, 2) AS total_evaluation_amount,
    ROUND(ps.buy_amt, 2) AS total_buy_amount,
    ROUND(ps.profit_loss, 2) AS total_profit_loss,
    ps.proc_date AS last_update_date,
    ps.upd_dtm
FROM pfo_stck_ma ps
WHERE ps.proc_date = (
    SELECT MAX(proc_date) FROM pfo_stck_ma
    WHERE mncm_code = ps.mncm_code AND fund_code = ps.fund_code
)

UNION ALL

-- 8. 신탁 주식 항목 히스토리 분석
SELECT
    'TRU_STOCK_HISTORY_ANALYSIS' AS analysis_type,
    NULL AS mncm_code,
    NULL AS fund_code,
    ts.itms_name || ' (' || ts.itms_code || ')' AS fund_name,
    'STOCK_HISTORY' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(ts.close_price, 2) AS current_nav,
    ROUND(ts.prdy_acqs_amt / NULLIF(ts.prdy_hold_stcn, 0), 2) AS base_price,
    NULL AS currency_code,
    NULL AS manager_id,
    CAST((ts.close_price * ts.hold_qty - ts.prdy_acqs_amt) AS REAL) AS nav_change,
    CASE
        WHEN ts.prdy_acqs_amt > 0 THEN CAST(((ts.close_price * ts.hold_qty - ts.prdy_acqs_amt) / ts.prdy_acqs_amt * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    CAST(ts.hold_qty AS INTEGER) AS holding_items,
    ROUND(ts.eval_amt, 2) AS total_evaluation_amount,
    ROUND(ts.prdy_acqs_amt + ts.incr_acqs_amt - ts.dcrs_acqs_amt, 2) AS total_buy_amount,
    ROUND((ts.eval_amt - (ts.prdy_acqs_amt + ts.incr_acqs_amt - ts.dcrs_acqs_amt)), 2) AS total_profit_loss,
    ts.proc_date AS last_update_date,
    ts.upd_dtm
FROM tru_stck_itms_ht ts
WHERE ts.proc_date = (
    SELECT MAX(proc_date) FROM tru_stck_itms_ht
    WHERE itms_code = ts.itms_code
)

UNION ALL

-- 9. 포트폴리오 테스트 데이터 기본 정보 분석
SELECT
    'PFO_TEST_FUND_BASIC_ANALYSIS' AS analysis_type,
    pft.mncm_code,
    pft.fund_code,
    pft.fund_name,
    pft.fund_type,
    pft.fund_status,
    pft.setting_date,
    pft.maturity_date,
    ROUND(pft.nav_amt, 2) AS current_nav,
    ROUND(pft.base_price, 2) AS base_price,
    pft.currency_code,
    pft.manager_id,
    CAST((pft.nav_amt - pft.base_price) AS REAL) AS nav_change,
    CASE
        WHEN pft.base_price > 0 THEN CAST(((pft.nav_amt - pft.base_price) / pft.base_price * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    COUNT(DISTINCT pst.itms_code) AS holding_items,
    ROUND(SUM(COALESCE(pst.eval_amt, 0)), 2) AS total_evaluation_amount,
    ROUND(SUM(COALESCE(pst.buy_amt, 0)), 2) AS total_buy_amount,
    ROUND(SUM(COALESCE(pst.profit_loss, 0)), 2) AS total_profit_loss,
    MAX(pst.proc_date) AS last_update_date,
    pft.upd_dtm
FROM pfo_fund_bs_t pft
LEFT JOIN pfo_stck_ma_t pst ON pft.mncm_code = pst.mncm_code
    AND pft.fund_code = pst.fund_code
    AND pst.proc_date = (
        SELECT MAX(proc_date) FROM pfo_stck_ma_t
        WHERE mncm_code = pft.mncm_code AND fund_code = pft.fund_code
    )
GROUP BY pft.mncm_code, pft.fund_code, pft.fund_name, pft.fund_type, pft.fund_status,
         pft.setting_date, pft.maturity_date, pft.nav_amt, pft.base_price,
         pft.currency_code, pft.manager_id, pft.upd_dtm

UNION ALL

-- 10. 포트폴리오 테스트 자산 구성 분석
SELECT
    'PFO_TEST_ASSET_COMPOSITION' AS analysis_type,
    pmt.mncm_code,
    pmt.fund_code,
    'Test Asset Composition as of ' || pmt.proc_date AS fund_name,
    'TEST_ASSET_ANALYSIS' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(pmt.nav_amt, 2) AS current_nav,
    ROUND(pmt.prdy_nav_amt, 2) AS base_price,
    pmt.currency_code,
    NULL AS manager_id,
    CAST((pmt.nav_amt - pmt.prdy_nav_amt) AS REAL) AS nav_change,
    CASE
        WHEN pmt.prdy_nav_amt > 0 THEN CAST(((pmt.nav_amt - pmt.prdy_nav_amt) / pmt.prdy_nav_amt * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    5 AS holding_items,
    ROUND(pmt.nav_amt, 2) AS total_evaluation_amount,
    ROUND(pmt.tast_amt, 2) AS total_buy_amount,
    ROUND((pmt.nav_amt - pmt.tast_amt), 2) AS total_profit_loss,
    pmt.proc_date AS last_update_date,
    pmt.upd_dtm
FROM pfo_clfd_mip_ma_t pmt
WHERE pmt.proc_date = (
    SELECT MAX(proc_date) FROM pfo_clfd_mip_ma_t
    WHERE mncm_code = pmt.mncm_code AND fund_code = pmt.fund_code
)

UNION ALL

-- 11. 포트폴리오 테스트 수익률 분석
SELECT
    'PFO_TEST_PERFORMANCE_COMPARISON' AS analysis_type,
    prt.mncm_code,
    prt.fund_code,
    'Test Performance vs Benchmark as of ' || prt.proc_date AS fund_name,
    'TEST_PERFORMANCE' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    prt.revs_stpr AS current_nav,
    prt.bm_stpr AS base_price,
    prt.currency_code,
    NULL AS manager_id,
    CAST((prt.revs_stpr - prt.bm_stpr) AS REAL) AS nav_change,
    CASE
        WHEN prt.bm_stpr > 0 THEN CAST(((prt.revs_stpr - prt.bm_stpr) / prt.bm_stpr * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    1 AS holding_items,
    ROUND(prt.rnrt, 2) AS total_evaluation_amount,
    ROUND(prt.bm_rnrt, 2) AS total_buy_amount,
    ROUND((prt.rnrt - prt.bm_rnrt), 2) AS total_profit_loss,
    prt.proc_date AS last_update_date,
    prt.upd_dtm
FROM pfo_clfd_revs_stpr_ma_t prt
WHERE prt.proc_date = (
    SELECT MAX(proc_date) FROM pfo_clfd_revs_stpr_ma_t
    WHERE mncm_code = prt.mncm_code AND fund_code = prt.fund_code
)

UNION ALL

-- 12. 포트폴리오 테스트 펀드 히스토리 분석
SELECT
    'PFO_TEST_HISTORY_ANALYSIS' AS analysis_type,
    pht.mncm_code,
    pht.fund_code,
    pht.fund_name,
    pht.fund_type,
    pht.fund_status,
    pht.setting_date,
    pht.maturity_date,
    ROUND(pht.nav_amt, 2) AS current_nav,
    ROUND(pht.base_price, 2) AS base_price,
    pht.currency_code,
    pht.manager_id,
    CAST((pht.nav_amt - pht.base_price) AS REAL) AS nav_change,
    CASE
        WHEN pht.base_price > 0 THEN CAST(((pht.nav_amt - pht.base_price) / pht.base_price * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    NULL AS holding_items,
    ROUND(pht.nav_amt, 2) AS total_evaluation_amount,
    ROUND(pht.base_price, 2) AS total_buy_amount,
    ROUND((pht.nav_amt - pht.base_price), 2) AS total_profit_loss,
    pht.proc_date AS last_update_date,
    pht.upd_dtm
FROM pfo_fund_infr_ht_t pht

UNION ALL

-- 13. 신탁 펀드 테스트 기본 정보 분석
SELECT
    'TRU_TEST_FUND_BASIC_ANALYSIS' AS analysis_type,
    tft.mncm_code,
    tft.fund_code,
    tft.fund_name,
    tft.fund_type,
    tft.trmt_dncd AS fund_status,
    tft.firt_stup_date AS setting_date,
    tft.trm_date AS maturity_date,
    NULL AS current_nav,
    NULL AS base_price,
    tft.currency_code,
    tft.manager_id,
    NULL AS nav_change,
    NULL AS return_percentage,
    NULL AS holding_items,
    NULL AS total_evaluation_amount,
    NULL AS total_buy_amount,
    NULL AS total_profit_loss,
    NULL AS last_update_date,
    tft.upd_dtm
FROM tru_fund_infr_bs_t tft

UNION ALL

-- 14. 신탁 펀드 테스트 위험등급별 분석
SELECT
    'TRU_TEST_FUND_RISK_ANALYSIS' AS analysis_type,
    tft.mncm_code,
    tft.fund_code,
    'Test Risk Grade: ' || COALESCE(tft.risk_grade, 'UNRATED') || ' - ' || tft.fund_name AS fund_name,
    tft.fund_type,
    tft.trmt_dncd AS fund_status,
    tft.firt_stup_date AS setting_date,
    tft.trm_date AS maturity_date,
    NULL AS current_nav,
    NULL AS base_price,
    tft.currency_code,
    tft.manager_id,
    NULL AS nav_change,
    NULL AS return_percentage,
    NULL AS holding_items,
    NULL AS total_evaluation_amount,
    NULL AS total_buy_amount,
    NULL AS total_profit_loss,
    NULL AS last_update_date,
    tft.upd_dtm
FROM tru_fund_infr_bs_t tft
WHERE tft.risk_grade IS NOT NULL

UNION ALL

-- 15. 포트폴리오 테스트 주식 보유 상세 분석
SELECT
    'PFO_TEST_STOCK_DETAIL_ANALYSIS' AS analysis_type,
    pst.mncm_code,
    pst.fund_code,
    pst.itms_name || ' (' || pst.itms_code || ')' AS fund_name,
    'TEST_STOCK_HOLDING' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(pst.close_price, 2) AS current_nav,
    ROUND(pst.avg_buy_price, 2) AS base_price,
    pst.currency_code,
    NULL AS manager_id,
    CAST((pst.close_price - pst.avg_buy_price) AS REAL) AS nav_change,
    CASE
        WHEN pst.avg_buy_price > 0 THEN CAST(((pst.close_price - pst.avg_buy_price) / pst.avg_buy_price * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    pst.hold_qty AS holding_items,
    ROUND(pst.eval_amt, 2) AS total_evaluation_amount,
    ROUND(pst.buy_amt, 2) AS total_buy_amount,
    ROUND(pst.profit_loss, 2) AS total_profit_loss,
    pst.proc_date AS last_update_date,
    pst.upd_dtm
FROM pfo_stck_ma_t pst
WHERE pst.proc_date = (
    SELECT MAX(proc_date) FROM pfo_stck_ma_t
    WHERE mncm_code = pst.mncm_code AND fund_code = pst.fund_code
)

UNION ALL

-- 16. 신탁 테스트 주식 항목 히스토리 분석
SELECT
    'TRU_TEST_STOCK_HISTORY_ANALYSIS' AS analysis_type,
    NULL AS mncm_code,
    NULL AS fund_code,
    tst.itms_name || ' (' || tst.itms_code || ')' AS fund_name,
    'TEST_STOCK_HISTORY' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(tst.close_price, 2) AS current_nav,
    ROUND(tst.prdy_acqs_amt / NULLIF(tst.prdy_hold_stcn, 0), 2) AS base_price,
    NULL AS currency_code,
    NULL AS manager_id,
    CAST((tst.close_price * tst.hold_qty - tst.prdy_acqs_amt) AS REAL) AS nav_change,
    CASE
        WHEN tst.prdy_acqs_amt > 0 THEN CAST(((tst.close_price * tst.hold_qty - tst.prdy_acqs_amt) / tst.prdy_acqs_amt * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    CAST(tst.hold_qty AS INTEGER) AS holding_items,
    ROUND(tst.eval_amt, 2) AS total_evaluation_amount,
    ROUND(tst.prdy_acqs_amt + tst.incr_acqs_amt - tst.dcrs_acqs_amt, 2) AS total_buy_amount,
    ROUND((tst.eval_amt - (tst.prdy_acqs_amt + tst.incr_acqs_amt - tst.dcrs_acqs_amt)), 2) AS total_profit_loss,
    tst.proc_date AS last_update_date,
    tst.upd_dtm
FROM tru_stck_itms_ht_t tst
WHERE tst.proc_date = (
    SELECT MAX(proc_date) FROM tru_stck_itms_ht_t
    WHERE itms_code = tst.itms_code
)

UNION ALL

-- 17. 통합 펀드 요약 분석 - 통화별 그룹핑
SELECT
    'FUND_SUMMARY_BY_CURRENCY' AS analysis_type,
    'SUMMARY' AS mncm_code,
    pf.currency_code AS fund_code,
    'Currency: ' || COALESCE(pf.currency_code, 'UNKNOWN') AS fund_name,
    'CURRENCY_SUMMARY' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS current_nav,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS base_price,
    pf.currency_code,
    NULL AS manager_id,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS nav_change,
    CASE
        WHEN SUM(COALESCE(pf.base_price, 0)) > 0 THEN CAST((SUM(COALESCE(pf.nav_amt - pf.base_price, 0)) / SUM(COALESCE(pf.base_price, 0)) * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    COUNT(DISTINCT pf.fund_code) AS holding_items,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS total_evaluation_amount,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS total_buy_amount,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS total_profit_loss,
    NULL AS last_update_date,
    NULL AS upd_dtm
FROM pfo_fund_bs pf
GROUP BY pf.currency_code

UNION ALL

-- 18. 통합 펀드 요약 분석 - 펀드 타입별 그룹핑
SELECT
    'FUND_SUMMARY_BY_TYPE' AS analysis_type,
    'SUMMARY' AS mncm_code,
    pf.fund_type AS fund_code,
    'Fund Type: ' || COALESCE(pf.fund_type, 'UNKNOWN') AS fund_name,
    'FUND_TYPE_SUMMARY' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS current_nav,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS base_price,
    NULL AS currency_code,
    NULL AS manager_id,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS nav_change,
    CASE
        WHEN SUM(COALESCE(pf.base_price, 0)) > 0 THEN CAST((SUM(COALESCE(pf.nav_amt - pf.base_price, 0)) / SUM(COALESCE(pf.base_price, 0)) * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    COUNT(DISTINCT pf.fund_code) AS holding_items,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS total_evaluation_amount,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS total_buy_amount,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS total_profit_loss,
    NULL AS last_update_date,
    NULL AS upd_dtm
FROM pfo_fund_bs pf
GROUP BY pf.fund_type

UNION ALL

-- 19. 통합 펀드 요약 분석 - 펀드 상태별 그룹핑
SELECT
    'FUND_SUMMARY_BY_STATUS' AS analysis_type,
    'SUMMARY' AS mncm_code,
    pf.fund_status AS fund_code,
    'Fund Status: ' || COALESCE(pf.fund_status, 'UNKNOWN') AS fund_name,
    'FUND_STATUS_SUMMARY' AS fund_type,
    pf.fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS current_nav,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS base_price,
    NULL AS currency_code,
    NULL AS manager_id,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS nav_change,
    CASE
        WHEN SUM(COALESCE(pf.base_price, 0)) > 0 THEN CAST((SUM(COALESCE(pf.nav_amt - pf.base_price, 0)) / SUM(COALESCE(pf.base_price, 0)) * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    COUNT(DISTINCT pf.fund_code) AS holding_items,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS total_evaluation_amount,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS total_buy_amount,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS total_profit_loss,
    NULL AS last_update_date,
    NULL AS upd_dtm
FROM pfo_fund_bs pf
GROUP BY pf.fund_status

UNION ALL

-- 20. 통합 펀드 요약 분석 - 매니저별 그룹핑
SELECT
    'FUND_SUMMARY_BY_MANAGER' AS analysis_type,
    'SUMMARY' AS mncm_code,
    pf.manager_id AS fund_code,
    'Manager: ' || COALESCE(pf.manager_id, 'UNASSIGNED') AS fund_name,
    'MANAGER_SUMMARY' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS current_nav,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS base_price,
    NULL AS currency_code,
    pf.manager_id,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS nav_change,
    CASE
        WHEN SUM(COALESCE(pf.base_price, 0)) > 0 THEN CAST((SUM(COALESCE(pf.nav_amt - pf.base_price, 0)) / SUM(COALESCE(pf.base_price, 0)) * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    COUNT(DISTINCT pf.fund_code) AS holding_items,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS total_evaluation_amount,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS total_buy_amount,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS total_profit_loss,
    NULL AS last_update_date,
    NULL AS upd_dtm
FROM pfo_fund_bs pf
GROUP BY pf.manager_id

UNION ALL

-- 21. 통합 펀드 요약 분석 - 만기 상태별 그룹핑
SELECT
    'FUND_SUMMARY_BY_MATURITY' AS analysis_type,
    'SUMMARY' AS mncm_code,
    CASE
        WHEN pf.maturity_date IS NULL THEN 'NO_MATURITY'
        WHEN pf.maturity_date < date('now') THEN 'EXPIRED'
        ELSE 'ACTIVE'
    END AS fund_code,
    'Maturity Status: ' || CASE
        WHEN pf.maturity_date IS NULL THEN 'No Maturity Date'
        WHEN pf.maturity_date < date('now') THEN 'Expired'
        ELSE 'Active'
    END AS fund_name,
    'MATURITY_SUMMARY' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS current_nav,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS base_price,
    NULL AS currency_code,
    NULL AS manager_id,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS nav_change,
    CASE
        WHEN SUM(COALESCE(pf.base_price, 0)) > 0 THEN CAST((SUM(COALESCE(pf.nav_amt - pf.base_price, 0)) / SUM(COALESCE(pf.base_price, 0)) * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    COUNT(DISTINCT pf.fund_code) AS holding_items,
    ROUND(SUM(COALESCE(pf.nav_amt, 0)), 2) AS total_evaluation_amount,
    ROUND(SUM(COALESCE(pf.base_price, 0)), 2) AS total_buy_amount,
    ROUND(SUM(COALESCE(pf.nav_amt - pf.base_price, 0)), 2) AS total_profit_loss,
    NULL AS last_update_date,
    NULL AS upd_dtm
FROM pfo_fund_bs pf
GROUP BY CASE
    WHEN pf.maturity_date IS NULL THEN 'NO_MATURITY'
    WHEN pf.maturity_date < date('now') THEN 'EXPIRED'
    ELSE 'ACTIVE'
END

UNION ALL

-- 22. 포트폴리오 주식 보유 - 종목별 통합 분석
SELECT
    'PFO_STOCK_CONSOLIDATED' AS analysis_type,
    'STOCK_ANALYSIS' AS mncm_code,
    ps.itms_code AS fund_code,
    ps.itms_name AS fund_name,
    'CONSOLIDATED_STOCK' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    ROUND(AVG(ps.close_price), 2) AS current_nav,
    ROUND(AVG(ps.avg_buy_price), 2) AS base_price,
    ps.currency_code,
    NULL AS manager_id,
    ROUND(AVG(ps.close_price - ps.avg_buy_price), 2) AS nav_change,
    CASE
        WHEN AVG(ps.avg_buy_price) > 0 THEN CAST((AVG(ps.close_price - ps.avg_buy_price) / AVG(ps.avg_buy_price) * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    COUNT(DISTINCT ps.fund_code) AS holding_items,
    ROUND(SUM(ps.eval_amt), 2) AS total_evaluation_amount,
    ROUND(SUM(ps.buy_amt), 2) AS total_buy_amount,
    ROUND(SUM(ps.profit_loss), 2) AS total_profit_loss,
    MAX(ps.proc_date) AS last_update_date,
    MAX(ps.upd_dtm) AS upd_dtm
FROM pfo_stck_ma ps
WHERE ps.proc_date = (
    SELECT MAX(proc_date) FROM pfo_stck_ma
    WHERE itms_code = ps.itms_code
)
GROUP BY ps.itms_code, ps.itms_name, ps.currency_code

UNION ALL

-- 23. 신탁 펀드 통합 분석 - 신탁 형태별
SELECT
    'TRU_FUND_BY_TRUST_TYPE' AS analysis_type,
    'TRUST_ANALYSIS' AS mncm_code,
    tf.trst_dncd AS fund_code,
    'Trust Type: ' || COALESCE(tf.trst_dncd, 'UNKNOWN') AS fund_name,
    'TRUST_TYPE_ANALYSIS' AS fund_type,
    'ACTIVE' AS fund_status,
    NULL AS setting_date,
    NULL AS maturity_date,
    NULL AS current_nav,
    NULL AS base_price,
    tf.currency_code,
    NULL AS manager_id,
    NULL AS nav_change,
    NULL AS return_percentage,
    COUNT(DISTINCT tf.fund_code) AS holding_items,
    NULL AS total_evaluation_amount,
    NULL AS total_buy_amount,
    NULL AS total_profit_loss,
    NULL AS last_update_date,
    NULL AS upd_dtm
FROM tru_fund_infr_bs tf
GROUP BY tf.trst_dncd, tf.currency_code

UNION ALL

-- 24. 신탁 펀드 통합 분석 - 신탁 상태별
SELECT
    'TRU_FUND_BY_TRUST_STATUS' AS analysis_type,
    'TRUST_ANALYSIS' AS mncm_code,
    tf.trmt_dncd AS fund_code,
    'Trust Status: ' || COALESCE(tf.trmt_dncd, 'UNKNOWN') AS fund_name,
    'TRUST_STATUS_ANALYSIS' AS fund_type,
    tf.trmt_dncd,
    NULL AS setting_date,
    NULL AS maturity_date,
    NULL AS current_nav,
    NULL AS base_price,
    tf.currency_code,
    NULL AS manager_id,
    NULL AS nav_change,
    NULL AS return_percentage,
    COUNT(DISTINCT tf.fund_code) AS holding_items,
    NULL AS total_evaluation_amount,
    NULL AS total_buy_amount,
    NULL AS total_profit_loss,
    NULL AS last_update_date,
    NULL AS upd_dtm
FROM tru_fund_infr_bs tf
GROUP BY tf.trmt_dncd, tf.currency_code

UNION ALL

-- 25. 포트폴리오 펀드 상관 분석 - 주식 보유 현황
SELECT
    'PFO_FUND_STOCK_CORRELATION' AS analysis_type,
    ps.mncm_code,
    pf.fund_code,
    pf.fund_name || ' - Stock Holdings' AS fund_name,
    'CORRELATION_ANALYSIS' AS fund_type,
    pf.fund_status,
    pf.setting_date,
    pf.maturity_date,
    ROUND(SUM(ps.hold_qty * ps.close_price), 2) AS current_nav,
    ROUND(SUM(ps.buy_amt), 2) AS base_price,
    pf.currency_code,
    pf.manager_id,
    ROUND(SUM(ps.eval_amt - ps.buy_amt), 2) AS nav_change,
    CASE
        WHEN SUM(ps.buy_amt) > 0 THEN CAST((SUM(ps.eval_amt - ps.buy_amt) / SUM(ps.buy_amt) * 100) AS REAL)
        ELSE 0
    END AS return_percentage,
    COUNT(DISTINCT ps.itms_code) AS holding_items,
    ROUND(SUM(ps.eval_amt), 2) AS total_evaluation_amount,
    ROUND(SUM(ps.buy_amt), 2) AS total_buy_amount,
    ROUND(SUM(ps.profit_loss), 2) AS total_profit_loss,
    MAX(ps.proc_date) AS last_update_date,
    pf.upd_dtm
FROM pfo_stck_ma ps
INNER JOIN pfo_fund_bs pf ON ps.mncm_code = pf.mncm_code
    AND ps.fund_code = pf.fund_code
WHERE ps.proc_date = (
    SELECT MAX(proc_date) FROM pfo_stck_ma
    WHERE mncm_code = ps.mncm_code AND fund_code = ps.fund_code
)
GROUP BY ps.mncm_code, pf.fund_code, pf.fund_name, pf.fund_type, pf.fund_status,
         pf.setting_date, pf.maturity_date, pf.currency_code, pf.manager_id, pf.upd_dtm

ORDER BY analysis_type, mncm_code, fund_code;
