/**
 * xiao-agent - Content Script
 * Injected into web pages
 */

// Listen for messages from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Content script received:', message);
  
  if (message.type === 'ping') {
    sendResponse({ status: 'alive' });
    return true;
  }
  
  return false;
});

console.log('xiao-agent content script loaded');