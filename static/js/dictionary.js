// 주식 용어사전 JavaScript

const API_BASE = '/api/v1/dictionary';

// 페이지 로드 시 전체 용어 표시
document.addEventListener('DOMContentLoaded', () => {
    filterCategory('all');
    
    // Enter 키로 검색
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchTerms();
        }
    });
});

// 검색 기능
async function searchTerms() {
    const query = document.getElementById('search-input').value.trim();
    const resultsDiv = document.getElementById('search-results');
    const container = document.getElementById('terms-container');
    
    if (!query) {
        resultsDiv.textContent = '';
        filterCategory('all');
        return;
    }
    
    container.innerHTML = '<div class="loading">검색 중</div>';
    
    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.results.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>검색 결과가 없습니다</h3>
                    <p>"${query}"에 대한 결과를 찾을 수 없습니다.</p>
                </div>
            `;
            resultsDiv.textContent = '';
        } else {
            renderTerms(data.results);
            resultsDiv.textContent = `"${query}" 검색 결과: ${data.results.length}개`;
        }
    } catch (error) {
        console.error('검색 실패:', error);
        container.innerHTML = `
            <div class="empty-state">
                <h3>오류가 발생했습니다</h3>
                <p>검색 중 문제가 발생했습니다. 다시 시도해주세요.</p>
            </div>
        `;
    }
}

// 카테고리 필터
async function filterCategory(category) {
    const container = document.getElementById('terms-container');
    const resultsDiv = document.getElementById('search-results');
    
    // 탭 활성화 상태 변경
    document.querySelectorAll('.category-tab').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target?.classList.add('active');
    
    // 검색창 초기화
    document.getElementById('search-input').value = '';
    resultsDiv.textContent = '';
    
    container.innerHTML = '<div class="loading">로딩 중</div>';
    
    try {
        let url = `${API_BASE}/categories`;
        let data;
        
        if (category !== 'all') {
            url += `/${encodeURIComponent(category)}`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }
            data = await response.json();
        } else {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }
            data = await response.json();
        }
        
        if (category === 'all') {
            // 전체 카테고리의 모든 용어 표시
            const allTerms = [];
            for (const [cat, terms] of Object.entries(data.terms)) {
                for (const term of Object.values(terms)) {
                    allTerms.push({ ...term, category: cat });
                }
            }
            renderTerms(allTerms);
        } else {
            // 특정 카테고리 용어만 표시
            const terms = Object.values(data.terms).map(term => ({
                ...term,
                category: category
            }));
            renderTerms(terms);
        }
    } catch (error) {
        console.error('카테고리 로딩 실패:', error);
        container.innerHTML = `
            <div class="empty-state">
                <h3>오류가 발생했습니다</h3>
                <p>용어를 불러올 수 없습니다. 페이지를 새로고침해주세요.</p>
            </div>
        `;
    }
}

// 용어 카드 렌더링
function renderTerms(terms) {
    const container = document.getElementById('terms-container');
    
    if (terms.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>용어가 없습니다</h3>
            </div>
        `;
        return;
    }
    
    container.innerHTML = terms.map(term => createTermCard(term)).join('');
}

// 용어 카드 HTML 생성
function createTermCard(term) {
    const categoryClass = getCategoryClass(term.category);
    
    let cardHTML = `
        <div class="term-card">
            <div class="term-header">
                <h3 class="term-title">${term.term}</h3>
                <span class="term-category ${categoryClass}">${term.category}</span>
            </div>
    `;
    
    if (term.english) {
        cardHTML += `<div class="term-english">${term.english}</div>`;
    }
    
    cardHTML += `<p class="term-description">${term.description}</p>`;
    
    if (term.example) {
        cardHTML += `
            <div class="term-example">
                <div class="term-example-label">예시</div>
                <div class="term-example-text">"${term.example}"</div>
            </div>
        `;
    }
    
    if (term.formula) {
        cardHTML += `
            <div class="term-formula">
                <strong>공식:</strong> ${term.formula}
            </div>
        `;
    }
    
    if (term.warning) {
        cardHTML += `
            <div class="term-warning">
                ${term.warning}
            </div>
        `;
    }
    
    if (term.tip) {
        cardHTML += `
            <div class="term-tip">
                <strong>💡 TIP:</strong> ${term.tip}
            </div>
        `;
    }
    
    if (term.related) {
        cardHTML += `
            <div class="term-related">
                <strong>관련 용어:</strong> ${term.related}
            </div>
        `;
    }
    
    if (term.emoji) {
        cardHTML += `
            <div style="text-align: center; font-size: 2em; margin-top: 10px;">
                ${term.emoji}
            </div>
        `;
    }
    
    if (term.meme) {
        cardHTML += `
            <div style="text-align: center; font-size: 1.5em; margin-top: 10px;">
                ${term.meme}
            </div>
        `;
    }
    
    cardHTML += `</div>`;
    
    return cardHTML;
}

// 카테고리별 CSS 클래스
function getCategoryClass(category) {
    if (category.includes('은어') || category.includes('밈')) {
        return '슬랭';
    } else if (category.includes('ETF')) {
        return 'ETF';
    } else if (category.includes('지표')) {
        return '지표';
    }
    return '';
}

