// Background service worker

// Default settings
const DEFAULT_SETTINGS = {
  autoScan: true,
  saveHistory: true,
  theme: 'dark',
  apiUrl: 'http://localhost:8000'
};

// Initialize extension on install
chrome.runtime.onInstalled.addListener(() => {
  // Set default settings
  chrome.storage.local.set(DEFAULT_SETTINGS);
  
  // Initialize storage
  chrome.storage.local.get(['resume', 'history', 'settings'], (result) => {
    if (!result.resume) {
      chrome.storage.local.set({ resume: null });
    }
    if (!result.history) {
      chrome.storage.local.set({ history: [] });
    }
    if (!result.settings) {
      chrome.storage.local.set({ settings: DEFAULT_SETTINGS });
    }
  });
});

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'scanJob':
      handleJobScan(request.jobDetails, request.resume)
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ error: error.message }));
      break;
      
    case 'saveResume':
      chrome.storage.local.set({ resume: request.resume });
      sendResponse({ success: true });
      break;
      
    case 'getResume':
      chrome.storage.local.get(['resume'], (result) => {
        sendResponse({ resume: result.resume });
      });
      return true; // Keep channel open for async
      
    case 'saveToHistory':
      saveToHistory(request.scanData);
      sendResponse({ success: true });
      break;
      
    case 'getHistory':
      chrome.storage.local.get(['history'], (result) => {
        sendResponse({ history: result.history || [] });
      });
      return true;
      
    case 'clearHistory':
      chrome.storage.local.set({ history: [] });
      sendResponse({ success: true });
      break;
      
    case 'openDashboard':
      chrome.tabs.create({ url: 'http://localhost:8501' });
      break;
  }
  return true;
});

// Handle job scan
async function handleJobScan(jobDetails, resume) {
  if (!jobDetails || !resume) {
    throw new Error('Missing job details or resume');
  }

  try {
    // Get API URL from settings
    const settings = await chrome.storage.local.get(['settings']);
    const apiUrl = settings.settings?.apiUrl || 'http://localhost:8000';

    // Call backend API
    const response = await fetch(`${apiUrl}/api/analyze-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        resume_text: resume.content,
        job_description: jobDetails.description
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const result = await response.json();
    
    // Add job details to result
    result.job = {
      title: jobDetails.title,
      company: jobDetails.company,
      location: jobDetails.location
    };

    // Save to history if enabled
    if (settings.settings?.saveHistory) {
      saveToHistory({
        timestamp: new Date().toISOString(),
        job: result.job,
        score: result.ats_analysis.overall_score,
        skills: result.parsed_data.skills,
        missing_keywords: result.ats_analysis.missing_keywords
      });
    }

    return result;
  } catch (error) {
    console.error('Scan error:', error);
    throw error;
  }
}

// Save scan to history
function saveToHistory(scanData) {
  chrome.storage.local.get(['history'], (result) => {
    const history = result.history || [];
    history.unshift(scanData); // Add to beginning
    // Keep last 50 scans
    if (history.length > 50) {
      history.pop();
    }
    chrome.storage.local.set({ history });
  });
}

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  chrome.action.setPopup({ 
    popup: 'popup.html' 
  });
});