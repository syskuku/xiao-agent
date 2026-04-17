/**
 * xiao-agent - Background Service Worker
 */

let ws = null;
let isConnected = false;

// Initialize
async function init() {
  console.log('Initializing...');
  await connect();
  setupMessageListener();
}

// Connect to WebSocket
async function connect() {
  const result = await chrome.storage.local.get(['websocketHost', 'websocketPort']);
  const host = result.websocketHost || 'localhost';
  const port = result.websocketPort || 8765;
  
  const wsUrl = `ws://${host}:${port}`;
  console.log(`Connecting to ${wsUrl}...`);
  
  try {
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('Connected!');
      isConnected = true;
    };
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('Received:', message);
        
        if (message.action) {
          executeCommand(message);
        }
      } catch (e) {
        console.error('Parse error:', e);
      }
    };
    
    ws.onclose = () => {
      console.log('Disconnected');
      isConnected = false;
      setTimeout(connect, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error');
    };
    
  } catch (e) {
    console.error('Connect failed:', e);
    setTimeout(connect, 3000);
  }
}

// Execute command
async function executeCommand(message) {
  const action = message.action;
  const params = message.params || {};
  
  console.log('Executing:', action, params);
  
  try {
    switch (action) {
      case 'open_url':
      case 'browser_open_url':
        await chrome.tabs.create({ url: params.url });
        break;
        
      case 'click':
      case 'browser_click':
        await executeInTab((sel) => {
          const el = document.querySelector(sel);
          if (el) el.click();
          return el ? 'clicked' : 'not found';
        }, [params.selector]);
        break;
        
      case 'input':
      case 'browser_input':
        await executeInTab((sel, txt) => {
          const el = document.querySelector(sel);
          if (el) {
            el.value = txt;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
          }
          return el ? 'filled' : 'not found';
        }, [params.selector, params.text]);
        break;
        
      case 'scroll':
      case 'browser_scroll':
        await executeInTab((dir, amt) => {
          window.scrollBy({ top: dir === 'up' ? -amt : amt, behavior: 'smooth' });
          return 'scrolled';
        }, [params.direction || 'down', params.amount || 500]);
        break;
        
      case 'back':
      case 'browser_back':
        await goBack();
        break;
        
      case 'forward':
      case 'browser_forward':
        await goForward();
        break;
        
      default:
        console.log('Unknown action:', action);
    }
  } catch (e) {
    console.error('Execute error:', e);
  }
}

// Execute in active tab
async function executeInTab(func, args) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return null;
  
  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: func,
    args: args || []
  });
  
  return results[0]?.result;
}

// Navigate back
async function goBack() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab) await chrome.tabs.goBack(tab.id);
}

// Navigate forward
async function goForward() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab) await chrome.tabs.goForward(tab.id);
}

// Message listener
function setupMessageListener() {
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'status') {
      sendResponse({ connected: isConnected });
    }
    return true;
  });
}

// Start
init();