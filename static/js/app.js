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

// 추천 데이터 전역 저장
let currentRecommendationData = null;
let currentRecommendationTab = 'high_return';

// 인기 ETF 추천
async function loadRecommendations() {
    const category = document.getElementById('recommendation-category').value;
    const period = document.getElementById('recommendation-period').value;
    const contentDiv = document.getElementById('recommendations-content');
    const tabsDiv = document.getElementById('recommendation-tabs');
    
    contentDiv.innerHTML = '<p style="color: #94a3b8;">분석 중... (10~20초 소요)</p>';
    tabsDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/portfolio/recommendations?category=${category}&period=${period}&limit=5`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '추천 실패');
        }
        
        const data = await response.json();
        currentRecommendationData = data;
        
        // 탭 표시
        tabsDiv.style.display = 'flex';
        
        // 첫 번째 탭 표시
        switchRecommendationTab('high_return');
        
        console.log('ETF 추천 완료:', data);
        
    } catch (error) {
        console.error('ETF 추천 실패:', error);
        contentDiv.innerHTML = `<p style="color: #ef4444;">추천 실패: ${error.message}</p>`;
        tabsDiv.style.display = 'none';
    }
}

// 추천 탭 전환
function switchRecommendationTab(tabKey) {
    if (!currentRecommendationData) return;
    
    currentRecommendationTab = tabKey;
    
    // 탭 버튼 활성화 상태 변경
    document.querySelectorAll('.tab-btn').forEach((btn, idx) => {
        btn.classList.remove('active');
        // 클릭된 탭 찾기
        const tabKeys = ['high_return', 'stable', 'high_dividend', 'monthly_investing', 'popular', 'high_aum', 'balanced'];
        if (tabKeys[idx] === tabKey) {
            btn.classList.add('active');
        }
    });
    
    const contentDiv = document.getElementById('recommendations-content');
    const data = currentRecommendationData;
    
    // 탭 정보
    const tabInfo = {
        'high_return': { title: '고수익형', icon: '📈', desc: 'CAGR 기준 최고 수익률' },
        'stable': { title: '안정형', icon: '🛡️', desc: '낮은 변동성 + 높은 샤프 비율' },
        'high_dividend': { title: '고배당형', icon: '💰', desc: '배당 수익률 기준' },
        'monthly_investing': { title: '적립식 추천', icon: '📅', desc: '낮은 변동성 + 꾸준한 상승세' },
        'popular': { title: '인기순', icon: '🔥', desc: '거래량 기준 인기 ETF' },
        'high_aum': { title: '투자유치 TOP', icon: '💎', desc: '자산총액 기준 대형 ETF' },
        'balanced': { title: '균형형', icon: '⚖️', desc: '수익률 + 안정성 + 배당 종합' }
    };
    
    const info = tabInfo[tabKey];
    const etfs = data[tabKey] || [];
    
    let html = `
        <div style="margin: 20px 0 15px 0; padding: 15px; background: #0f172a; border-radius: 8px; border: 1px solid #334155;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="font-size: 1.5em;">${info.icon}</span>
                <h3 style="color: #f1f5f9; font-size: 1.2em; margin: 0;">${info.title}</h3>
            </div>
            <p style="color: #94a3b8; margin: 0; font-size: 0.9em;">${info.desc}</p>
            <p style="color: #64748b; margin: 8px 0 0 0; font-size: 0.85em;">
                ${data.metadata.total_analyzed}개 ETF 분석 완료 | 기간: ${data.metadata.period}
            </p>
        </div>
    `;
    
    if (etfs.length === 0) {
        html += `<p style="color: #94a3b8; text-align: center; padding: 20px;">해당 카테고리에 추천할 ETF가 없습니다.</p>`;
    } else {
        html += `<div style="display: grid; gap: 10px;">`;
        
        etfs.forEach((etf, index) => {
            const rank = index + 1;
            const cagr_color = etf.cagr >= 15 ? '#10b981' : etf.cagr >= 10 ? '#3b82f6' : etf.cagr >= 5 ? '#f59e0b' : '#94a3b8';
            
            html += `
                <div onclick="addRecommendedETF('${etf.ticker}', '${etf.name.replace(/'/g, "\\'")}', ${etf.cagr.toFixed(2)})" 
                     style="padding: 15px; background: #1e293b; border-radius: 8px; border: 1px solid #334155; display: flex; align-items: center; gap: 15px; cursor: pointer; transition: all 0.2s;"
                     onmouseover="this.style.background='#0f172a'; this.style.borderColor='#3b82f6';"
                     onmouseout="this.style.background='#1e293b'; this.style.borderColor='#334155';">
                    <div style="font-size: 1.5em; font-weight: 700; color: #3b82f6; min-width: 30px;">${rank}</div>
                    <div style="flex: 1;">
                        <div style="color: #f1f5f9; font-weight: 600; margin-bottom: 5px;">${etf.name}</div>
                        <div style="color: #94a3b8; font-size: 0.85em;">${etf.ticker}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: ${cagr_color}; font-size: 1.3em; font-weight: 700; margin-bottom: 3px;">
                            ${etf.cagr >= 0 ? '+' : ''}${etf.cagr.toFixed(2)}%
                        </div>
                        <div style="color: #64748b; font-size: 0.8em;">연평균</div>
                    </div>
                    <div style="text-align: right; min-width: 120px;">
                        <div style="color: #94a3b8; font-size: 0.8em;">샤프: ${etf.sharpe_ratio.toFixed(2)}</div>
                        <div style="color: #94a3b8; font-size: 0.8em;">변동성: ${etf.volatility.toFixed(1)}%</div>
                        ${etf.dividend_yield > 0 ? `<div style="color: #94a3b8; font-size: 0.8em;">배당: ${etf.dividend_yield.toFixed(2)}%</div>` : ''}
                        ${tabKey === 'popular' && etf.avg_volume > 0 ? `<div style="color: #94a3b8; font-size: 0.8em;">거래량: ${(etf.avg_volume / 1000000).toFixed(1)}M</div>` : ''}
                        ${tabKey === 'high_aum' && etf.total_assets > 0 ? `<div style="color: #94a3b8; font-size: 0.8em;">자산: ${(etf.total_assets / 1000000000).toFixed(1)}B</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    contentDiv.innerHTML = html;
}

// 추천 ETF 클릭하여 추가
async function addRecommendedETF(ticker, name, cagr) {
    if (!confirm(`${name} (${ticker})\n연평균 수익률: ${cagr >= 0 ? '+' : ''}${cagr}%\n\n이 ETF를 추가하시겠습니까?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/etf/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticker: ticker,
                name: name
            })
        });
        
        if (response.ok) {
            alert(`✅ ${name} 추가 완료!`);
            loadETFs();
        } else {
            const error = await response.json();
            if (error.detail && error.detail.includes('이미 등록')) {
                alert('이미 추가된 ETF입니다.');
            } else {
                alert(`오류: ${error.detail}`);
            }
        }
    } catch (error) {
        console.error('ETF 추가 실패:', error);
        alert('ETF 추가 중 오류가 발생했습니다.');
    }
}

