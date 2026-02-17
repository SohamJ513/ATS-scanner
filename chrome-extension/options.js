// Load settings
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.local.get(['settings'], (result) => {
    const settings = result.settings || {
      autoScan: true,
      saveHistory: true,
      apiUrl: 'http://localhost:8000',
      theme: 'dark'
    };
    
    document.getElementById('autoScan').checked = settings.autoScan;
    document.getElementById('saveHistory').checked = settings.saveHistory;
    document.getElementById('apiUrl').value = settings.apiUrl;
    document.getElementById('theme').value = settings.theme;
  });
});

// Save settings
document.getElementById('saveBtn').addEventListener('click', () => {
  const settings = {
    autoScan: document.getElementById('autoScan').checked,
    saveHistory: document.getElementById('saveHistory').checked,
    apiUrl: document.getElementById('apiUrl').value,
    theme: document.getElementById('theme').value
  };
  
  chrome.storage.local.set({ settings }, () => {
    const status = document.getElementById('status');
    status.classList.add('success');
    setTimeout(() => {
      status.classList.remove('success');
    }, 2000);
  });
});