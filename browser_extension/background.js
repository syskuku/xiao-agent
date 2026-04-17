/**
 * 小爱音箱浏览器控制器 - 后台脚本
 * 负责WebSocket连接和浏览器自动化
 */

class BrowserController {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.heartbeatInterval = null;
    this.clientId = `browser_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    this.init();
  }
  
  init() {
    console.log('小爱音箱浏览器控制器初始化...');
    this.connectWebSocket();
    this.setupEventListeners();
  }
  
  connectWebSocket() {
    try {
      // 从存储中获取WebSocket配置
      chrome.storage.local.get(['websocketHost', 'websocketPort'], (result) => {
        const host = result.websocketHost || 'localhost';
        const port = result.websocketPort || 8765;
        const wsUrl = `ws://${host}:${port}`;
        
        console.log(`正在连接WebSocket: ${wsUrl}`);
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => this.onWebSocketOpen();
        this.ws.onmessage = (event) => this.onWebSocketMessage(event);
        this.ws.onclose = () => this.onWebSocketClose();
        this.ws.onerror = (error) => this.onWebSocketError(error);
      });
      
    } catch (error) {
      console.error('WebSocket连接失败:', error);
      this.scheduleReconnect();
    }
  }
  
  onWebSocketOpen() {
    console.log('WebSocket连接已建立');
    this.isConnected = true;
    this.reconnectAttempts = 0;
    
    // 发送注册消息
    this.send({
      type: 'register',
      client_id: this.clientId,
      user_agent: navigator.userAgent
    });
    
    // 启动心跳
    this.startHeartbeat();
    
    // 更新插件图标状态
    this.updateIcon(true);
    
    // 显示连接成功通知
    this.showNotification('已连接到小爱音箱控制系统', 'success');
  }
  
  onWebSocketMessage(event) {
    try {
      const message = JSON.parse(event.data);
      console.log('收到消息:', message);
      
      switch (message.type) {
        case 'registered':
          console.log('注册成功:', message.client_id);
          break;
          
        case 'heartbeat_response':
          // 心跳响应，无需处理
          break;
          
        default:
          // 处理浏览器控制指令
          this.handleCommand(message);
          break;
      }
      
    } catch (error) {
      console.error('处理消息失败:', error);
    }
  }
  
  onWebSocketClose() {
    console.log('WebSocket连接已关闭');
    this.isConnected = false;
    this.stopHeartbeat();
    this.updateIcon(false);
    this.scheduleReconnect();
  }
  
  onWebSocketError(error) {
    console.error('WebSocket错误:', error);
  }
  
  scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`尝试重新连接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connectWebSocket();
      }, this.reconnectDelay);
    } else {
      console.error('达到最大重连次数，停止重连');
      this.showNotification('无法连接到服务器，请检查网络设置', 'error');
    }
  }
  
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.send({
          type: 'heartbeat',
          timestamp: Date.now()
        });
      }
    }, 30000); // 每30秒发送一次心跳
  }
  
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
  
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket未连接，无法发送消息');
    }
  }
  
  async handleCommand(command) {
    console.log('处理命令:', command);
    
    try {
      let result;
      
      switch (command.action) {
        case 'open_url':
          result = await this.openUrl(command.params);
          break;
          
        case 'navigate':
          result = await this.navigate(command.params);
          break;
          
        case 'click':
          result = await this.clickElement(command.params);
          break;
          
        case 'input':
          result = await this.inputText(command.params);
          break;
          
        case 'scroll':
          result = await this.scrollPage(command.params);
          break;
          
        case 'screenshot':
          result = await this.takeScreenshot(command.params);
          break;
          
        case 'extract':
          result = await this.extractData(command.params);
          break;
          
        case 'search':
          result = await this.search(command.params);
          break;
          
        case 'back':
          result = await this.goBack();
          break;
          
        case 'forward':
          result = await this.goForward();
          break;
          
        case 'wait':
          result = await this.wait(command.params);
          break;
          
        case 'multi_step':
          result = await this.multiStep(command.params);
          break;
          
        default:
          result = { error: `未知操作: ${command.action}` };
      }
      
      // 发送执行结果
      this.send({
        type: 'execution_result',
        command_id: command.id,
        action: command.action,
        result: result,
        timestamp: Date.now()
      });
      
    } catch (error) {
      console.error('执行命令失败:', error);
      
      // 发送错误信息
      this.send({
        type: 'error',
        command_id: command.id,
        action: command.action,
        error: error.message,
        timestamp: Date.now()
      });
    }
  }
  
  // 浏览器操作实现
  
  async openUrl(params) {
    const { url } = params;
    if (!url) throw new Error('URL参数缺失');
    
    const tab = await chrome.tabs.create({ url });
    return { tabId: tab.id, url: tab.url };
  }
  
  async navigate(params) {
    const { url } = params;
    if (!url) throw new Error('URL参数缺失');
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('没有活动的标签页');
    
    await chrome.tabs.update(tab.id, { url });
    return { tabId: tab.id, url };
  }
  
  async clickElement(params) {
    const { selector, description } = params;
    if (!selector) throw new Error('选择器参数缺失');
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('没有活动的标签页');
    
    // 执行点击脚本
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (sel) => {
        const element = document.querySelector(sel);
        if (!element) return { error: `未找到元素: ${sel}` };
        
        element.click();
        return { success: true, element: element.outerHTML.substring(0, 100) };
      },
      args: [selector]
    });
    
    return results[0].result;
  }
  
  async inputText(params) {
    const { selector, text } = params;
    if (!selector || text === undefined) throw new Error('选择器或文本参数缺失');
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('没有活动的标签页');
    
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (sel, txt) => {
        const element = document.querySelector(sel);
        if (!element) return { error: `未找到元素: ${sel}` };
        
        // 设置值
        element.value = txt;
        
        // 触发输入事件
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        
        return { success: true, value: element.value };
      },
      args: [selector, text]
    });
    
    return results[0].result;
  }
  
  async scrollPage(params) {
    const { direction = 'down', amount = 500 } = params;
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('没有活动的标签页');
    
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (dir, amt) => {
        const scrollAmount = dir === 'up' ? -amt : amt;
        window.scrollBy({
          top: scrollAmount,
          behavior: 'smooth'
        });
        
        return { 
          success: true, 
          scrollY: window.scrollY,
          scrollHeight: document.documentElement.scrollHeight 
        };
      },
      args: [direction, amount]
    });
    
    return results[0].result;
  }
  
  async takeScreenshot(params) {
    const { fullPage = false } = params;
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('没有活动的标签页');
    
    // 使用chrome.debugger进行截图
    // 注意：这需要用户授权调试权限
    return { message: '截图功能需要调试权限，请在插件弹出窗口中启用' };
  }
  
  async extractData(params) {
    const { selector, attribute = 'text' } = params;
    if (!selector) throw new Error('选择器参数缺失');
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('没有活动的标签页');
    
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (sel, attr) => {
        const elements = document.querySelectorAll(sel);
        const data = [];
        
        elements.forEach(element => {
          let value;
          switch (attr) {
            case 'text':
              value = element.textContent.trim();
              break;
            case 'html':
              value = element.innerHTML;
              break;
            case 'value':
              value = element.value;
              break;
            default:
              value = element.getAttribute(attr);
          }
          data.push(value);
        });
        
        return { success: true, data };
      },
      args: [selector, attribute]
    });
    
    return results[0].result;
  }
  
  async search(params) {
    const { keyword, engine = 'baidu' } = params;
    if (!keyword) throw new Error('搜索关键词缺失');
    
    let searchUrl;
    switch (engine.toLowerCase()) {
      case 'baidu':
        searchUrl = `https://www.baidu.com/s?wd=${encodeURIComponent(keyword)}`;
        break;
      case 'google':
        searchUrl = `https://www.google.com/search?q=${encodeURIComponent(keyword)}`;
        break;
      case 'bing':
        searchUrl = `https://www.bing.com/search?q=${encodeURIComponent(keyword)}`;
        break;
      default:
        searchUrl = `https://www.baidu.com/s?wd=${encodeURIComponent(keyword)}`;
    }
    
    return await this.openUrl({ url: searchUrl });
  }
  
  async goBack() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('没有活动的标签页');
    
    await chrome.tabs.goBack(tab.id);
    return { success: true };
  }
  
  async goForward() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('没有活动的标签页');
    
    await chrome.tabs.goForward(tab.id);
    return { success: true };
  }
  
  async wait(params) {
    const { seconds = 1 } = params;
    
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ success: true, waited: seconds });
      }, seconds * 1000);
    });
  }
  
  async multiStep(params) {
    const { steps } = params;
    if (!steps || !Array.isArray(steps)) throw new Error('步骤参数缺失');
    
    const results = [];
    
    for (let i = 0; i < steps.length; i++) {
      const step = steps[i];
      console.log(`执行步骤 ${i + 1}/${steps.length}:`, step);
      
      try {
        const result = await this.handleCommand(step);
        results.push({
          step: i + 1,
          action: step.action,
          success: true,
          result: result
        });
        
        // 步骤间短暂延迟
        if (i < steps.length - 1) {
          await this.wait({ seconds: 0.5 });
        }
        
      } catch (error) {
        results.push({
          step: i + 1,
          action: step.action,
          success: false,
          error: error.message
        });
        
        // 如果某一步失败，停止后续步骤
        break;
      }
    }
    
    return { success: true, results };
  }
  
  // 辅助方法
  
  updateIcon(connected) {
    const iconPath = connected ? 'icons/icon48_connected.png' : 'icons/icon48.png';
    chrome.action.setIcon({ path: iconPath });
  }
  
  showNotification(message, type = 'info') {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: '小爱音箱浏览器控制器',
      message: message
    });
  }
  
  setupEventListeners() {
    // 监听标签页更新
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete') {
        console.log(`标签页 ${tabId} 加载完成: ${tab.url}`);
      }
    });
    
    // 监听插件安装
    chrome.runtime.onInstalled.addListener((details) => {
      if (details.reason === 'install') {
        console.log('插件已安装');
        this.showNotification('插件已安装，请配置WebSocket连接', 'info');
      }
    });
  }
}

// 初始化浏览器控制器
const browserController = new BrowserController();

// 导出到全局作用域（用于调试）
window.browserController = browserController;