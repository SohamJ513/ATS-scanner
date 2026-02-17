// Popup script - Main UI logic

// DOM Elements
const elements = {
  jobTitle: document.getElementById('jobTitle'),
  jobCompany: document.getElementById('jobCompany'),
  jobLocation: document.getElementById('jobLocation'),
  jobDescription: document.getElementById('jobDescription'),
  resumeName: document.getElementById('resumeName'),
  resumeStatus: document.getElementById('resumeStatus'),
  uploadSection: document.getElementById('uploadSection'),
  resumeUpload: document.getElementById('resumeUpload'),
  changeResumeBtn: document.getElementById('changeResumeBtn'),
  scoreSection: document.getElementById('scoreSection'),
  scoreValue: document.getElementById('scoreValue'),
  scoreFill: document.getElementById('scoreFill'),
  scoreBadge: document.getElementById('scoreBadge'),
  skillsFound: document.getElementById('skillsFound'),
  keywordsMissing: document.getElementById('keywordsMissing'),
  missingKeywordsSection: document.getElementById('missingKeywordsSection'),
  missingKeywordsList: document.getElementById('missingKeywordsList'),
  companyMatch: document.getElementById('companyMatch'),
  companyMatchSection: document.getElementById('companyMatchSection'),
  viewFullReportBtn: document.getElementById('viewFullReportBtn'),
  optimizeBtn: document.getElementById('optimizeBtn'),
  loginSection: document.getElementById('loginSection'),
  loginBtn: document.getElementById('loginBtn'),
  continueAsGuestBtn: document.getElementById('continueAsGuestBtn'),
  loadingOverlay: document.getElementById('loadingOverlay'),
  loadingMessage: document.getElementById('loadingMessage'),
  openDashboard: document.getElementById('openDashboard'),
  openSettings: document.getElementById('openSettings'),
  openHelp: document.getElementById('openHelp'),
  jobPortalBadge: document.getElementById('jobPortalBadge'),
  errorMessage: document.getElementById('errorMessage'),
  retryBtn: document.getElementById('retryBtn')
};

// State
let currentJobDetails = null;
let currentResume = null;
let currentScanResult = null;
let retryCount = 0;
const MAX_RETRIES = 3;

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 Popup initialized');
  showLoading('Initializing...');
  
  try {
    // Load saved resume
    await loadSavedResume();
    
    // Get current job details
    await getJobDetails();
    
    // Auto-scan if enabled
    const settings = await getSettings();
    if (settings.autoScan && currentResume && currentJobDetails && !currentJobDetails.error) {
      scanJob();
    } else {
      hideLoading();
    }
    
    // Setup event listeners
    setupEventListeners();
  } catch (error) {
    console.error('Initialization error:', error);
    hideLoading();
    showError('Failed to initialize. Please refresh the page.');
  }
});

// Load saved resume from storage
async function loadSavedResume() {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ action: 'getResume' }, (response) => {
      if (response && response.resume) {
        currentResume = response.resume;
        elements.resumeName.textContent = currentResume.name;
        elements.uploadSection.classList.add('hidden');
        console.log('✅ Loaded saved resume:', currentResume.name);
      } else {
        elements.uploadSection.classList.remove('hidden');
        console.log('📁 No saved resume found');
      }
      resolve();
    });
  });
}

// Get current job details from content script
async function getJobDetails() {
  return new Promise((resolve) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || tabs.length === 0) {
        console.error('❌ No active tab found');
        showError('No active tab found');
        resolve(null);
        return;
      }

      console.log('📄 Sending message to tab:', tabs[0].id);
      
      chrome.tabs.sendMessage(tabs[0].id, { action: 'getJobDetails' }, (response) => {
        if (chrome.runtime.lastError) {
          console.error('❌ Content script not ready:', chrome.runtime.lastError);
          showError('Please refresh the page and try again');
          showRetryButton();
          resolve(null);
          return;
        }
        
        console.log('📦 Received response:', response);
        
        if (response && response.error) {
          handleJobError(response);
          resolve(null);
          return;
        }
        
        if (response) {
          currentJobDetails = response;
          updateJobInfo(response);
          hideError();
          console.log('✅ Job details extracted:', response.title);
        } else {
          console.log('⚠️ No job details received');
          showError('Could not detect job details. Make sure you are on a job posting page.');
        }
        resolve(response);
      });
    });
  });
}

