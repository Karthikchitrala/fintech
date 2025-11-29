// API Configuration
const API_BASE = 'http://localhost:8000';
let currentToken = null;
let currentUser = null;

// DOM Elements
const authModal = document.getElementById('authModal');
const protectedContent = document.getElementById('protectedContent');
const publicFeatures = document.getElementById('publicFeatures');
const authButtons = document.getElementById('authButtons');
const userMenu = document.getElementById('userMenu');
const userGreeting = document.getElementById('userGreeting');
const navLinks = document.getElementById('navLinks');
const heroSection = document.querySelector('.gradient-bg');

// Utility Functions
function showLoading(element) {
    element.innerHTML = `
        <div class="flex justify-center items-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span class="ml-3 text-gray-600">Loading real-time data...</span>
        </div>
    `;
}

function showError(element, message) {
    element.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-center">
                <i class="fas fa-exclamation-triangle text-red-600 mr-3"></i>
                <span class="text-red-800">${message}</span>
            </div>
        </div>
    `;
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 fade-in';
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-check-circle mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Authentication Functions
function showAuthModal() {
    authModal.classList.remove('hidden');
    showLoginForm();
}

function hideAuthModal() {
    authModal.classList.add('hidden');
}

function showLoginForm() {
    document.getElementById('loginForm').classList.remove('hidden');
    document.getElementById('signupForm').classList.add('hidden');
    document.getElementById('authTitle').textContent = 'Welcome Back to FinPulse';
}

function showSignupForm() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.remove('hidden');
    document.getElementById('authTitle').textContent = 'Join FinPulse Today';
}

async function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!username || !password) {
        alert('Please enter both username and password');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE}/token`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            currentToken = data.access_token;
            await loadUserProfile();
            hideAuthModal();
            showSuccess('Successfully signed in! Loading real-time data...');
        } else {
            throw new Error('Invalid credentials');
        }
    } catch (error) {
        alert('Login failed. Please check your credentials.');
        console.error('Login error:', error);
    }
}