// 포트폴리오 상관관계 분석
async function loadCorrelation() {
    const period = document.getElementById('correlation-period').value;
    const scoreDiv = document.getElementById('correlation-score');
    const heatmapDiv = document.getElementById('correlation-heatmap');
    
    scoreDiv.innerHTML = '<p>분석 중...</p>';
    heatmapDiv.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/portfolio/correlation?period=${period}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '상관관계 분석 실패');
        }
        
        const data = await response.json();
        
        // 그룹별 결과 표시
        let scoreHTML = '';
        let heatmapHTML = '';
        
        for (const group of data.groups) {
            // 비교 대상 없음 메시지
            if (group.message) {
                scoreHTML += `
                    <div style="padding: 25px; background: #0f172a; border-radius: 12px; color: white; margin-bottom: 20px; border: 2px solid #f59e0b;">
                        <h3 style="margin: 0 0 15px 0; font-size: 1.2em; font-weight: 600; color: #f59e0b;">${group.name}</h3>
                        <p style="margin: 0; font-size: 1.05em; color: #e2e8f0;">📊 ${group.etf_names[0]}</p>
                        <p style="margin: 15px 0 0 0; color: #fbbf24; line-height: 1.6;">💡 ${group.message}</p>
                    </div>
                `;
                continue;
            }
            
            // 에러 메시지
            if (group.error) {
                scoreHTML += `
                    <div style="padding: 20px; background: #fee2e2; border-radius: 10px; border-left: 4px solid #ef4444; margin-bottom: 20px;">
                        <h3 style="margin: 0 0 10px 0; color: #991b1b;">${group.name}</h3>
                        <p style="margin: 0; color: #7f1d1d;">⚠️ ${group.error}</p>
                    </div>
                `;
                continue;
            }
            
            // 정상 분석 결과
            const div = group.diversification;
        
        // 분산투자 점수 표시
        const scoreColor = div.diversification_score >= 80 ? '#10b981' :
                          div.diversification_score >= 60 ? '#3b82f6' :
                          div.diversification_score >= 40 ? '#f59e0b' :
                          div.diversification_score >= 20 ? '#f97316' : '#ef4444';
        
        let highCorrPairsHTML = '';
        if (div.high_correlation_pairs.length > 0) {
            highCorrPairsHTML = `
                <div style="margin-top: 20px; padding: 18px; background: #1e293b; border-radius: 10px; border-left: 4px solid #f59e0b;">
                    <strong style="color: #fbbf24; font-size: 1.05em;">⚠️ 높은 상관관계 ETF 쌍 (0.7 이상)</strong>
                    <ul style="margin: 12px 0; padding-left: 20px; line-height: 1.8; color: #e2e8f0;">
                        ${div.high_correlation_pairs.map(pair => 
                            `<li><strong style="color: #f1f5f9;">${pair.etf1} ↔ ${pair.etf2}:</strong> ${(pair.correlation * 100).toFixed(1)}%</li>`
                        ).join('')}
                    </ul>
                    <p style="font-size: 0.95em; color: #fcd34d; margin-top: 10px;">이 ETF들은 거의 같은 방향으로 움직입니다.</p>
                </div>
            `;
        }
        
            scoreHTML += `
            <div style="padding: 25px; background: #0f172a; border-radius: 12px; color: white; margin-bottom: 20px; border: 1px solid #334155;">
                <h3 style="margin: 0 0 10px 0; font-size: 1.3em; font-weight: 600; color: #f1f5f9;">${group.name}</h3>
                <p style="margin: 0 0 20px 0; color: #94a3b8; font-size: 0.95em;">${group.etf_count}개 ETF 분석</p>
                <h4 style="margin: 0 0 15px 0; font-size: 1em; color: #cbd5e1; font-weight: 500;">분산투자 점수</h4>
                <div style="font-size: 3em; font-weight: bold; margin: 15px 0; color: ${scoreColor}; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
                    ${div.diversification_score}<span style="font-size: 0.5em;">/100</span>
                </div>
                <div style="font-size: 1.2em; margin: 10px 0; font-weight: 600;">
                    ${div.rating}
                </div>
                <p style="margin: 15px 0 0 0; line-height: 1.6; opacity: 0.95;">
                    ${div.advice}
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                <div style="padding: 18px; background: #1e293b; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.85em; color: #94a3b8; margin-bottom: 8px; font-weight: 500;">평균 상관계수</div>
                    <div style="font-size: 1.6em; font-weight: 700; color: #f1f5f9;">${(div.average_correlation * 100).toFixed(1)}%</div>
                </div>
                <div style="padding: 18px; background: #1e293b; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.85em; color: #94a3b8; margin-bottom: 8px; font-weight: 500;">최대 상관계수</div>
                    <div style="font-size: 1.6em; font-weight: 700; color: #f1f5f9;">${(div.max_correlation * 100).toFixed(1)}%</div>
                </div>
                <div style="padding: 18px; background: #1e293b; border-radius: 10px; border: 1px solid #334155;">
                    <div style="font-size: 0.85em; color: #94a3b8; margin-bottom: 8px; font-weight: 500;">최소 상관계수</div>
                    <div style="font-size: 1.6em; font-weight: 700; color: #f1f5f9;">${(div.min_correlation * 100).toFixed(1)}%</div>
                </div>
            </div>
            
            ${highCorrPairsHTML}
            
            <div style="margin-top: 20px; padding: 18px; background: #1e293b; border-radius: 10px; border-left: 4px solid #3b82f6;">
                <strong style="color: #60a5fa; font-size: 1.05em;">💡 상관계수 이해하기</strong>
                <ul style="margin: 12px 0; padding-left: 20px; line-height: 2; color: #cbd5e1;">
                    <li><strong style="color: #f1f5f9;">1.0 (100%):</strong> 완전히 같은 방향 (분산투자 효과 없음)</li>
                    <li><strong style="color: #f1f5f9;">0.7~0.9:</strong> 매우 높은 상관관계</li>
                    <li><strong style="color: #f1f5f9;">0.3~0.7:</strong> 중간 상관관계</li>
                    <li><strong style="color: #f1f5f9;">0.0:</strong> 무관계 (이상적인 분산투자)</li>
                    <li><strong style="color: #f1f5f9;">-1.0:</strong> 완전 반대 방향 (헤지 효과)</li>
                </ul>
            </div>
        `;
            
            // 히트맵 추가
            heatmapHTML += `<div id="heatmap-${group.name.replace(/\s/g, '-')}" style="margin-bottom: 30px;"></div>`;
        }
        
        // 결과 표시
        scoreDiv.innerHTML = scoreHTML;
        heatmapDiv.innerHTML = heatmapHTML;
        
        // 각 그룹의 히트맵 렌더링
        for (const group of data.groups) {
            if (group.heatmap) {
                const heatmapId = `heatmap-${group.name.replace(/\s/g, '-')}`;
                Plotly.newPlot(heatmapId, JSON.parse(group.heatmap).data, JSON.parse(group.heatmap).layout);
            }
        }
        
        console.log('상관관계 분석 완료:', data);
        
    } catch (error) {
        console.error('상관관계 분석 실패:', error);
        scoreDiv.innerHTML = `<p style="color: #ef4444;">❌ ${error.message}</p>`;
        
        if (error.message.includes('최소 2개')) {
            scoreDiv.innerHTML += `<p style="color: #6b7280;">ETF를 2개 이상 추가한 후 분석해주세요.</p>`;
        }
    }
}

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeDBModal();
    }
});

