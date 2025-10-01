# 주식 용어 사전 데이터
# 일반 용어, 은어/줄임말, ETF 용어 등을 포함

STOCK_TERMS = {
    "일반 용어": {
        "매수": {
            "term": "매수",
            "english": "Buy",
            "description": "주식을 사는 행위. '롱 포지션'이라고도 함",
            "example": "KODEX 200을 10주 매수했다"
        },
        "매도": {
            "term": "매도",
            "english": "Sell",
            "description": "보유한 주식을 파는 행위",
            "example": "손절을 위해 전량 매도했다"
        },
        "시가": {
            "term": "시가",
            "english": "Opening Price",
            "description": "장 시작 시 첫 거래 가격",
            "example": "오늘 시가는 50,000원이었다"
        },
        "종가": {
            "term": "종가",
            "english": "Closing Price",
            "description": "장 마감 시 마지막 거래 가격. 가장 중요한 가격",
            "example": "종가 기준으로 수익률을 계산한다"
        },
        "고가": {
            "term": "고가",
            "english": "High Price",
            "description": "하루 중 가장 높았던 가격",
            "example": "고가 대비 -5% 하락했다"
        },
        "저가": {
            "term": "저가",
            "english": "Low Price",
            "description": "하루 중 가장 낮았던 가격",
            "example": "저가에서 반등했다"
        },
        "상한가": {
            "term": "상한가",
            "english": "Upper Limit",
            "description": "하루 최대 상승 제한 (+30%). 2회 연속 시 거래 정지될 수 있음",
            "example": "따상 (시초가 상한가)"
        },
        "하한가": {
            "term": "하한가",
            "english": "Lower Limit",
            "description": "하루 최대 하락 제한 (-30%)",
            "example": "악재로 인해 하한가를 쳤다"
        },
        "거래량": {
            "term": "거래량",
            "english": "Volume",
            "description": "하루 동안 거래된 주식 수. 거래량이 많으면 유동성이 좋음",
            "example": "평소 거래량의 10배가 터졌다"
        },
        "시가총액": {
            "term": "시가총액",
            "english": "Market Cap",
            "description": "주가 × 발행주식수. 회사의 시장 가치",
            "example": "삼성전자 시가총액은 400조원"
        },
        "액면분할": {
            "term": "액면분할",
            "english": "Stock Split",
            "description": "주식을 쪼개서 개수를 늘리는 것. 1주 → 2주, 가격은 반으로",
            "example": "5:1 액면분할로 주가가 1/5이 되었다"
        },
        "배당": {
            "term": "배당",
            "english": "Dividend",
            "description": "회사가 이익을 주주에게 나눠주는 것",
            "example": "연 배당률 3%"
        },
        "배당락": {
            "term": "배당락",
            "english": "Ex-Dividend",
            "description": "배당 기준일 다음 날. 보통 배당만큼 주가가 떨어짐",
            "example": "배당락일에 -3% 하락"
        },
        "IPO": {
            "term": "IPO",
            "english": "Initial Public Offering",
            "description": "기업공개, 상장. 회사가 처음으로 주식시장에 나오는 것",
            "example": "카카오뱅크 IPO에 청약했다"
        },
        "공모주": {
            "term": "공모주",
            "english": "IPO Stock",
            "description": "상장 전에 일반 투자자에게 파는 주식. 로또라고도 불림",
            "example": "공모주 청약에 당첨됐다!"
        }
    },
    
    "은어/줄임말": {
        "물타기": {
            "term": "물타기",
            "english": "Averaging Down",
            "description": "손실 중인 주식을 추가 매수해서 평균 단가를 낮추는 것",
            "example": "물타기 3번째... 이제 평단가 45,000원",
            "warning": "⚠️ 하락장에서 물타기는 위험할 수 있음"
        },
        "불타기": {
            "term": "불타기",
            "english": "Averaging Up",
            "description": "수익 중인 주식을 추가 매수하는 것. 물타기 반대",
            "example": "+10% 올랐는데 추가 매수 불타기!",
            "tip": "상승 추세 확신할 때 사용"
        },
        "익절": {
            "term": "익절",
            "english": "Take Profit",
            "description": "이익 실현. 수익이 난 상태에서 파는 것",
            "example": "+20% 익절했다",
            "related": "손절"
        },
        "손절": {
            "term": "손절",
            "english": "Stop Loss",
            "description": "손해 보고 파는 것. 추가 손실을 막기 위해",
            "example": "-10%에서 손절 기준 설정",
            "tip": "손절 못하고 존버하다가 더 큰 손실 보는 경우 많음"
        },
        "존버": {
            "term": "존버",
            "english": "HODL (Hold On for Dear Life)",
            "description": "존나 버티기. 손실이 나도 팔지 않고 버티는 것",
            "example": "-30%인데 존버 중...",
            "meme": "💎🙌 (다이아몬드 핸즈)"
        },
        "존버vs손절": {
            "term": "존버vs손절",
            "english": "Hold vs Cut Loss",
            "description": "주식 투자자의 영원한 딜레마",
            "example": "손절할까 존버할까... 이게 고민이다",
            "tip": "정답은 없지만, 손절 라인 미리 정해두는 게 중요"
        },
        "평단가": {
            "term": "평단가",
            "english": "Average Price",
            "description": "평균 매수 단가. 여러 번 사고팔았을 때 평균 가격",
            "example": "평단가 50,000원에 현재가 48,000원",
            "related": "물타기, 불타기"
        },
        "물린다": {
            "term": "물린다",
            "english": "Trapped",
            "description": "손실 상태에 빠진 것. 평단가보다 현재가가 낮음",
            "example": "50,000원에 샀는데 지금 40,000원... 물렸다"
        },
        "깊물": {
            "term": "깊물",
            "english": "Deep Underwater",
            "description": "깊게 물림. -20%, -30% 이상 큰 손실",
            "example": "깊물이라 손절도 못하겠다...",
            "warning": "⚠️ 손실이 크면 회복하기 더 어려움"
        },
        "앝물": {
            "term": "앝물",
            "english": "Shallow Underwater",
            "description": "얕게 물림. -5% 정도 작은 손실",
            "example": "앝물이니까 조금만 기다려보자",
            "tip": "앝물일 때 손절이 쉬움"
        },
        "태운다": {
            "term": "태운다",
            "english": "Moon / Pump",
            "description": "급등하는 것. 로켓 타고 달까지 간다는 의미",
            "example": "오늘 +15% 태웠다! 🚀",
            "emoji": "🚀🌙"
        },
        "빠진다": {
            "term": "빠진다",
            "english": "Dump / Drop",
            "description": "급락하는 것",
            "example": "장 시작하자마자 -10% 빠졌다"
        },
        "떡락": {
            "term": "떡락",
            "english": "Heavy Drop",
            "description": "떡 하니 떨어짐. 급격한 하락",
            "example": "악재에 떡락... -15%",
            "emoji": "📉"
        },
        "떡상": {
            "term": "떡상",
            "english": "Heavy Rise",
            "description": "떡 하니 오름. 급격한 상승",
            "example": "실적 호재로 떡상! +20%",
            "emoji": "📈"
        },
        "수직낙하": {
            "term": "수직낙하",
            "english": "Vertical Drop",
            "description": "거의 90도로 떨어지는 것처럼 보이는 급락",
            "example": "수직낙하 시작... 손절 타이밍 놓침",
            "warning": "⚠️ 공포 매도 조심"
        },
        "깡통": {
            "term": "깡통",
            "english": "Blown Account",
            "description": "전 재산을 날린 상태. 계좌가 텅 빔",
            "example": "레버리지 쓰다가 깡통됐다...",
            "warning": "⚠️ 레버리지, 선물옵션 조심!"
        },
        "파산": {
            "term": "파산",
            "english": "Bankrupt",
            "description": "진짜 파산. 깡통보다 더 심각한 상태",
            "example": "빚투하다가 파산 직전...",
            "warning": "🚨 절대 빚내서 투자하지 마세요"
        },
        "영끌": {
            "term": "영끌",
            "english": "All-In",
            "description": "영혼까지 끌어모음. 대출, 신용까지 다 동원해서 투자",
            "example": "영끌해서 삼성전자 샀다",
            "warning": "🚨 매우 위험! 절대 추천하지 않음"
        },
        "빚투": {
            "term": "빚투",
            "english": "Margin Trading",
            "description": "빚내서 투자. 대출로 주식 사는 것",
            "example": "신용대출 받아서 빚투 중",
            "warning": "🚨 이자 부담 + 원금 손실 위험"
        },
        "대출투자": {
            "term": "대출투자",
            "english": "Leveraged Investment",
            "description": "빚투와 같은 의미",
            "example": "대출투자로 10배 레버리지",
            "warning": "🚨 파산 지름길"
        },
        "개미": {
            "term": "개미",
            "english": "Retail Investor",
            "description": "개인투자자. 일반 사람들",
            "example": "오늘도 개미들이 순매수 1위",
            "related": "외인, 기관"
        },
        "외인": {
            "term": "외인",
            "english": "Foreign Investor",
            "description": "외국인 투자자. 보통 덩치가 크고 영향력이 큼",
            "example": "외인 순매수 폭발!"
        },
        "기관": {
            "term": "기관",
            "english": "Institutional Investor",
            "description": "기관투자자. 연기금, 보험사, 자산운용사 등",
            "example": "기관이 물량을 털고 있다"
        },
        "외인 빨대": {
            "term": "외인 빨대",
            "english": "Foreign Outflow",
            "description": "외국인이 계속 팔아치우는 상황",
            "example": "외인 빨대 시작... 이제 하락 장기화될 듯",
            "tip": "외인 순매도가 계속되면 약세장 신호"
        },
        "기관 털기": {
            "term": "기관 털기",
            "english": "Institutional Selling",
            "description": "기관이 대량으로 파는 것",
            "example": "기관 털기에 -5% 하락",
            "warning": "⚠️ 기관이 팔면 추가 하락 가능성"
        },
        "개미털기": {
            "term": "개미털기",
            "english": "Retail Shakeout",
            "description": "세력이 일부러 하락시켜 개인투자자를 내쫓는 것",
            "example": "이거 개미털기인 것 같은데... 존버할까?",
            "tip": "공포에 팔지 말고 냉정하게 판단"
        },
        "작전": {
            "term": "작전",
            "english": "Pump & Dump",
            "description": "작전세력. 주가를 인위적으로 조작하는 세력",
            "example": "작전주 같은데? 조심해야겠다",
            "warning": "⚠️ 작전주는 결국 폭락함"
        },
        "세력": {
            "term": "세력",
            "english": "Market Maker",
            "description": "큰 자금으로 주가에 영향을 주는 집단",
            "example": "세력이 물량을 모으고 있다"
        },
        "작전주": {
            "term": "작전주",
            "english": "Manipulated Stock",
            "description": "작전 세력이 조종하는 주식. 급등 후 폭락",
            "example": "작전주 조심! 물리면 못 나옴",
            "warning": "🚨 절대 손대지 마세요"
        },
        "따상": {
            "term": "따상",
            "english": "IPO Upper Limit",
            "description": "시초가 상한가. 공모주가 상장 첫날 상한가 가는 것",
            "example": "공모주 따상 대박!"
        },
        "동학개미": {
            "term": "동학개미",
            "english": "Korean Retail Bulls",
            "description": "한국 주식에 투자하는 개인투자자. 동학농민운동에서 유래",
            "example": "동학개미들이 바닥을 매수 중"
        },
        "서학개미": {
            "term": "서학개미",
            "english": "Overseas Retail Investor",
            "description": "미국 주식에 투자하는 한국 개인투자자",
            "example": "서학개미들이 테슬라 매수"
        },
        "북학개미": {
            "term": "북학개미",
            "english": "China Stock Investor",
            "description": "중국 주식에 투자하는 개인투자자",
            "example": "북학개미들 알리바바 존버 중",
            "tip": "중국 주식은 정책 리스크 큼"
        },
        "호재": {
            "term": "호재",
            "english": "Positive News",
            "description": "좋은 소식. 주가 상승 요인",
            "example": "실적 호재로 급등!"
        },
        "악재": {
            "term": "악재",
            "english": "Negative News",
            "description": "나쁜 소식. 주가 하락 요인",
            "example": "CEO 횡령 악재..."
        },
        "호재는 악재": {
            "term": "호재는 악재",
            "english": "Buy the Rumor, Sell the News",
            "description": "좋은 뉴스가 나오면 오히려 주가가 떨어지는 현상. 이미 반영됨",
            "example": "실적 좋은데 하락? 호재는 악재네",
            "tip": "뉴스 나오기 전에 이미 상승했다면 정점일 수 있음"
        },
        "악재는 호재": {
            "term": "악재는 호재",
            "english": "Selling is Buying Opportunity",
            "description": "나쁜 뉴스에 하락했지만 오히려 매수 기회",
            "example": "악재에 떨어졌지만 악재는 호재! 매수 찬스",
            "tip": "일시적 악재는 매수 기회가 될 수 있음"
        },
        "묻어두기": {
            "term": "묻어두기",
            "english": "Buy and Hold",
            "description": "장기 투자. 사서 잊어버리기",
            "example": "S&P500 묻어두고 10년 기다린다"
        },
        "장투": {
            "term": "장투",
            "english": "Long-term Investment",
            "description": "장기 투자. 수년 이상 보유",
            "example": "장투 목적으로 삼성전자 매수",
            "related": "단타"
        },
        "단타": {
            "term": "단타",
            "english": "Day Trading",
            "description": "단기 매매. 당일 또는 며칠 내 매도",
            "example": "단타로 +3% 먹고 도망",
            "warning": "⚠️ 수수료 + 세금 고려 필요"
        },
        "스윙": {
            "term": "스윙",
            "english": "Swing Trading",
            "description": "며칠~몇 주 보유하는 중기 매매",
            "example": "스윙 트레이딩으로 일주일 보유",
            "tip": "단타와 장투의 중간"
        },
        "데이트레이딩": {
            "term": "데이트레이딩",
            "english": "Day Trading",
            "description": "하루 안에 사고파는 초단타 매매",
            "example": "데이트레이딩으로 1% 수익",
            "warning": "⚠️ 고수나 전업투자자용"
        },
        "반등": {
            "term": "반등",
            "english": "Bounce / Rebound",
            "description": "하락 후 다시 오르는 것",
            "example": "저점에서 반등 시작"
        },
        "반락": {
            "term": "반락",
            "english": "Pullback",
            "description": "상승 후 일시적으로 떨어지는 것",
            "example": "고점 대비 반락 중"
        },
        "조정": {
            "term": "조정",
            "english": "Correction",
            "description": "상승 후 자연스러운 하락. 건강한 신호일 수 있음",
            "example": "과열됐으니 조정 필요",
            "tip": "조정은 매수 기회가 될 수 있음"
        },
        "쌍바닥": {
            "term": "쌍바닥",
            "english": "Double Bottom (W Pattern)",
            "description": "W자 모양 패턴. 바닥을 두 번 찍고 반등하는 신호",
            "example": "쌍바닥 형성 후 상승 전환!"
        },
        "쌍봉": {
            "term": "쌍봉",
            "english": "Double Top (M Pattern)",
            "description": "M자 모양 패턴. 고점을 두 번 찍고 하락하는 신호",
            "example": "쌍봉 완성... 하락 전환 위험",
            "warning": "⚠️ 매도 신호"
        },
        "갭상승": {
            "term": "갭상승",
            "english": "Gap Up",
            "description": "전일 종가보다 높게 시작하는 것",
            "example": "긍정적 뉴스로 갭상승 출발"
        },
        "갭하락": {
            "term": "갭하락",
            "english": "Gap Down",
            "description": "전일 종가보다 낮게 시작하는 것",
            "example": "실적 쇼크로 갭하락..."
        },
        "갭메우기": {
            "term": "갭메우기",
            "english": "Gap Fill",
            "description": "갭 생긴 구간을 다시 채우는 현상",
            "example": "갭상승 했는데 바로 갭메우기",
            "tip": "갭은 채워지는 경향이 있음"
        },
        "불장": {
            "term": "불장",
            "english": "Bull Market",
            "description": "강세장. 주가가 계속 오르는 장세",
            "example": "요즘 불장이라 뭘 사도 오른다",
            "emoji": "🐂📈"
        },
        "곰장": {
            "term": "곰장",
            "english": "Bear Market",
            "description": "약세장. 주가가 계속 떨어지는 장세",
            "example": "곰장에선 현금이 최고",
            "emoji": "🐻📉"
        },
        "횡보": {
            "term": "횡보",
            "english": "Sideways",
            "description": "옆으로 가는 장. 오르지도 내리지도 않음",
            "example": "한 달째 횡보 중...",
            "tip": "횡보 후 큰 움직임 올 수 있음"
        },
        "박스권": {
            "term": "박스권",
            "english": "Range Bound",
            "description": "특정 가격대 안에서만 움직이는 것",
            "example": "50,000~52,000원 박스권 장세",
            "related": "횡보"
        },
        "물량": {
            "term": "물량",
            "english": "Volume / Supply",
            "description": "거래되는 주식의 양. 또는 팔려는 주식",
            "example": "세력이 물량 털어내는 중"
        },
        "물량폭탄": {
            "term": "물량폭탄",
            "english": "Heavy Selling",
            "description": "갑자기 엄청난 매도 물량이 쏟아지는 것",
            "example": "물량폭탄에 -10% 급락",
            "warning": "⚠️ 대량 매도는 하락 신호"
        },
        "가즈아": {
            "term": "가즈아",
            "english": "Let's Go!",
            "description": "올라가자! 상승 기원",
            "example": "비트코인 가즈아! 🚀",
            "meme": "🚀🚀🚀"
        },
        "우주 가즈아": {
            "term": "우주 가즈아",
            "english": "To The Moon",
            "description": "우주까지 가자! 더 높은 상승 기원",
            "example": "테슬라 우주 가즈아!",
            "emoji": "🚀🌙"
        },
        "관심 주시": {
            "term": "관심 주시",
            "english": "Watchlist",
            "description": "매수 전에 지켜보는 종목",
            "example": "일단 관심 주시에 넣어두고 관망",
            "tip": "매수 타이밍 노릴 때 사용"
        },
        "관종": {
            "term": "관종",
            "english": "Watchlist Stock",
            "description": "관심 종목. 지켜보는 주식",
            "example": "이 주식 내 관종이야"
        },
        "분할매수": {
            "term": "분할매수",
            "english": "Dollar Cost Averaging",
            "description": "한 번에 사지 않고 나눠서 매수",
            "example": "1000주를 200주씩 5번 분할매수",
            "tip": "리스크 분산 효과"
        },
        "분할매도": {
            "term": "분할매도",
            "english": "Scale Out",
            "description": "한 번에 팔지 않고 나눠서 매도",
            "example": "익절을 3번에 걸쳐 분할매도",
            "tip": "고점 못 잡아도 안정적 수익"
        },
        "풀매수": {
            "term": "풀매수",
            "english": "All-In Buy",
            "description": "가용 자금 전부로 매수",
            "example": "확신해서 풀매수 때렸다",
            "warning": "⚠️ 위험한 전략"
        },
        "풀매도": {
            "term": "풀매도",
            "english": "Full Exit",
            "description": "보유 주식 전량 매도",
            "example": "불안해서 풀매도 했다"
        },
        "현타": {
            "term": "현타",
            "english": "Reality Check",
            "description": "현실 자각 타임. 손실 보고 정신 차림",
            "example": "-50% 보고 현타 왔다...",
            "related": "멘붕"
        },
        "멘붕": {
            "term": "멘붕",
            "english": "Mental Breakdown",
            "description": "멘탈 붕괴. 큰 손실에 정신적 타격",
            "example": "연속 손절에 멘붕...",
            "tip": "휴식이 필요한 신호"
        },
        "패닉": {
            "term": "패닉",
            "english": "Panic Selling",
            "description": "공포에 질려 무작정 파는 것",
            "example": "패닉 매도로 저점에서 다 팔았다",
            "warning": "⚠️ 냉정함 잃으면 큰 손실"
        }
    },
    
    "ETF 용어": {
        "ETF": {
            "term": "ETF",
            "english": "Exchange Traded Fund",
            "description": "상장지수펀드. 인덱스를 추종하는 펀드를 주식처럼 거래",
            "example": "KODEX 200은 코스피 200 지수를 추종하는 ETF"
        },
        "추종 지수": {
            "term": "추종 지수",
            "english": "Underlying Index",
            "description": "ETF가 따라가는 기준 지수",
            "example": "SPY는 S&P 500 지수를 추종"
        },
        "괴리율": {
            "term": "괴리율",
            "english": "Tracking Error",
            "description": "ETF 가격과 실제 순자산가치(NAV)의 차이",
            "example": "괴리율 +0.5%는 약간 비싸게 거래된다는 의미",
            "tip": "괴리율이 크면 비효율적인 ETF"
        },
        "NAV": {
            "term": "NAV",
            "english": "Net Asset Value",
            "description": "순자산가치. ETF가 보유한 자산의 실제 가치",
            "example": "NAV는 10,000원인데 시장가는 10,050원"
        },
        "레버리지 ETF": {
            "term": "레버리지 ETF",
            "english": "Leveraged ETF",
            "description": "지수 변동의 2배 또는 3배로 움직이는 ETF",
            "example": "KODEX 레버리지는 코스피 200의 2배 움직임",
            "warning": "⚠️ 장기 보유 시 손실 누적 (복리 효과)"
        },
        "인버스 ETF": {
            "term": "인버스 ETF",
            "english": "Inverse ETF",
            "description": "지수와 반대로 움직이는 ETF. 하락장에서 수익",
            "example": "KODEX 인버스는 코스피가 떨어지면 오름",
            "warning": "⚠️ 장기 보유 부적합"
        },
        "배당 ETF": {
            "term": "배당 ETF",
            "english": "Dividend ETF",
            "description": "배당을 많이 주는 기업들로 구성된 ETF",
            "example": "SCHD, VYM, TIGER 미국배당귀족"
        },
        "섹터 ETF": {
            "term": "섹터 ETF",
            "english": "Sector ETF",
            "description": "특정 산업만 모은 ETF",
            "example": "XLK (기술), XLE (에너지), SMH (반도체)"
        },
        "리밸런싱": {
            "term": "리밸런싱",
            "english": "Rebalancing",
            "description": "ETF가 추종 지수에 맞춰 구성 종목을 재조정하는 것",
            "example": "분기마다 리밸런싱 실시"
        }
    },
    
    "지표": {
        "CAGR": {
            "term": "CAGR",
            "english": "Compound Annual Growth Rate",
            "description": "연평균 복리 수익률. 매년 평균 몇 %씩 벌었는지",
            "example": "5년 CAGR 12%",
            "formula": "((종가/시작가)^(1/년수) - 1) × 100"
        },
        "MDD": {
            "term": "MDD",
            "english": "Maximum Drawdown",
            "description": "최대 낙폭. 역대 최고가 대비 최대 얼마나 떨어졌는지",
            "example": "MDD 30%는 최고가에서 30% 빠졌던 적 있다는 의미",
            "tip": "적립식 투자에서 매우 중요한 지표"
        },
        "샤프 비율": {
            "term": "샤프 비율",
            "english": "Sharpe Ratio",
            "description": "위험 대비 수익의 효율성. 높을수록 좋음",
            "example": "샤프 비율 1.5 (매우 양호)",
            "formula": "(CAGR - 무위험수익률) / 변동성"
        },
        "변동성": {
            "term": "변동성",
            "english": "Volatility",
            "description": "가격이 얼마나 들쭉날쭉한지. 높을수록 위험함",
            "example": "변동성 15% (안정적)",
            "tip": "10% 미만: 매우 안정, 30% 이상: 위험"
        },
        "PER": {
            "term": "PER",
            "english": "Price to Earnings Ratio",
            "description": "주가수익비율. 주가 ÷ 주당순이익. 낮을수록 저평가",
            "example": "PER 10배 (저평가), PER 50배 (고평가)",
            "tip": "업종별로 기준이 다름"
        },
        "PBR": {
            "term": "PBR",
            "english": "Price to Book Ratio",
            "description": "주가순자산비율. 주가 ÷ 주당순자산. 1 미만이면 자산 대비 저평가",
            "example": "PBR 0.8 (저평가 가능성)"
        },
        "ROE": {
            "term": "ROE",
            "english": "Return on Equity",
            "description": "자기자본이익률. 자본으로 얼마나 이익을 냈는지. 높을수록 좋음",
            "example": "ROE 15% (우량 기업)"
        },
        "EPS": {
            "term": "EPS",
            "english": "Earnings Per Share",
            "description": "주당순이익. 한 주당 얼마나 이익을 냈는지",
            "example": "EPS 5,000원"
        }
    },
    
    "트렌드/밈": {
        "YOLO": {
            "term": "YOLO",
            "english": "You Only Live Once",
            "description": "인생 한 방! 전 재산 몰빵",
            "example": "YOLO 테슬라 콜옵션!",
            "warning": "🚨 도박이 아닙니다"
        },
        "FOMO": {
            "term": "FOMO",
            "english": "Fear Of Missing Out",
            "description": "놓칠까봐 두려워서 급하게 사는 심리",
            "example": "FOMO로 고점에 물림..."
        },
        "다이아몬드 핸즈": {
            "term": "다이아몬드 핸즈",
            "english": "Diamond Hands 💎🙌",
            "description": "어떤 상황에서도 팔지 않고 존버",
            "example": "-50%인데 다이아몬드 핸즈 유지 중"
        },
        "페이퍼 핸즈": {
            "term": "페이퍼 핸즈",
            "english": "Paper Hands 📄🙌",
            "description": "조금만 떨어져도 바로 파는 약한 멘탈",
            "example": "페이퍼 핸즈라서 -5%에 손절함"
        },
        "투더문": {
            "term": "투더문",
            "english": "To The Moon 🚀🌙",
            "description": "달까지 간다! 엄청난 상승 기대",
            "example": "GME 투더문! 🚀🚀🚀"
        },
        "우주 가즈아": {
            "term": "우주 가즈아",
            "english": "Let's Go!",
            "description": "더 높이 상승하자!",
            "example": "비트코인 우주 가즈아! 🚀"
        }
    }
}


def search_terms(query: str, limit: int = 20):
    """
    용어 검색 함수
    
    Args:
        query: 검색어
        limit: 최대 결과 개수
    
    Returns:
        검색 결과 리스트
    """
    query_lower = query.lower()
    results = []
    
    for category, terms in STOCK_TERMS.items():
        for term_key, term_data in terms.items():
            # 용어, 영문, 설명에서 검색
            if (query_lower in term_data["term"].lower() or
                query_lower in term_data.get("english", "").lower() or
                query_lower in term_data.get("description", "").lower()):
                
                results.append({
                    **term_data,
                    "category": category
                })
    
    return results[:limit]


def get_all_categories():
    """모든 카테고리 목록 반환"""
    return list(STOCK_TERMS.keys())


def get_terms_by_category(category: str):
    """카테고리별 용어 반환"""
    return STOCK_TERMS.get(category, {})