// Handle job extraction errors
function handleJobError(response) {
  if (response.error === 'NOT_JOB_PAGE') {
    showError('⚠️ Please click on a specific job posting first');
    elements.jobTitle.textContent = 'Click on a job title';
    elements.jobCompany.textContent = '';
    elements.jobLocation.textContent = '';
  } else if (response.error === 'EXTRACTION_FAILED') {
    showError('⚠️ Could not extract job details. Try Indeed or LinkedIn');
    showRetryButton();
  } else {
    showError(response.message || 'Failed to extract job details');
  }
}

// Update job information in UI
function updateJobInfo(jobDetails) {
  if (!jobDetails) return;
  
  // Show portal badge
  if (jobDetails.portal) {
    let portalBadge = document.createElement('span');
    portalBadge.className = 'portal-badge';
    portalBadge.textContent = jobDetails.portal.toUpperCase();
    
    const header = document.querySelector('.job-header');
    if (header && !document.querySelector('.portal-badge')) {
      header.appendChild(portalBadge);
    }
  }
  
  elements.jobTitle.textContent = jobDetails.title || 'Unknown Position';
  elements.jobCompany.textContent = jobDetails.company || '';
  elements.jobLocation.textContent = `📍 ${jobDetails.location || 'Location Not Specified'}`;
  
  // Truncate description
  const desc = jobDetails.description || '';
  elements.jobDescription.textContent = desc.length > 200 
    ? desc.substring(0, 200) + '...' 
    : desc;
}

// Scan job with resume
async function scanJob() {
  if (!currentJobDetails || currentJobDetails.error) {
    showError('Please select a valid job posting first');
    return;
  }

  if (!currentResume) {
    showError('Please upload a resume first');
    return;
  }

  showLoading('Analyzing resume against job...');

  try {
    chrome.runtime.sendMessage({
      action: 'scanJob',
      jobDetails: currentJobDetails,
      resume: currentResume
    }, (response) => {
      hideLoading();
      
      if (chrome.runtime.lastError) {
        console.error('❌ Scan error:', chrome.runtime.lastError);
        showError('Backend connection failed. Make sure the server is running.');
        return;
      }
      
      if (response && response.error) {
        console.error('❌ Scan failed:', response.error);
        showError(response.error);
        return;
      }

      if (response) {
        currentScanResult = response;
        displayResults(response);
        console.log('✅ Scan completed, score:', response.ats_analysis?.overall_score);
      }
    });
  } catch (error) {
    console.error('❌ Scan exception:', error);
    hideLoading();
    showError('Failed to analyze resume. Please try again.');
  }
}

// Display scan results
function displayResults(result) {
  if (!result || !result.ats_analysis) {
    showError('Invalid scan results');
    return;
  }

  const score = result.ats_analysis.overall_score || 0;
  const missingKeywords = result.ats_analysis.missing_keywords || [];
  const skills = result.parsed_data?.skills || [];
  
  // Update score
  elements.scoreValue.textContent = Math.round(score);
  elements.scoreFill.style.width = `${score}%`;
  
  // Set score badge
  if (score >= 80) {
    elements.scoreBadge.textContent = 'Excellent';
    elements.scoreBadge.className = 'score-badge excellent';
  } else if (score >= 60) {
    elements.scoreBadge.textContent = 'Good';
    elements.scoreBadge.className = 'score-badge good';
  } else {
    elements.scoreBadge.textContent = 'Needs Work';
    elements.scoreBadge.className = 'score-badge needs-work';
  }
  
  // Update metrics
  elements.skillsFound.textContent = skills.length;
  elements.keywordsMissing.textContent = missingKeywords.length;
  
  // Show missing keywords
  if (missingKeywords.length > 0) {
    elements.missingKeywordsSection.classList.remove('hidden');
    elements.missingKeywordsList.innerHTML = missingKeywords
      .slice(0, 8)
      .map(kw => `<span class="keyword-tag">${kw}</span>`)
      .join('');
  } else {
    elements.missingKeywordsSection.classList.add('hidden');
  }
  
  // Show company match
  const topCompany = getTopCompanyMatch(skills);
  if (topCompany) {
    elements.companyMatchSection.classList.remove('hidden');
    elements.companyMatch.innerHTML = `
      <span class="company-name">${topCompany.name}</span>
      <span class="company-score">${topCompany.score}%</span>
    `;
  }
  
  // Show score section
  elements.scoreSection.classList.remove('hidden');
  elements.loginSection.classList.add('hidden');
  
  // Save to history
  saveToHistory(result);
}

