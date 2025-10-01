// ETFolio 프론트엔드 JavaScript

const API_BASE = '/api/v1';

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    loadETFs();
    loadPortfolioSummary();
});

// ETF 목록 로드
async function loadETFs() {
    try {
        const response = await fetch(`${API_BASE}/etf/`);
        const etfs = await response.json();
        
        const etfList = document.getElementById('etf-list');
        const tickerSelect = document.getElementById('chart-ticker-select');
        
        if (etfs.length === 0) {
            etfList.innerHTML = '<p>등록된 ETF가 없습니다. 위에서 ETF를 추가해주세요.</p>';
            return;
        }
        
        // ETF 목록 표시
        etfList.innerHTML = etfs.map(etf => `
            <div class="etf-item">
                <h3>${etf.name}</h3>
                <p>티커: ${etf.ticker}</p>
                <p>시장: ${etf.market || 'N/A'}</p>
                <button onclick="deleteETF('${etf.ticker}')">삭제</button>
            </div>
        `).join('');
        
        // 차트용 셀렉트 박스 업데이트
        tickerSelect.innerHTML = '<option value="">ETF 선택</option>' + 
            etfs.map(etf => `<option value="${etf.ticker}">${etf.name} (${etf.ticker})</option>`).join('');
        
    } catch (error) {
        console.error('ETF 로딩 실패:', error);
        document.getElementById('etf-list').innerHTML = '<p>ETF 목록을 불러올 수 없습니다.</p>';
    }
}

// ETF 추가
async function addETF() {
    const ticker = document.getElementById('ticker-input').value.trim();
    const name = document.getElementById('name-input').value.trim();
    
    if (!ticker || !name) {
        alert('종목 코드와 이름을 모두 입력해주세요.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/etf/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ticker: ticker,
                name: name,
                market: null,
                category: null
            })
        });
        
        if (response.ok) {
            alert('ETF가 추가되었습니다!');
            document.getElementById('ticker-input').value = '';
            document.getElementById('name-input').value = '';
            loadETFs();
        } else {
            const error = await response.json();
            alert(`오류: ${error.detail}`);
        }
    } catch (error) {
        console.error('ETF 추가 실패:', error);
        alert('ETF 추가에 실패했습니다.');
    }
}

// ETF 삭제
async function deleteETF(ticker) {
    if (!confirm(`${ticker}를 삭제하시겠습니까?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/etf/${ticker}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('ETF가 삭제되었습니다.');
            loadETFs();
        } else {
            alert('ETF 삭제에 실패했습니다.');
        }
    } catch (error) {
        console.error('ETF 삭제 실패:', error);
        alert('ETF 삭제에 실패했습니다.');
    }
}

// 티커 빠른 설정
function setTicker(ticker, name) {
    document.getElementById('ticker-input').value = ticker;
    document.getElementById('name-input').value = name;
}

// 포트폴리오 요약 로드
async function loadPortfolioSummary() {
    try {
        const response = await fetch(`${API_BASE}/portfolio/summary`);
        const summary = await response.json();
        
        const summaryDiv = document.getElementById('portfolio-summary');
        
        const returnClass = summary.total_return >= 0 ? 'positive' : 'negative';
        const returnSign = summary.total_return >= 0 ? '+' : '';
        
        summaryDiv.innerHTML = `
            <div class="summary-item">
                <h3>총 투자금액</h3>
                <p>${formatCurrency(summary.total_investment)}</p>
            </div>
            <div class="summary-item">
                <h3>현재 평가액</h3>
                <p>${formatCurrency(summary.current_value)}</p>
            </div>
            <div class="summary-item ${returnClass}">
                <h3>총 수익</h3>
                <p>${returnSign}${formatCurrency(summary.total_return)}</p>
            </div>
            <div class="summary-item ${returnClass}">
                <h3>수익률</h3>
                <p>${returnSign}${summary.return_rate.toFixed(2)}%</p>
            </div>
            <div class="summary-item">
                <h3>총 배당금</h3>
                <p>${formatCurrency(summary.total_dividends)}</p>
            </div>
        `;
    } catch (error) {
        console.error('포트폴리오 요약 로딩 실패:', error);
    }
}

// 차트 로드
async function loadCharts() {
    const ticker = document.getElementById('chart-ticker-select').value;
    const period = document.getElementById('period-select').value;
    
    if (!ticker) {
        alert('ETF를 선택해주세요.');
        return;
    }
    
    try {
        // 분석 정보
        const analyticsResponse = await fetch(`${API_BASE}/etf/${ticker}/analytics?period=${period}`);
        const analytics = await analyticsResponse.json();
        
        displayAnalytics(analytics);
        
        // 가격 차트
        const priceResponse = await fetch(`${API_BASE}/etf/${ticker}/chart/price?period=${period}`);
        const priceData = await priceResponse.json();
        Plotly.newPlot('price-chart', JSON.parse(priceData.chart).data, JSON.parse(priceData.chart).layout);
        
        // 배당금 차트
        const dividendResponse = await fetch(`${API_BASE}/etf/${ticker}/chart/dividend`);
        const dividendData = await dividendResponse.json();
        Plotly.newPlot('dividend-chart', JSON.parse(dividendData.chart).data, JSON.parse(dividendData.chart).layout);
        
        // 누적 수익률 차트
        const returnResponse = await fetch(`${API_BASE}/etf/${ticker}/chart/cumulative-return?period=${period}`);
        const returnData = await returnResponse.json();
        Plotly.newPlot('return-chart', JSON.parse(returnData.chart).data, JSON.parse(returnData.chart).layout);
        
    } catch (error) {
        console.error('차트 로딩 실패:', error);
        alert('차트를 불러올 수 없습니다.');
    }
}

// 분석 정보 표시
function displayAnalytics(analytics) {
    const analyticsDiv = document.getElementById('analytics-info');
    
    analyticsDiv.innerHTML = `
        <div class="analytics-metric">
            <h4>현재 가격</h4>
            <p>${formatCurrency(analytics.current_price)}</p>
        </div>
        <div class="analytics-metric">
            <h4>총 수익률</h4>
            <p>${analytics.total_return.toFixed(2)}%</p>
        </div>
        <div class="analytics-metric">
            <h4>연평균 수익률 (CAGR)</h4>
            <p>${analytics.cagr.toFixed(2)}%</p>
        </div>
        <div class="analytics-metric">
            <h4>변동성</h4>
            <p>${analytics.volatility.toFixed(2)}%</p>
        </div>
        <div class="analytics-metric">
            <h4>샤프 비율</h4>
            <p>${analytics.sharpe_ratio.toFixed(2)}</p>
        </div>
        <div class="analytics-metric">
            <h4>최대 낙폭 (MDD)</h4>
            <p>${analytics.max_drawdown.toFixed(2)}%</p>
        </div>
        <div class="analytics-metric">
            <h4>배당 수익률</h4>
            <p>${analytics.dividend_yield.toFixed(2)}%</p>
        </div>
        <div class="analytics-metric">
            <h4>총 배당금</h4>
            <p>${formatCurrency(analytics.total_dividends)}</p>
        </div>
    `;
}

// 통화 포맷
function formatCurrency(value) {
    return new Intl.NumberFormat('ko-KR').format(Math.round(value));
}

