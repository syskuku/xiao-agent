/**
 * 小爱音箱浏览器控制器 - 内容脚本
 * 注入到网页中，执行页面内操作
 */

class ContentScript {
  constructor() {
    this.init();
  }
  
  init() {
    console.log('小爱音箱浏览器控制器内容脚本已加载');
    
    // 监听来自后台脚本的消息
    this.setupMessageListener();
    
    // 监听页面变化
    this.setupPageObserver();
  }
  
  setupMessageListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      console.log('内容脚本收到消息:', message);
      
      switch (message.type) {
        case 'execute_action':
          this.executeAction(message.action, message.params)
            .then(result => sendResponse({ success: true, result }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          return true; // 表示异步响应
          
        case 'get_page_info':
          const pageInfo = this.getPageInfo();
          sendResponse({ success: true, result: pageInfo });
          break;
          
        case 'highlight_element':
          this.highlightElement(message.selector);
          sendResponse({ success: true });
          break;
          
        default:
          sendResponse({ error: '未知消息类型' });
      }
    });
  }
  
  setupPageObserver() {
    // 监听DOM变化
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          // 页面内容发生变化
          this.onPageContentChanged();
        }
      });
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
  
  onPageContentChanged() {
    // 页面内容变化时的处理
    // 可以在这里实现动态元素检测
  }
  
  async executeAction(action, params) {
    switch (action) {
      case 'click':
        return this.clickElement(params);
        
      case 'input':
        return this.inputText(params);
        
      case 'scroll':
        return this.scrollPage(params);
        
      case 'extract':
        return this.extractData(params);
        
      case 'get_text':
        return this.getText(params);
        
      case 'fill_form':
        return this.fillForm(params);
        
      case 'wait_for_element':
        return this.waitForElement(params);
        
      default:
        throw new Error(`未知操作: ${action}`);
    }
  }
  
  clickElement(params) {
    const { selector } = params;
    const element = document.querySelector(selector);
    
    if (!element) {
      throw new Error(`未找到元素: ${selector}`);
    }
    
    element.click();
    return { success: true, element: element.outerHTML.substring(0, 100) };
  }
  
  inputText(params) {
    const { selector, text } = params;
    const element = document.querySelector(selector);
    
    if (!element) {
      throw new Error(`未找到元素: ${selector}`);
    }
    
    // 设置值
    element.value = text;
    
    // 触发事件
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
    
    return { success: true, value: element.value };
  }
  
  scrollPage(params) {
    const { direction = 'down', amount = 500 } = params;
    const scrollAmount = direction === 'up' ? -amount : amount;
    
    window.scrollBy({
      top: scrollAmount,
      behavior: 'smooth'
    });
    
    return { 
      success: true, 
      scrollY: window.scrollY,
      scrollHeight: document.documentElement.scrollHeight 
    };
  }
  
  extractData(params) {
    const { selector, attribute = 'text' } = params;
    const elements = document.querySelectorAll(selector);
    const data = [];
    
    elements.forEach(element => {
      let value;
      switch (attribute) {
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
          value = element.getAttribute(attribute);
      }
      data.push(value);
    });
    
    return { success: true, data };
  }
  
  getText(params) {
    const { selector } = params;
    const element = document.querySelector(selector);
    
    if (!element) {
      throw new Error(`未找到元素: ${selector}`);
    }
    
    return { success: true, text: element.textContent.trim() };
  }
  
  fillForm(params) {
    const { fields } = params;
    
    if (!fields || !Array.isArray(fields)) {
      throw new Error('字段参数缺失');
    }
    
    const results = [];
    
    fields.forEach(field => {
      const { selector, value } = field;
      const element = document.querySelector(selector);
      
      if (element) {
        element.value = value;
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        results.push({ selector, success: true });
      } else {
        results.push({ selector, success: false, error: '元素未找到' });
      }
    });
    
    return { success: true, results };
  }
  
  async waitForElement(params) {
    const { selector, timeout = 5000 } = params;
    
    return new Promise((resolve, reject) => {
      const element = document.querySelector(selector);
      if (element) {
        resolve({ success: true, element: element.outerHTML.substring(0, 100) });
        return;
      }
      
      const observer = new MutationObserver((mutations, obs) => {
        const element = document.querySelector(selector);
        if (element) {
          obs.disconnect();
          resolve({ success: true, element: element.outerHTML.substring(0, 100) });
        }
      });
      
      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
      
      // 超时处理
      setTimeout(() => {
        observer.disconnect();
        reject(new Error(`等待元素超时: ${selector}`));
      }, timeout);
    });
  }
  
  getPageInfo() {
    return {
      url: window.location.href,
      title: document.title,
      domain: window.location.hostname,
      readyState: document.readyState,
      elementCount: document.querySelectorAll('*').length,
      linkCount: document.querySelectorAll('a').length,
      formCount: document.querySelectorAll('form').length,
      inputCount: document.querySelectorAll('input').length
    };
  }
  
  highlightElement(selector) {
    const element = document.querySelector(selector);
    if (!element) return;
    
    // 添加高亮样式
    element.style.outline = '3px solid red';
    element.style.outlineOffset = '2px';
    
    // 滚动到元素位置
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    });
    
    // 3秒后移除高亮
    setTimeout(() => {
      element.style.outline = '';
      element.style.outlineOffset = '';
    }, 3000);
  }
}

// 初始化内容脚本
const contentScript = new ContentScript();

// 导出到全局作用域（用于调试）
window.contentScript = contentScript;