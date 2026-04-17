/**
 * xiao-agent Chrome Extension - Background Script
 * Manifest V3 Service Worker
 */

class BrowserController {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.heartbeatInterval = null;
    this.wsHost = 'localhost';
    this.wsPort = 8765;
    
    this.init();
  }
  
  async init() {
    console.log('xiao-agent controller initializing...');
    
    // Load settings
    const result = await chrome.storage.local.get(['websocketHost', 'websocketPort']);
    if (result.websocketHost) this.wsHost = result.websocketHost;
    if (result.websocketPort) this.wsPort = result.websocketPort;
    
    this.connectWebSocket();
    this.setupListeners();
  }
  
  connectWebSocket() {
    const wsUrl = `ws://${this.wsHost}:${this.wsPort}`;
    console.log(`Connecting to ${wsUrl}...`);
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('Connected!');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.showNotification('Connected to xiao-agent');
      };
      
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('Received:', message);
          this.handleCommand(message);
        } catch (e) {
          console.error('Parse error:', e);
        }
      };
      
      this.ws.onclose = () => {
        console.log('Disconnected');
        this.isConnected = false;
        this.stopHeartbeat();
        this.scheduleReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error');
      };
      
    } catch (e) {
      console.error('Connection failed:', e);
      this.scheduleReconnect();
    }
  }
  
  scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => this.connectWebSocket(), 3000);
    }
  }
  
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000);
  }
  
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
  
  async handleCommand(message) {
    if (message.type !== 'command' && !message.action) return;
    
    const action = message.action;
    const params = message.params || {};
    
    try {
      let result;
      
      switch (action) {
        case 'open_url':
        case 'browser_open_url':
          result = await this.openUrl(params.url);
          break;
          
        case 'search':
        case 'browser_search':
          result = await this.search(params);
          break;
          
        case 'click':
        case 'browser_click':
          result = await this.clickElement(params);
          break;
          
        case 'input':
        case 'browser_input':
          result = await this.inputText(params);
          break;
          
        case 'scroll':
        case 'browser_scroll':
          result = await this.scrollPage(params);
          break;
          
        case 'back':
        case 'browser_back':
          result = await this.goBack();
          break;
          
        case 'forward':
        case 'browser_forward':
          result = await this.goForward();
          break;
          
        case 'extract':
        case 'browser_extract':
          result = await this.extractData(params);
          break;
          
        default:
          result = { error: `Unknown action: ${action}` };
      }
      
      console.log('Result:', result);
      
    } catch (e) {
      console.error('Execute error:', e);
    }
  }
  
  async openUrl(url) {
    if (!url) throw new Error('URL required');
    const tab = await chrome.tabs.create({ url });
    return { tabId: tab.id, url: tab.url };
  }
  
  async search(params) {
    const { query, engine = 'baidu' } = params;
    const urls = {
      baidu: `https://www.baidu.com/s?wd=${encodeURIComponent(query)}`,
      google: `https://www.google.com/search?q=${encodeURIComponent(query)}`,
      bing: `https://www.bing.com/search?q=${encodeURIComponent(query)}`
    };
    return this.openUrl(urls[engine] || urls.baidu);
  }
  
  async clickElement(params) {
    const { selector } = params;
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (sel) => {
        const el = document.querySelector(sel);
        if (el) { el.click(); return { success: true }; }
        return { error: `Element not found: ${sel}` };
      },
      args: [selector]
    });
    
    return results[0].result;
  }
  
  async inputText(params) {
    const { selector, text } = params;
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (sel, txt) => {
        const el = document.querySelector(sel);
        if (el) {
          el.value = txt;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true, value: el.value };
        }
        return { error: `Element not found: ${sel}` };
      },
      args: [selector, text]
    });
    
    return results[0].result;
  }
  
  async scrollPage(params) {
    const { direction = 'down', amount = 500 } = params;
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (dir, amt) => {
        window.scrollBy({ top: dir === 'up' ? -amt : amt, behavior: 'smooth' });
        return { success: true };
      },
      args: [direction, amount]
    });
    
    return results[0].result;
  }
  
  async goBack() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.tabs.goBack(tab.id);
    return { success: true };
  }
  
  async goForward() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.tabs.goForward(tab.id);
    return { success: true };
  }
  
  async extractData(params) {
    const { selector, attribute = 'text' } = params;
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (sel, attr) => {
        const els = document.querySelectorAll(sel);
        const data = [];
        els.forEach(el => {
          if (attr === 'text') data.push(el.textContent.trim());
          else if (attr === 'html') data.push(el.innerHTML);
          else if (attr === 'value') data.push(el.value);
          else data.push(el.getAttribute(attr));
        });
        return { success: true, data };
      },
      args: [selector, attribute]
    });
    
    return results[0].result;
  }
  
  setupListeners() {
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete') {
        console.log(`Tab loaded: ${tab.url}`);
      }
    });
  }
  
  showNotification(message) {
    console.log('[NOTIFY]', message);
  }
}

// Initialize
const controller = new BrowserController();