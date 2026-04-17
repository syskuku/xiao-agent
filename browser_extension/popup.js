/**
 * 小爱音箱浏览器控制器 - 弹出窗口脚本
 */

class PopupController {
  constructor() {
    this.backgroundPage = null;
    this.init();
  }
  
  async init() {
    // 获取后台页面
    this.backgroundPage = chrome.extension.getBackgroundPage();
    
    // 初始化UI
    this.initUI();
    
    // 加载保存的设置
    await this.loadSettings();
    
    // 更新连接状态
    this.updateConnectionStatus();
    
    // 设置事件监听器
    this.setupEventListeners();
    
    // 启动状态更新定时器
    this.startStatusUpdate();
  }
  
  initUI() {
    // 标签页切换
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', (e) => {
        const tabId = e.target.getAttribute('data-tab');
        this.switchTab(tabId);
      });
    });
  }
  
  switchTab(tabId) {
    // 更新标签页状态
    document.querySelectorAll('.tab').forEach(tab => {
      tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    
    // 激活选中的标签页
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
  }
  
  async loadSettings() {
    try {
      const result = await chrome.storage.local.get(['websocketHost', 'websocketPort']);
      
      if (result.websocketHost) {
        document.getElementById('host').value = result.websocketHost;
      }
      
      if (result.websocketPort) {
        document.getElementById('port').value = result.websocketPort;
      }
      
    } catch (error) {
      console.error('加载设置失败:', error);
    }
  }
  
  async saveSettings() {
    try {
      const host = document.getElementById('host').value;
      const port = document.getElementById('port').value;
      
      await chrome.storage.local.set({
        websocketHost: host,
        websocketPort: parseInt(port)
      });
      
      this.addLog('设置已保存', 'info');
      
    } catch (error) {
      console.error('保存设置失败:', error);
      this.addLog('保存设置失败', 'error');
    }
  }
  
  updateConnectionStatus() {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const connectBtn = document.getElementById('connectBtn');
    const disconnectBtn = document.getElementById('disconnectBtn');
    
    if (this.backgroundPage && this.backgroundPage.browserController) {
      const isConnected = this.backgroundPage.browserController.isConnected;
      
      statusIndicator.className = `status-indicator ${isConnected ? 'connected' : 'disconnected'}`;
      statusText.textContent = isConnected ? '已连接' : '未连接';
      
      connectBtn.disabled = isConnected;
      disconnectBtn.disabled = !isConnected;
      
      if (isConnected) {
        this.addLog('已连接到服务器', 'success');
      }
    }
  }
  
  setupEventListeners() {
    // 连接按钮
    document.getElementById('connectBtn').addEventListener('click', () => {
      this.connect();
    });
    
    // 断开连接按钮
    document.getElementById('disconnectBtn').addEventListener('click', () => {
      this.disconnect();
    });
    
    // 测试连接按钮
    document.getElementById('testBtn').addEventListener('click', () => {
      this.testConnection();
    });
    
    // 截图按钮
    document.getElementById('screenshotBtn').addEventListener('click', () => {
      this.takeScreenshot();
    });
    
    // 清空日志按钮
    document.getElementById('clearLogBtn').addEventListener('click', () => {
      this.clearLog();
    });
    
    // 输入框变化时自动保存
    document.getElementById('host').addEventListener('change', () => {
      this.saveSettings();
    });
    
    document.getElementById('port').addEventListener('change', () => {
      this.saveSettings();
    });
  }
  
  connect() {
    try {
      // 保存设置
      this.saveSettings();
      
      // 重新连接WebSocket
      if (this.backgroundPage && this.backgroundPage.browserController) {
        this.backgroundPage.browserController.connectWebSocket();
        this.addLog('正在连接...', 'info');
      }
      
    } catch (error) {
      console.error('连接失败:', error);
      this.addLog('连接失败: ' + error.message, 'error');
    }
  }
  
  disconnect() {
    try {
      if (this.backgroundPage && this.backgroundPage.browserController) {
        const controller = this.backgroundPage.browserController;
        
        if (controller.ws) {
          controller.ws.close();
        }
        
        this.addLog('已断开连接', 'info');
      }
      
    } catch (error) {
      console.error('断开连接失败:', error);
      this.addLog('断开连接失败: ' + error.message, 'error');
    }
  }
  
  testConnection() {
    try {
      if (this.backgroundPage && this.backgroundPage.browserController) {
        const controller = this.backgroundPage.browserController;
        
        if (controller.isConnected) {
          controller.send({
            type: 'test',
            timestamp: Date.now()
          });
          
          this.addLog('测试消息已发送', 'info');
        } else {
          this.addLog('未连接到服务器', 'error');
        }
      }
      
    } catch (error) {
      console.error('测试连接失败:', error);
      this.addLog('测试连接失败: ' + error.message, 'error');
    }
  }
  
  async takeScreenshot() {
    try {
      // 获取当前标签页
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab) {
        this.addLog('没有活动的标签页', 'error');
        return;
      }
      
      // 使用chrome.debugger进行截图
      // 注意：这需要用户授权调试权限
      this.addLog('截图功能需要调试权限', 'info');
      
    } catch (error) {
      console.error('截图失败:', error);
      this.addLog('截图失败: ' + error.message, 'error');
    }
  }
  
  addLog(message, type = 'info') {
    const logContainer = document.getElementById('logContainer');
    const timestamp = new Date().toLocaleTimeString();
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;
    
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
    
    // 限制日志条目数量
    while (logContainer.children.length > 50) {
      logContainer.removeChild(logContainer.firstChild);
    }
  }
  
  clearLog() {
    const logContainer = document.getElementById('logContainer');
    logContainer.innerHTML = '';
    this.addLog('日志已清空', 'info');
  }
  
  startStatusUpdate() {
    // 每2秒更新一次状态
    setInterval(() => {
      this.updateConnectionStatus();
    }, 2000);
  }
}

// 初始化弹出窗口控制器
document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});