// Save scan to history
function saveToHistory(result) {
  const historyItem = {
    timestamp: new Date().toISOString(),
    job: {
      title: currentJobDetails?.title,
      company: currentJobDetails?.company,
      portal: currentJobDetails?.portal
    },
    score: result.ats_analysis?.overall_score,
    skills: result.parsed_data?.skills?.length || 0,
    missing: result.ats_analysis?.missing_keywords?.length || 0
  };
  
  chrome.runtime.sendMessage({
    action: 'saveToHistory',
    scanData: historyItem
  });
}

// Get top company match
function getTopCompanyMatch(skills) {
  const companies = [
    { name: 'TCS Ninja', keywords: ['python', 'java', 'sql', 'c++', 'dbms'], baseScore: 75 },
    { name: 'Infosys', keywords: ['python', 'django', 'sql', 'spring', 'react'], baseScore: 70 },
    { name: 'Wipro', keywords: ['java', 'sql', 'testing', 'selenium'], baseScore: 68 },
    { name: 'Amazon', keywords: ['aws', 'dsa', 'system design', 'leadership', 'oop'], baseScore: 65 },
    { name: 'Google', keywords: ['algorithms', 'python', 'cpp', 'distributed systems'], baseScore: 60 },
    { name: 'Microsoft', keywords: ['azure', 'c#', 'dotnet', 'design patterns'], baseScore: 62 },
    { name: 'TCS Digital', keywords: ['advanced dsa', 'cloud', 'microservices', 'devops'], baseScore: 72 },
    { name: 'Accenture', keywords: ['communication', 'agile', 'any language'], baseScore: 70 }
  ];
  
  let bestMatch = null;
  let bestScore = 0;
  
  companies.forEach(company => {
    let matchCount = 0;
    company.keywords.forEach(keyword => {
      if (skills.some(s => s.toLowerCase().includes(keyword.toLowerCase()))) {
        matchCount++;
      }
    });
    
    const matchPercentage = (matchCount / company.keywords.length) * 100;
    const score = company.baseScore + (matchPercentage * 0.2);
    if (score > bestScore) {
      bestScore = score;
      bestMatch = { 
        name: company.name, 
        score: Math.min(Math.round(score), 98) 
      };
    }
  });
  
  return bestMatch;
}

// Setup event listeners
function setupEventListeners() {
  // Resume upload
  elements.resumeUpload.addEventListener('change', handleResumeUpload);
  elements.changeResumeBtn.addEventListener('click', showUploadSection);
  
  // Action buttons
  elements.viewFullReportBtn.addEventListener('click', openFullReport);
  elements.optimizeBtn.addEventListener('click', openOptimizer);
  
  // Retry button
  if (elements.retryBtn) {
    elements.retryBtn.addEventListener('click', () => {
      hideError();
      showLoading('Retrying...');
      getJobDetails().then(() => {
        hideLoading();
      });
    });
  }
  
  // Navigation
  elements.openDashboard.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.sendMessage({ action: 'openDashboard' });
  });
  
  elements.openSettings.addEventListener('click', (e) => {
    e.preventDefault();
    if (chrome.runtime.openOptionsPage) {
      chrome.runtime.openOptionsPage();
    } else {
      chrome.tabs.create({ url: 'options.html' });
    }
  });
  
  elements.openHelp.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: 'https://github.com/yourusername/ats-scanner/wiki' });
  });
  
  // Login buttons
  elements.loginBtn.addEventListener('click', () => {
    chrome.tabs.create({ url: 'http://localhost:8501' });
  });
  
  elements.continueAsGuestBtn.addEventListener('click', () => {
    elements.loginSection.classList.add('hidden');
    elements.uploadSection.classList.remove('hidden');
  });
}

