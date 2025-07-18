/**
 * GamePlayer-Raspberry Web Interface
 * 游戏启动器Web界面主要JavaScript文件
 */

class GamePlayerApp {
    constructor() {
        this.currentSystem = null;
        this.games = {};
        this.settings = this.loadSettings();
        this.stats = this.loadStats();
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSystemData();
        this.updateUI();
        this.checkSystemStatus();
    }

    bindEvents() {
        // 导航按钮事件
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.nav-btn').dataset.tab);
            });
        });

        // 系统卡片点击事件
        document.querySelectorAll('.system-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const system = e.target.closest('.system-card').dataset.system;
                this.showGames(system);
            });
        });

        // 返回按钮
        document.getElementById('backBtn').addEventListener('click', () => {
            this.showSystemSelector();
        });

        // 搜索功能
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filterGames(e.target.value);
        });

        // 刷新按钮
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshData();
        });

        // 模态框事件
        document.getElementById('closeModal').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('cancelBtn').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('launchGameBtn').addEventListener('click', () => {
            this.launchSelectedGame();
        });

        // 设置事件
        this.bindSettingsEvents();

        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });

        // 模态框背景点击关闭
        document.getElementById('gameModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.closeModal();
            }
        });
    }

    bindSettingsEvents() {
        // 音量滑块
        const volumeSlider = document.getElementById('volume');
        const volumeValue = document.getElementById('volumeValue');
        
        volumeSlider.addEventListener('input', (e) => {
            volumeValue.textContent = e.target.value + '%';
            this.settings.audio.volume = parseInt(e.target.value);
        });

        // 保存设置
        document.getElementById('saveSettingsBtn').addEventListener('click', () => {
            this.saveSettings();
        });

        // 重置设置
        document.getElementById('resetSettingsBtn').addEventListener('click', () => {
            this.resetSettings();
        });

        // 实时设置更新
        ['fullscreen', 'audioEnabled', 'gamepadEnabled', 'autoDetectGamepad'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', (e) => {
                    this.updateSetting(id, e.target.checked);
                });
            }
        });

        document.getElementById('resolution').addEventListener('change', (e) => {
            this.updateSetting('resolution', e.target.value);
        });
    }

    switchTab(tabName) {
        // 更新导航按钮状态
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // 切换标签页内容
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName + 'Tab').classList.add('active');

        // 特殊处理
        if (tabName === 'stats') {
            this.updateStats();
        }
    }

    async loadSystemData() {
        this.showLoading(true);
        
        try {
            // 模拟API调用获取系统数据
            const response = await this.fetchAPI('/api/systems');
            this.games = response.games || {};
            
            // 更新游戏数量显示
            this.updateGameCounts();
            
        } catch (error) {
            console.error('加载系统数据失败:', error);
            this.showNotification('加载数据失败', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    updateGameCounts() {
        const systems = ['nes', 'snes', 'gameboy', 'gba', 'genesis'];
        
        systems.forEach(system => {
            const count = this.games[system] ? this.games[system].length : 0;
            const countElement = document.getElementById(system + 'Count');
            if (countElement) {
                countElement.textContent = `${count} 个游戏`;
            }
        });
    }

    async showGames(system) {
        this.currentSystem = system;
        
        // 隐藏系统选择器，显示游戏列表
        document.querySelector('.system-selector').style.display = 'none';
        document.getElementById('gameSection').style.display = 'block';
        
        // 更新标题
        const systemNames = {
            'nes': 'NES 游戏',
            'snes': 'SNES 游戏',
            'gameboy': 'Game Boy 游戏',
            'gba': 'GBA 游戏',
            'genesis': 'Genesis 游戏'
        };
        
        document.getElementById('systemTitle').textContent = systemNames[system] || '游戏列表';
        
        // 加载游戏列表
        await this.loadGames(system);
    }

    async loadGames(system) {
        this.showLoading(true);
        
        try {
            const response = await this.fetchAPI(`/api/games/${system}`);
            const games = response.games || [];
            
            this.renderGames(games);
            
        } catch (error) {
            console.error('加载游戏列表失败:', error);
            this.showNotification('加载游戏列表失败', 'error');
            this.renderGames([]);
        } finally {
            this.showLoading(false);
        }
    }

    renderGames(games) {
        const gameGrid = document.getElementById('gameGrid');
        
        if (games.length === 0) {
            gameGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <i class="fas fa-gamepad" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>此系统暂无游戏</p>
                    <p style="font-size: 0.9rem;">请将ROM文件放入相应的文件夹中</p>
                </div>
            `;
            return;
        }

        gameGrid.innerHTML = games.map(game => `
            <div class="game-card" data-game='${JSON.stringify(game)}'>
                <div class="game-cover">
                    <i class="fas fa-gamepad"></i>
                </div>
                <div class="game-info">
                    <div class="game-name">${game.name}</div>
                    <div class="game-system">${game.system.toUpperCase()}</div>
                </div>
            </div>
        `).join('');

        // 绑定游戏卡片点击事件
        gameGrid.querySelectorAll('.game-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const gameData = JSON.parse(e.target.closest('.game-card').dataset.game);
                this.showGameModal(gameData);
            });
        });
    }

    filterGames(searchTerm) {
        const gameCards = document.querySelectorAll('.game-card');
        
        gameCards.forEach(card => {
            const gameName = card.querySelector('.game-name').textContent.toLowerCase();
            const isMatch = gameName.includes(searchTerm.toLowerCase());
            
            card.style.display = isMatch ? 'block' : 'none';
        });
    }

    showGameModal(game) {
        const modal = document.getElementById('gameModal');
        
        // 更新模态框内容
        document.getElementById('gameTitle').textContent = game.name;
        document.getElementById('gameSystem').textContent = game.system.toUpperCase();
        document.getElementById('gameFile').textContent = game.filename;
        document.getElementById('gameSize').textContent = game.size || '未知';
        
        // 存储当前选中的游戏
        modal.dataset.currentGame = JSON.stringify(game);
        
        // 显示模态框
        modal.classList.add('active');
    }

    closeModal() {
        document.getElementById('gameModal').classList.remove('active');
    }

    async launchSelectedGame() {
        const modal = document.getElementById('gameModal');
        const game = JSON.parse(modal.dataset.currentGame);
        const saveSlot = document.getElementById('saveSlot').value;
        const cheatsEnabled = document.getElementById('cheatsEnabled').checked;
        
        this.showLoading(true);
        
        try {
            const response = await this.fetchAPI('/api/launch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    system: game.system,
                    game: game.filename,
                    saveSlot: parseInt(saveSlot),
                    cheats: cheatsEnabled
                })
            });
            
            if (response.success) {
                this.showNotification(`正在启动 ${game.name}`, 'success');
                this.closeModal();
                
                // 更新统计
                this.updateGameStats(game);
            } else {
                throw new Error(response.error || '启动游戏失败');
            }
            
        } catch (error) {
            console.error('启动游戏失败:', error);
            this.showNotification(`启动失败: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    showSystemSelector() {
        document.querySelector('.system-selector').style.display = 'block';
        document.getElementById('gameSection').style.display = 'none';
        document.getElementById('searchInput').value = '';
    }

    async refreshData() {
        this.showNotification('正在刷新数据...', 'info');
        await this.loadSystemData();
        
        if (this.currentSystem) {
            await this.loadGames(this.currentSystem);
        }
        
        this.showNotification('数据刷新完成', 'success');
    }

    async checkSystemStatus() {
        try {
            const response = await this.fetchAPI('/api/status');
            const statusElement = document.getElementById('systemStatus');
            
            if (response.online) {
                statusElement.innerHTML = '<i class="fas fa-circle"></i><span>在线</span>';
                statusElement.style.color = 'var(--success-color)';
            } else {
                statusElement.innerHTML = '<i class="fas fa-circle"></i><span>离线</span>';
                statusElement.style.color = 'var(--error-color)';
            }
        } catch (error) {
            const statusElement = document.getElementById('systemStatus');
            statusElement.innerHTML = '<i class="fas fa-circle"></i><span>连接错误</span>';
            statusElement.style.color = 'var(--warning-color)';
        }
    }

    async fetchAPI(url, options = {}) {
        // 模拟API调用 - 在实际环境中这里会连接到后端服务
        await this.sleep(500); // 模拟网络延迟
        
        // 根据URL返回模拟数据
        if (url === '/api/systems') {
            return {
                games: {
                    nes: Array.from({length: 5}, (_, i) => ({
                        name: `NES游戏 ${i + 1}`,
                        filename: `game${i + 1}.nes`,
                        system: 'nes',
                        size: '256KB'
                    })),
                    snes: Array.from({length: 3}, (_, i) => ({
                        name: `SNES游戏 ${i + 1}`,
                        filename: `game${i + 1}.smc`,
                        system: 'snes',
                        size: '512KB'
                    })),
                    gameboy: [],
                    gba: [],
                    genesis: []
                }
            };
        }
        
        if (url.startsWith('/api/games/')) {
            const system = url.split('/').pop();
            return {
                games: this.games[system] || []
            };
        }
        
        if (url === '/api/status') {
            return { online: true };
        }
        
        if (url === '/api/launch') {
            return { success: true };
        }
        
        throw new Error('API endpoint not found');
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.add('active');
        } else {
            loading.classList.remove('active');
        }
    }

    showNotification(message, type = 'info') {
        const notifications = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const typeIcons = {
            info: 'fas fa-info-circle',
            success: 'fas fa-check-circle',
            warning: 'fas fa-exclamation-triangle',
            error: 'fas fa-times-circle'
        };
        
        notification.innerHTML = `
            <div class="notification-title">
                <i class="${typeIcons[type] || typeIcons.info}"></i>
                ${message}
            </div>
        `;
        
        notifications.appendChild(notification);
        
        // 自动移除通知
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    loadSettings() {
        const defaultSettings = {
            display: {
                fullscreen: true,
                resolution: '1920x1080',
                vsync: true
            },
            audio: {
                enabled: true,
                volume: 80
            },
            input: {
                gamepadEnabled: true,
                autoDetectGamepad: true
            }
        };
        
        try {
            const saved = localStorage.getItem('gamePlayerSettings');
            return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
        } catch (error) {
            return defaultSettings;
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('gamePlayerSettings', JSON.stringify(this.settings));
            this.showNotification('设置已保存', 'success');
        } catch (error) {
            this.showNotification('保存设置失败', 'error');
        }
    }

    resetSettings() {
        if (confirm('确定要重置所有设置吗？')) {
            localStorage.removeItem('gamePlayerSettings');
            this.settings = this.loadSettings();
            this.updateSettingsUI();
            this.showNotification('设置已重置', 'success');
        }
    }

    updateSetting(key, value) {
        const keys = key.split('.');
        let obj = this.settings;
        
        for (let i = 0; i < keys.length - 1; i++) {
            if (!obj[keys[i]]) obj[keys[i]] = {};
            obj = obj[keys[i]];
        }
        
        obj[keys[keys.length - 1]] = value;
    }

    updateSettingsUI() {
        document.getElementById('fullscreen').checked = this.settings.display.fullscreen;
        document.getElementById('resolution').value = this.settings.display.resolution;
        document.getElementById('audioEnabled').checked = this.settings.audio.enabled;
        document.getElementById('volume').value = this.settings.audio.volume;
        document.getElementById('volumeValue').textContent = this.settings.audio.volume + '%';
        document.getElementById('gamepadEnabled').checked = this.settings.input.gamepadEnabled;
        document.getElementById('autoDetectGamepad').checked = this.settings.input.autoDetectGamepad;
    }

    loadStats() {
        const defaultStats = {
            totalGames: 0,
            playTime: 0,
            favoriteGames: 0,
            achievements: 0,
            systemDistribution: {}
        };
        
        try {
            const saved = localStorage.getItem('gamePlayerStats');
            return saved ? { ...defaultStats, ...JSON.parse(saved) } : defaultStats;
        } catch (error) {
            return defaultStats;
        }
    }

    updateStats() {
        // 计算统计数据
        let totalGames = 0;
        const systemDistribution = {};
        Object.keys(this.games).forEach(system => {
            const count = this.games[system] ? this.games[system].length : 0;
            totalGames += count;
            if (count > 0) {
                systemDistribution[system] = count;
            }
        });
        
        // 更新显示
        document.getElementById('totalGames').textContent = totalGames;
        document.getElementById('playTime').textContent = this.stats.playTime + 'h';
        document.getElementById('favoriteGames').textContent = this.stats.favoriteGames;
        document.getElementById('achievements').textContent = this.stats.achievements;
        
        // 更新图表（简单的文本显示）
        const chartContainer = document.querySelector('.chart-container');
        if (Object.keys(systemDistribution).length > 0) {
            const chartHtml = Object.entries(systemDistribution)
                .map(([system, count]) => `<div>${system.toUpperCase()}: ${count} 个游戏</div>`)
                .join('');
            chartContainer.innerHTML = chartHtml;
        } else {
            chartContainer.innerHTML = '<div style="color: var(--text-secondary);">暂无数据</div>';
        }
    }

    updateGameStats(game) {
        this.stats.totalGames++;
        this.stats.playTime += 0.5; // 假设每次游戏0.5小时
        
        if (!this.stats.systemDistribution[game.system]) {
            this.stats.systemDistribution[game.system] = 0;
        }
        this.stats.systemDistribution[game.system]++;
        
        try {
            localStorage.setItem('gamePlayerStats', JSON.stringify(this.stats));
        } catch (error) {
            console.error('保存统计数据失败:', error);
        }
    }

    updateUI() {
        this.updateSettingsUI();
        this.updateStats();
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.gamePlayerApp = new GamePlayerApp();
});

// 添加一些实用的全局函数
window.gamePlayerUtils = {
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    formatPlayTime: (hours) => {
        if (hours < 1) return Math.round(hours * 60) + ' 分钟';
        return Math.round(hours) + ' 小时';
    },
    
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// 导出供其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GamePlayerApp;
}