async function signup() {
    const userData = {
        username: document.getElementById('signupUsername').value,
        email: document.getElementById('signupEmail').value,
        full_name: document.getElementById('signupName').value,
        password: document.getElementById('signupPassword').value
    };
    
    if (!userData.username || !userData.email || !userData.full_name || !userData.password) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            showLoginForm();
            document.getElementById('loginUsername').value = userData.username;
            showSuccess('Account created successfully! Please sign in.');
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }
    } catch (error) {
        alert('Registration failed: ' + error.message);
        console.error('Signup error:', error);
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE}/users/me`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            updateUIForUser();
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

function updateUIForUser() {
    heroSection.classList.add('hidden');
    publicFeatures.classList.add('hidden');
    protectedContent.classList.remove('hidden');
    
    userGreeting.textContent = `Hello, ${currentUser.full_name}`;
    userMenu.classList.remove('hidden');
    authButtons.classList.add('hidden');
    navLinks.classList.remove('hidden');
    
    setTimeout(() => {
        document.getElementById('dashboard').scrollIntoView({ behavior: 'smooth' });
    }, 500);
}

function logout() {
    currentToken = null;
    currentUser = null;
    
    heroSection.classList.remove('hidden');
    publicFeatures.classList.remove('hidden');
    protectedContent.classList.add('hidden');
    
    userMenu.classList.add('hidden');
    authButtons.classList.remove('hidden');
    navLinks.classList.add('hidden');
    
    localStorage.removeItem('finpulse_token');
    showSuccess('Successfully logged out');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Dashboard Functions
async function loadDashboardData() {
    await loadMarketOverview();
    await loadPortfolioAnalysis();
    await loadOpportunities();
}

async function loadMarketOverview() {
    try {
        const response = await fetch(`${API_BASE}/api/market/overview`);
        if (response.ok) {
            const data = await response.json();
            updateMarketOverview(data);
        }
    } catch (error) {
        console.error('Error loading market overview:', error);
    }
}

function updateMarketOverview(data) {
    const dashboard = document.getElementById('dashboard');
    if (dashboard) {
        let marketElement = document.getElementById('marketOverview');
        if (!marketElement) {
            marketElement = document.createElement('div');
            marketElement.id = 'marketOverview';
            marketElement.className = 'bg-white rounded-xl shadow-lg p-6 mb-8';
            dashboard.insertBefore(marketElement, dashboard.firstChild);
        }
        
        marketElement.innerHTML = `
            <h3 class="text-xl font-semibold mb-4">📊 Live Market Overview</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center p-4 ${data.market_sentiment === 'Bullish' ? 'bg-green-50 border border-green-200' : data.market_sentiment === 'Bearish' ? 'bg-red-50 border border-red-200' : 'bg-yellow-50 border border-yellow-200'} rounded-lg">
                    <div class="text-sm ${data.market_sentiment === 'Bullish' ? 'text-green-600' : data.market_sentiment === 'Bearish' ? 'text-red-600' : 'text-yellow-600'} mb-1">Market Sentiment</div>
                    <div class="text-lg font-semibold ${data.market_sentiment === 'Bullish' ? 'text-green-600' : data.market_sentiment === 'Bearish' ? 'text-red-600' : 'text-yellow-600'}">${data.market_sentiment}</div>
                </div>
                <div class="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div class="text-sm text-blue-600 mb-1">S&P 500 (SPY)</div>
                    <div class="text-lg font-semibold ${data.spy_performance >= 0 ? 'text-green-600' : 'text-red-600'}">${data.spy_performance >= 0 ? '+' : ''}${data.spy_performance}%</div>
                </div>
                <div class="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <div class="text-sm text-purple-600 mb-1">Data Source</div>
                    <div class="text-lg font-semibold">Live Market</div>
                </div>
            </div>
            ${data.is_real_data ? '<p class="text-green-600 text-sm mt-3"><i class="fas fa-check-circle mr-1"></i> Real-time data</p>' : '<p class="text-yellow-600 text-sm mt-3"><i class="fas fa-info-circle mr-1"></i> Using fallback data</p>'}
        `;
    }
}

async function loadPortfolioAnalysis() {
    try {
        const response = await fetch(`${API_BASE}/api/portfolio/analysis`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const portfolio = await response.json();
            updateDashboard(portfolio);
        }
    } catch (error) {
        console.error('Error loading portfolio:', error);
    }
}

function updateDashboard(portfolio) {
    document.getElementById('portfolioValue').textContent = `$${portfolio.total_current_value.toLocaleString()}`;
    document.getElementById('portfolioChange').textContent = 
        `${portfolio.total_gain_loss >= 0 ? '+' : ''}${portfolio.total_gain_loss_percent.toFixed(2)}%`;
    document.getElementById('cashBalance').textContent = `$${portfolio.cash_balance.toLocaleString()}`;
    document.getElementById('riskLevel').textContent = portfolio.overall_risk;
    document.getElementById('diversificationScore').textContent = `Diversification: ${portfolio.diversification_score}/100`;
    
    const portfolioOverview = document.getElementById('portfolioOverview');
    portfolioOverview.innerHTML = `
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div>
                <h4 class="text-sm font-medium text-gray-600">Total Invested</h4>
                <p class="text-xl font-semibold">$${portfolio.total_invested.toLocaleString()}</p>
            </div>
            <div>
                <h4 class="text-sm font-medium text-gray-600">Current Value</h4>
                <p class="text-xl font-semibold">$${portfolio.total_current_value.toLocaleString()}</p>
            </div>
            <div>
                <h4 class="text-sm font-medium text-gray-600">Total Gain/Loss</h4>
                <p class="text-xl font-semibold ${portfolio.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}">
                    $${portfolio.total_gain_loss.toLocaleString()} (${portfolio.total_gain_loss_percent.toFixed(2)}%)
                </p>
            </div>
            <div>
                <h4 class="text-sm font-medium text-gray-600">Cash Balance</h4>
                <p class="text-xl font-semibold">$${portfolio.cash_balance.toLocaleString()}</p>
            </div>
        </div>
        
        <div class="mb-6">
            <h4 class="text-lg font-semibold mb-3">📈 Holdings (Live Prices)</h4>
            <div class="space-y-3">
                ${portfolio.holdings.map(holding => `
                    <div class="flex justify-between items-center p-4 bg-gray-50 rounded-lg border border-gray-200">
                        <div class="flex items-center space-x-3">
                            <span class="font-semibold text-lg">${holding.symbol}</span>
                            <span class="text-sm text-gray-600">${holding.shares} shares</span>
                        </div>
                        <div class="text-right">
                            <div class="font-semibold text-lg">$${holding.current_value.toLocaleString()}</div>
                            <div class="text-sm ${holding.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}">
                                ${holding.gain_loss >= 0 ? '+' : ''}$${holding.gain_loss.toLocaleString()} (${holding.gain_loss_percent.toFixed(2)}%)
                            </div>
                            <div class="text-xs text-gray-500">Current: $${holding.current_price}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div>
            <h4 class="text-lg font-semibold mb-3">🤖 AI Insights</h4>
            <div class="space-y-2">
                ${portfolio.ai_insights.map(insight => `
                    <div class="flex items-center text-blue-600 bg-blue-50 p-3 rounded-lg">
                        <i class="fas fa-robot mr-3 text-blue-500"></i>
                        <span class="font-medium">${insight}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Stock Analysis Functions
async function analyzeStock() {
    const symbol = document.getElementById('stockSearch').value.trim();
    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }
    
    const analysisResults = document.getElementById('analysisResults');
    analysisResults.classList.remove('hidden');
    
    await loadPulseScore(symbol);
    await loadRiskRadar(symbol);
    await loadHedgeSuggestions(symbol);
}

async function loadPulseScore(symbol) {
    const display = document.getElementById('pulseScoreDisplay');
    showLoading(display);
    
    try {
        const response = await fetch(`${API_BASE}/api/pulsescore/${symbol}`);
        if (response.ok) {
            const data = await response.json();
            displayPulseScore(data);
        } else {
            throw new Error('Failed to load PulseScore');
        }
    } catch (error) {
        showError(display, 'Error loading PulseScore analysis');
    }
}

function displayPulseScore(data) {
    const display = document.getElementById('pulseScoreDisplay');
    
    display.innerHTML = `
        <div class="text-center mb-6">
            <div class="w-40 h-40 ${getPulseScoreClass(data.pulsescore)} rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                <span class="text-4xl font-bold text-white">${data.pulsescore}</span>
            </div>
            <h4 class="text-2xl font-semibold ${data.color} mb-2">${data.trend}</h4>
            <p class="text-lg text-gray-600">Recommendation: <strong>${data.recommendation}</strong></p>
            <p class="text-gray-500">Confidence: ${data.confidence}%</p>
            ${data.is_real_data ? '<p class="text-green-600 text-sm mt-2"><i class="fas fa-bolt mr-1"></i> Live market data</p>' : '<p class="text-yellow-600 text-sm mt-2"><i class="fas fa-database mr-1"></i> Using fallback data</p>'}
        </div>
        
        <div class="mb-6">
            <h5 class="font-semibold text-gray-700 mb-3">Technical Indicators</h5>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div class="text-center p-3 bg-blue-50 rounded-lg">
                    <div class="text-sm text-blue-600 mb-1">RSI</div>
                    <div class="text-lg font-semibold ${data.technical_indicators?.rsi > 70 ? 'text-red-600' : data.technical_indicators?.rsi < 30 ? 'text-green-600' : 'text-gray-700'}">${data.technical_indicators?.rsi || 'N/A'}</div>
                </div>
                <div class="text-center p-3 bg-green-50 rounded-lg">
                    <div class="text-sm text-green-600 mb-1">MACD</div>
                    <div class="text-lg font-semibold">${data.technical_indicators?.macd || 'N/A'}</div>
                </div>
                <div class="text-center p-3 bg-purple-50 rounded-lg">
                    <div class="text-sm text-purple-600 mb-1">vs SMA20</div>
                    <div class="text-lg font-semibold ${data.technical_indicators?.price_vs_sma20 > 0 ? 'text-green-600' : 'text-red-600'}">${data.technical_indicators?.price_vs_sma20 || 'N/A'}%</div>
                </div>
                <div class="text-center p-3 bg-orange-50 rounded-lg">
                    <div class="text-sm text-orange-600 mb-1">Volume Ratio</div>
                    <div class="text-lg font-semibold">${data.technical_indicators?.volume_ratio || 'N/A'}x</div>
                </div>
            </div>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center p-3 bg-blue-50 rounded-lg">
                <div class="text-sm text-blue-600 mb-1">Momentum</div>
                <div class="text-xl font-semibold">${data.breakdown.momentum}</div>
            </div>
            <div class="text-center p-3 bg-green-50 rounded-lg">
                <div class="text-sm text-green-600 mb-1">Trend</div>
                <div class="text-xl font-semibold">${data.breakdown.trend}</div>
            </div>
            <div class="text-center p-3 bg-purple-50 rounded-lg">
                <div class="text-sm text-purple-600 mb-1">Volume</div>
                <div class="text-xl font-semibold">${data.breakdown.volume}</div>
            </div>
            <div class="text-center p-3 bg-orange-50 rounded-lg">
                <div class="text-sm text-orange-600 mb-1">RSI</div>
                <div class="text-xl font-semibold">${data.breakdown.rsi}</div>
            </div>
        </div>
    `;
}

async function loadRiskRadar(symbol) {
    const display = document.getElementById('riskRadarDisplay');
    showLoading(display);
    
    try {
        const response = await fetch(`${API_BASE}/api/risk/${symbol}`);
        if (response.ok) {
            const data = await response.json();
            displayRiskRadar(data);
        } else {
            throw new Error('Failed to load risk analysis');
        }
    } catch (error) {
        showError(display, 'Error loading risk analysis');
    }
}

function displayRiskRadar(data) {
    const display = document.getElementById('riskRadarDisplay');
    
    display.innerHTML = `
        <div class="flex justify-between items-center mb-6">
            <div>
                <span class="text-2xl font-semibold ${getRiskColor(data.color)}">${data.risk_level} Risk</span>
                <div class="text-gray-600">Risk Score: ${data.risk_score}/100</div>
                ${data.is_real_data ? '<p class="text-green-600 text-sm mt-1"><i class="fas fa-bolt mr-1"></i> Real volatility data</p>' : '<p class="text-yellow-600 text-sm mt-1"><i class="fas fa-database mr-1"></i> Using estimated data</p>'}
            </div>
            <div class="w-20 h-20 ${getRiskClass(data.risk_level)} rounded-full flex items-center justify-center text-white font-semibold">
                ${data.risk_level}
            </div>
        </div>
        
        <div class="grid md:grid-cols-2 gap-6">
            <div class="space-y-4">
                <h5 class="font-semibold text-gray-700">Key Risk Metrics</h5>
                <div class="space-y-3">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Volatility:</span>
                        <span class="font-semibold ${data.volatility > 0.3 ? 'text-red-600' : data.volatility > 0.2 ? 'text-orange-600' : 'text-green-600'}">${data.volatility}</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Max Drawdown:</span>
                        <span class="font-semibold text-red-600">-${data.max_drawdown}%</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Sharpe Ratio:</span>
                        <span class="font-semibold ${data.sharpe_ratio > 1 ? 'text-green-600' : data.sharpe_ratio > 0 ? 'text-yellow-600' : 'text-red-600'}">${data.sharpe_ratio}</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Beta:</span>
                        <span class="font-semibold">${data.beta}</span>
                    </div>
                </div>
            </div>
            
            <div>
                <h5 class="font-semibold text-gray-700 mb-3">Stress Test Scenarios</h5>
                <div class="space-y-2">
                    <div class="flex justify-between items-center text-red-600">
                        <span>Market Crash:</span>
                        <span class="font-semibold">${data.stress_test.market_crash}%</span>
                    </div>
                    <div class="flex justify-between items-center text-orange-600">
                        <span>Recession:</span>
                        <span class="font-semibold">${data.stress_test.recession}%</span>
                    </div>
                    <div class="flex justify-between items-center text-yellow-600">
                        <span>Volatility Spike:</span>
                        <span class="font-semibold">${data.stress_test.volatility_spike}%</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function loadHedgeSuggestions(symbol) {
    const display = document.getElementById('hedgeEngineDisplay');
    showLoading(display);
    
    try {
        const response = await fetch(`${API_BASE}/api/hedge/${symbol}`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayHedgeSuggestions(data);
        } else {
            throw new Error('Failed to load hedge suggestions');
        }
    } catch (error) {
        showError(display, 'Error loading hedge suggestions');
    }
}

function displayHedgeSuggestions(data) {
    const display = document.getElementById('hedgeEngineDisplay');
    
    display.innerHTML = `
        <div class="mb-4">
            <div class="flex items-center justify-between mb-2">
                <span class="text-lg font-semibold">Hedge Effectiveness</span>
                <span class="text-2xl font-bold text-green-600">${data.hedge_score}%</span>
            </div>
            <p class="text-gray-600">${data.portfolio_impact}</p>
        </div>
        
        <div class="space-y-4">
            ${data.suggestions.map(suggestion => `
                <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                    <div class="flex justify-between items-start mb-2">
                        <div>
                            <h6 class="font-semibold">${suggestion.type}</h6>
                            <p class="text-sm text-gray-600">${suggestion.symbol}</p>
                        </div>
                        <span class="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded">${suggestion.effectiveness}% effective</span>
                    </div>
                    <p class="text-sm text-gray-700 mb-2">${suggestion.description}</p>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-500">Cost: ${suggestion.cost}</span>
                        <button class="text-blue-600 hover:text-blue-700 font-semibold">
                            Implement Strategy
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Opportunities Functions
async function loadOpportunities() {
    const display = document.getElementById('opportunitiesDisplay');
    showLoading(display);
    
    try {
        const response = await fetch(`${API_BASE}/api/opportunities`);
        if (response.ok) {
            const data = await response.json();
            displayOpportunities(data.opportunities);
        } else {
            throw new Error('Failed to load opportunities');
        }
    } catch (error) {
        showError(display, 'Error loading market opportunities');
    }
}

function displayOpportunities(opportunities) {
    const display = document.getElementById('opportunitiesDisplay');
    
    if (opportunities.length === 0) {
        display.innerHTML = `
            <div class="col-span-full text-center py-8">
                <i class="fas fa-search text-gray-400 text-4xl mb-4"></i>
                <h3 class="text-xl font-semibold text-gray-600 mb-2">No strong opportunities detected</h3>
                <p class="text-gray-500">Check back later for new market opportunities</p>
            </div>
        `;
        return;
    }
    
    display.innerHTML = opportunities.map(opp => `
        <div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition">
            <div class="flex justify-between items-start mb-3">
                <div>
                    <h3 class="text-xl font-semibold">${opp.symbol}</h3>
                    <p class="text-gray-600">${opp.name}</p>
                </div>
                <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                    ${opp.type}
                </span>
            </div>
            
            <div class="space-y-3 mb-4">
                <div class="flex justify-between">
                    <span class="text-gray-600">Confidence:</span>
                    <span class="font-semibold">${opp.confidence}%</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Potential Return:</span>
                    <span class="font-semibold text-green-600">+${opp.potential_return}%</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Current Change:</span>
                    <span class="font-semibold ${opp.current_change >= 0 ? 'text-green-600' : 'text-red-600'}">${opp.current_change >= 0 ? '+' : ''}${opp.current_change}%</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Current Price:</span>
                    <span class="font-semibold">$${opp.current_price}</span>
                </div>
            </div>
            
            ${opp.reasoning && opp.reasoning.length > 0 ? `
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                    <div class="flex items-start">
                        <i class="fas fa-robot text-blue-600 mt-1 mr-2"></i>
                        <div>
                            <p class="text-sm text-blue-800 font-semibold">AI Analysis:</p>
                            <p class="text-sm text-blue-700">${opp.reasoning[0]}</p>
                        </div>
                    </div>
                </div>
            ` : ''}
            
            ${opp.is_real_data ? '<p class="text-green-600 text-sm mb-3"><i class="fas fa-bolt mr-1"></i> Live market data</p>' : '<p class="text-yellow-600 text-sm mb-3"><i class="fas fa-database mr-1"></i> Estimated data</p>'}
            
            <div class="flex space-x-2">
                <button onclick="analyzeStockManual('${opp.symbol}')" class="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition text-sm">
                    Analyze
                </button>
                <button onclick="quickTrade('${opp.symbol}', 'buy')" class="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition text-sm">
                    Quick Buy
                </button>
            </div>
        </div>
    `).join('');
}

function analyzeStockManual(symbol) {
    document.getElementById('stockSearch').value = symbol;
    analyzeStock();
}

// Trading Functions
async function executeTrade(action) {
    const symbol = document.getElementById('tradeSymbol').value.trim();
    const shares = parseInt(document.getElementById('tradeShares').value);
    
    if (!symbol || !shares || shares <= 0) {
        alert('Please enter valid symbol and share quantity');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/trade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                symbol: symbol,
                shares: shares,
                action: action
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showSuccess(result.message);
            await loadPortfolioAnalysis();
            document.getElementById('tradeSymbol').value = '';
            document.getElementById('tradeShares').value = '';
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Trade failed');
        }
    } catch (error) {
        alert('Trade failed: ' + error.message);
    }
}

async function quickTrade(symbol, action) {
    const shares = prompt(`How many shares of ${symbol} do you want to ${action}?`, "10");
    if (shares && !isNaN(shares)) {
        document.getElementById('tradeSymbol').value = symbol;
        document.getElementById('tradeShares').value = shares;
        await executeTrade(action);
    }
}

// Utility Functions
function getPulseScoreClass(score) {
    if (score >= 80) return 'pulse-score-excellent';
    if (score >= 60) return 'pulse-score-good';
    if (score >= 40) return 'pulse-score-moderate';
    return 'pulse-score-weak';
}

function getRiskClass(riskLevel) {
    const riskMap = {
        'Low': 'risk-low',
        'Medium': 'risk-medium',
        'High': 'risk-high'
    };
    return riskMap[riskLevel] || 'risk-medium';
}

function getRiskColor(color) {
    const colorMap = {
        'green': 'text-green-600',
        'orange': 'text-orange-600',
        'red': 'text-red-600'
    };
    return colorMap[color] || 'text-gray-600';
}

function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({ 
        behavior: 'smooth' 
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    const savedToken = localStorage.getItem('finpulse_token');
    if (savedToken) {
        currentToken = savedToken;
        loadUserProfile();
    }
    
    document.getElementById('stockSearch').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeStock();
        }
    });
    
    // Save token to localStorage when available
    const originalLoadUserProfile = loadUserProfile;
    loadUserProfile = async function() {
        await originalLoadUserProfile();
        if (currentToken) {
            localStorage.setItem('finpulse_token', currentToken);
        }
    };
});