// Handle resume upload
async function handleResumeUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Check file size (5MB limit)
  if (file.size > 5 * 1024 * 1024) {
    showError('File size must be less than 5MB');
    return;
  }
  
  // Check file type
  const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
  if (!validTypes.includes(file.type) && !file.name.endsWith('.txt')) {
    showError('Please upload PDF, DOCX, or TXT files only');
    return;
  }
  
  showLoading('Uploading resume...');
  
  try {
    // Read file content
    const content = await readFileContent(file);
    
    const resume = {
      name: file.name,
      content: content,
      type: file.type,
      size: file.size,
      uploadedAt: new Date().toISOString()
    };
    
    // Save to storage
    chrome.runtime.sendMessage({
      action: 'saveResume',
      resume: resume
    }, (response) => {
      if (response && response.success) {
        currentResume = resume;
        elements.resumeName.textContent = resume.name;
        elements.uploadSection.classList.add('hidden');
        hideLoading();
        
        // Auto-scan after upload
        if (currentJobDetails && !currentJobDetails.error) {
          setTimeout(() => scanJob(), 500);
        }
        
        console.log('✅ Resume saved:', resume.name);
      } else {
        hideLoading();
        showError('Failed to save resume');
      }
    });
  } catch (error) {
    console.error('❌ File read error:', error);
    hideLoading();
    showError('Failed to read file');
  }
}

// Read file content as text
function readFileContent(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = (e) => reject(e);
    
    if (file.type === 'application/pdf') {
      // For PDF, we just store the name and type
      // Actual parsing happens on backend
      resolve(`[PDF File: ${file.name}]`);
    } else if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      resolve(`[DOCX File: ${file.name}]`);
    } else {
      reader.readAsText(file);
    }
  });
}

// Show upload section
function showUploadSection() {
  elements.uploadSection.classList.remove('hidden');
  elements.resumeUpload.value = '';
  elements.scoreSection.classList.add('hidden');
}

// Open full report in main app
function openFullReport() {
  chrome.tabs.create({ 
    url: 'http://localhost:8501' 
  });
}

// Open resume optimizer
function openOptimizer() {
  chrome.tabs.create({ 
    url: 'http://localhost:8501?mode=build' 
  });
}

// Get settings from storage
async function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['settings'], (result) => {
      resolve(result.settings || { 
        autoScan: true, 
        saveHistory: true,
        apiUrl: 'http://localhost:8000'
      });
    });
  });
}

// UI Helpers
function showLoading(message) {
  if (elements.loadingMessage) {
    elements.loadingMessage.textContent = message || 'Loading...';
  }
  if (elements.loadingOverlay) {
    elements.loadingOverlay.classList.remove('hidden');
  }
}

function hideLoading() {
  if (elements.loadingOverlay) {
    elements.loadingOverlay.classList.add('hidden');
  }
}

function showError(message) {
  console.error('❌ Error:', message);
  
  // Remove any existing error toasts
  const existingToasts = document.querySelectorAll('.error-toast');
  existingToasts.forEach(toast => toast.remove());
  
  // Create error toast
  const toast = document.createElement('div');
  toast.className = 'error-toast';
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 20px;
    right: 20px;
    background: #ef4444;
    color: white;
    padding: 12px;
    border-radius: 8px;
    text-align: center;
    z-index: 2000;
    animation: slideIn 0.3s ease;
  `;
  
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function showRetryButton() {
  if (!elements.retryBtn) {
    const retryBtn = document.createElement('button');
    retryBtn.id = 'retryBtn';
    retryBtn.textContent = '🔄 Retry';
    retryBtn.className = 'small-btn';
    retryBtn.style.marginTop = '10px';
    retryBtn.style.width = '100%';
    retryBtn.addEventListener('click', () => {
      hideError();
      showLoading('Retrying...');
      getJobDetails().then(() => hideLoading());
    });
    
    const jobInfoSection = document.getElementById('jobInfoSection');
    if (jobInfoSection) {
      jobInfoSection.appendChild(retryBtn);
      elements.retryBtn = retryBtn;
    }
  }
}

function hideError() {
  const toasts = document.querySelectorAll('.error-toast');
  toasts.forEach(toast => toast.remove());
  
  if (elements.retryBtn) {
    elements.retryBtn.remove();
    elements.retryBtn = null;
  }
}

// Handle errors
window.addEventListener('error', (e) => {
  console.error('🔥 Popup error:', e.error);
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateY(100%); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateY(0); opacity: 1; }
    to { transform: translateY(100%); opacity: 0; }
  }
  .portal-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
    margin-left: 8px;
    text-transform: uppercase;
  }
`;
document.head.appendChild(style);

console.log('✅ Popup script loaded');