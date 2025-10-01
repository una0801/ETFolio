"""
한국 주요 ETF 목록
수동으로 관리하거나, 추후 크롤링으로 자동 업데이트 가능
"""

KOREAN_ETFS = [
    # KODEX 시리즈
    {"ticker": "069500.KS", "name": "KODEX 200", "category": "국내주식"},
    {"ticker": "114800.KS", "name": "KODEX 인버스", "category": "국내주식"},
    {"ticker": "122630.KS", "name": "KODEX 레버리지", "category": "국내주식"},
    {"ticker": "229200.KS", "name": "KODEX 코스닥150", "category": "국내주식"},
    {"ticker": "148020.KS", "name": "KODEX 200선물인버스2X", "category": "국내주식"},
    {"ticker": "251340.KS", "name": "KODEX 코스닥150선물인버스", "category": "국내주식"},
    
    # KODEX 미국/해외
    {"ticker": "360750.KS", "name": "KODEX 미국S&P500", "category": "해외주식"},
    {"ticker": "379800.KS", "name": "KODEX 미국나스닥100TR", "category": "해외주식"},
    {"ticker": "261240.KS", "name": "KODEX 미국채울트라30년선물", "category": "해외채권"},
    
    # TIGER 시리즈
    {"ticker": "133690.KS", "name": "TIGER 미국나스닥100", "category": "해외주식"},
    {"ticker": "143850.KS", "name": "TIGER 200", "category": "국내주식"},
    {"ticker": "139260.KS", "name": "TIGER 200 IT", "category": "국내주식"},
    {"ticker": "139270.KS", "name": "TIGER 200 건설", "category": "국내주식"},
    {"ticker": "098560.KS", "name": "TIGER 미국S&P500", "category": "해외주식"},
    {"ticker": "458730.KS", "name": "TIGER 미국배당귀족", "category": "해외주식"},
    {"ticker": "360200.KS", "name": "TIGER 미국채10년선물", "category": "해외채권"},
    {"ticker": "381170.KS", "name": "TIGER 차이나항셍테크", "category": "해외주식"},
    {"ticker": "329200.KS", "name": "TIGER 유로스탁스배당30", "category": "해외주식"},
    
    # ARIRANG 시리즈
    {"ticker": "152100.KS", "name": "ARIRANG 200", "category": "국내주식"},
    {"ticker": "120660.KS", "name": "ARIRANG 고배당주", "category": "국내주식"},
    
    # KBSTAR 시리즈
    {"ticker": "091160.KS", "name": "KBSTAR 200", "category": "국내주식"},
    {"ticker": "148070.KS", "name": "KBSTAR 미국S&P500", "category": "해외주식"},
    
    # 섹터/테마
    {"ticker": "091180.KS", "name": "KODEX 자동차", "category": "국내주식"},
    {"ticker": "091170.KS", "name": "KODEX 은행", "category": "국내주식"},
    {"ticker": "229640.KS", "name": "KODEX 바이오", "category": "국내주식"},
    {"ticker": "244580.KS", "name": "KODEX 2차전지산업", "category": "국내주식"},
    {"ticker": "371460.KS", "name": "TIGER 반도체", "category": "국내주식"},
    
    # 배당/채권
    {"ticker": "140700.KS", "name": "KODEX 국고채3년", "category": "국내채권"},
    {"ticker": "148070.KS", "name": "KBSTAR 국고채10년", "category": "국내채권"},
    {"ticker": "091230.KS", "name": "KODEX 단기채권", "category": "국내채권"},
    
    # 금/원자재
    {"ticker": "132030.KS", "name": "KODEX 골드선물(H)", "category": "원자재"},
    {"ticker": "130680.KS", "name": "TIGER 원유선물Enhanced(H)", "category": "원자재"},
]

# 미국 주요 ETF
US_ETFS = [
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF", "category": "미국주식"},
    {"ticker": "QQQ", "name": "Invesco QQQ Trust", "category": "미국주식"},
    {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "category": "미국주식"},
    {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "category": "미국주식"},
    {"ticker": "IVV", "name": "iShares Core S&P 500 ETF", "category": "미국주식"},
    {"ticker": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "category": "해외주식"},
    {"ticker": "IEFA", "name": "iShares Core MSCI EAFE ETF", "category": "해외주식"},
    {"ticker": "AGG", "name": "iShares Core U.S. Aggregate Bond ETF", "category": "채권"},
    {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "category": "채권"},
    {"ticker": "GLD", "name": "SPDR Gold Shares", "category": "원자재"},
]

# 전체 ETF 목록 (검색용)
ALL_ETFS = KOREAN_ETFS + US_ETFS

