// ETFolio 프론트엔드 JavaScript

const API_BASE = '/api/v1';

// 페이지 로드 시 실행
let choicesInstance = null;
let allETFs = [];

document.addEventListener('DOMContentLoaded', function() {
    loadETFs();
    loadPortfolioSummary();
    loadETFList();
});

// 무한 스크롤용 변수
let currentOffset = 0;
let isLoadingMore = false;
let hasMore = true;
let totalETFCount = 0;

// 사용 가능한 ETF 목록 로드 (Choices.js 통합 + 무한 스크롤)
async function loadETFList(reset = false) {
    try {
        if (reset) {
            currentOffset = 0;
            allETFs = [];
            hasMore = true;
        }
        
        if (!hasMore || isLoadingMore) return;
        
        isLoadingMore = true;
        
        // 한 번에 많이 로드 (1000개)
        const response = await fetch(`${API_BASE}/etf/list?limit=1000&offset=${currentOffset}`);
        const data = await response.json();
        
        // 기존 목록에 추가
        allETFs = allETFs.concat(data.etfs);
        totalETFCount = data.total;
        hasMore = data.has_more;
        currentOffset += data.etfs.length;
        
        const etfSelect = document.getElementById('etf-select');
        if (!etfSelect) return;
        
        // 처음 로딩일 때만 Choices.js 초기화
        if (!choicesInstance) {
            choicesInstance = new Choices(etfSelect, {
                searchEnabled: true,
                searchPlaceholderValue: '종목명 또는 티커 입력...',
                noResultsText: '검색 결과 없음',
                noChoicesText: 'ETF 목록 로딩 중...',
                itemSelectText: '선택하려면 클릭',
                shouldSort: false,
                removeItemButton: false,
                searchFields: ['label', 'value'],
                fuseOptions: {
                    includeScore: true,
                    threshold: 0.3,
                }
            });
        }
        
        // ETF 목록을 Choices.js에 추가
        const choices = data.etfs.map(etf => ({
            value: etf.ticker,
            label: `${etf.name} (${etf.ticker}) - ${etf.category}`,
            customProperties: {
                name: etf.name,
                category: etf.category,
                market: etf.market || 'Unknown'
            }
        }));
        
        choicesInstance.setChoices(choices, 'value', 'label', false); // false = 기존 항목 유지
        
        console.log(`ETF 목록 로딩: ${allETFs.length}/${totalETFCount}개 (더 불러올 수 있음: ${hasMore})`);
        
        // 진행 상황 UI 업데이트
        const countInfo = document.getElementById('etf-count-info');
        if (countInfo) {
            if (hasMore) {
                countInfo.textContent = `📊 ETF 로딩 중... ${allETFs.length}/${totalETFCount}개`;
            } else {
                countInfo.textContent = `📊 총 ${totalETFCount}개 ETF 로딩 완료 (한국 ETF 전체 + 미국 주요 ETF)`;
            }
        }
        
        isLoadingMore = false;
        
        // 자동으로 전체 로드 (한국 ETF는 보통 300개 정도라 괜찮음)
        if (hasMore && allETFs.length < 2000) {
            setTimeout(() => loadETFList(false), 100); // 연속 로딩
        }
        
    } catch (error) {
        console.error('ETF 목록 로딩 실패:', error);
        alert('ETF 목록을 불러올 수 없습니다. 페이지를 새로고침해주세요.');
        isLoadingMore = false;
    }
}

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

// 셀렉트에서 ETF 선택 시
// Choices.js에서 선택한 ETF 추가
async function addETFFromSelect() {
    if (!choicesInstance) {
        alert('ETF 목록이 로딩되지 않았습니다.');
        return;
    }
    
    const selectedValue = choicesInstance.getValue(true);
    
    if (!selectedValue) {
        alert('ETF를 선택해주세요.');
        return;
    }
    
    // 선택한 ETF 정보 찾기
    const selectedETF = allETFs.find(etf => etf.ticker === selectedValue);
    
    if (!selectedETF) {
        alert('선택한 ETF 정보를 찾을 수 없습니다.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/etf/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticker: selectedETF.ticker,
                name: selectedETF.name
            })
        });
        
        if (response.ok) {
            alert(`✅ ${selectedETF.name} (${selectedETF.ticker}) 추가 완료!`);
            choicesInstance.setChoiceByValue(''); // 선택 초기화
            loadETFs();
        } else {
            const error = await response.json();
            alert(`오류: ${error.detail}`);
        }
    } catch (error) {
        console.error('ETF 추가 실패:', error);
        alert('ETF 추가 중 오류가 발생했습니다.');
    }
}

// 레거시 함수 (호환성 유지)
async function addETF() {
    await addETFFromSelect();
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

// DB 정보 모달
async function showDBInfo() {
    const modal = document.getElementById('dbModal');
    const content = document.getElementById('dbInfoContent');
    
    modal.classList.add('show');
    content.innerHTML = '<p>로딩 중...</p>';
    
    try {
        const response = await fetch('/api/v1/db-info');
        const info = await response.json();
        
        const dbTypeClass = info.database_type === 'PostgreSQL' ? 'postgres' : 'sqlite';
        const dbIcon = info.database_type === 'PostgreSQL' ? '🐘' : '🗄️';
        
        content.innerHTML = `
            <div class="db-status">
                <h3>데이터베이스 타입</h3>
                <span class="db-type ${dbTypeClass}">
                    ${dbIcon} ${info.database_type}
                </span>
                <p><strong>환경:</strong> ${info.environment}</p>
                <p><strong>상태:</strong> ${info.status === 'connected' ? '✅ 연결됨' : '❌ 연결 안 됨'}</p>
                
                <h3 style="margin-top: 20px;">연결 URL</h3>
                <div class="connection-url">${info.connection_url}</div>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `
            <div class="db-status">
                <p style="color: #FC427B;">❌ 데이터베이스 정보를 불러올 수 없습니다.</p>
                <p>${error.message}</p>
            </div>
        `;
    }
}

function closeDBModal() {
    document.getElementById('dbModal').classList.remove('show');
}

function closeModal(event) {
    if (event.target.id === 'dbModal') {
        closeDBModal();
    }
}

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeDBModal();
    }
});

