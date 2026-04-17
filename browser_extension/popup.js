/**
 * xiao-agent - Popup Script
 */

document.addEventListener('DOMContentLoaded', async () => {
  const hostInput = document.getElementById('host');
  const portInput = document.getElementById('port');
  const statusText = document.getElementById('statusText');
  const connectBtn = document.getElementById('connectBtn');
  
  // Load saved settings
  const result = await chrome.storage.local.get(['websocketHost', 'websocketPort']);
  if (result.websocketHost) hostInput.value = result.websocketHost;
  if (result.websocketPort) portInput.value = result.websocketPort;
  
  // Check connection status
  chrome.runtime.sendMessage({ type: 'status' }, (response) => {
    if (response && response.connected) {
      statusText.textContent = 'Connected';
      statusText.style.color = 'green';
    } else {
      statusText.textContent = 'Disconnected';
      statusText.style.color = 'red';
    }
  });
  
  // Save settings
  connectBtn.addEventListener('click', async () => {
    const host = hostInput.value || 'localhost';
    const port = parseInt(portInput.value) || 8765;
    
    await chrome.storage.local.set({
      websocketHost: host,
      websocketPort: port
    });
    
    statusText.textContent = 'Settings saved. Restart extension.';
  });
});