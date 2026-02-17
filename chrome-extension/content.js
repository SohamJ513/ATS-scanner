// Content script - Extracts job details from various job portals

// Job portal patterns - UPDATED with working Naukri selectors
const PORTAL_PATTERNS = {
  naukri: {
    title: [
      '.jd-header-title',
      '.job-details h1',
      'h1.largeHeading',
      '[class*="jobTitle"]',
      '[class*="JobTitle"]',
      '.title h1',
      'h1'
    ],
    company: [
      '.job-details .about-company',
      '.company-name',
      '.subheading',
      '[class*="company"]',
      '[class*="Company"]',
      '.recruiter-info',
      '.job-company'
    ],
    location: [
      '.job-details .location',
      '.loc',
      '.job-location',
      '[class*="location"]',
      '[class*="Location"]',
      '.job-address'
    ],
    description: [
      '.job-details__description',
      '.job-desc',
      '.jd-desc',
      '[class*="description"]',
      '[class*="Description"]',
      '.job-description',
      '.details__description',
      '.job-detail',
      '.jobDescription'
    ]
  },
  indeed: {
    title: [
      'h1.jobsearch-JobInfoHeader-title',
      '.jobTitle',
      '[class*="job-title"]',
      '.jobtitle'
    ],
    company: [
      '.jobsearch-InlineCompanyRating-companyName',
      '.company',
      '[class*="company"]'
    ],
    location: [
      '.jobsearch-JobInfoHeader-subtitle',
      '.location',
      '[class*="location"]'
    ],
    description: [
      '#jobDescriptionText',
      '.jobsearch-JobComponent-description',
      '.jobsearch-jobDescriptionText'
    ]
  },
  linkedin: {
    title: [
      '.job-details-jobs-unified-top-card__job-title',
      'h1',
      '[class*="job-title"]',
      '.top-card-layout__title'
    ],
    company: [
      '.job-details-jobs-unified-top-card__company-name',
      '.company-name',
      '[class*="company"]',
      '.topcard__org-name-link'
    ],
    location: [
      '.job-details-jobs-unified-top-card__bullet',
      '.location',
      '[class*="location"]',
      '.topcard__flavor--bullet'
    ],
    description: [
      '.job-details-jobs-unified-top-card__description',
      '.description',
      '[class*="description"]',
      '.show-more-less-html__markup'
    ]
  },
  foundit: {
    title: ['.job-title', 'h1'],
    company: ['.company-name', '.recruiter-name'],
    location: ['.location', '.job-location'],
    description: ['.job-description', '.description']
  },
  monster: {
    title: ['.job-title', 'h1'],
    company: ['.company-name', '.company'],
    location: ['.location', '.job-location'],
    description: ['.job-description', '.description']
  }
};

// Detect current portal
function getCurrentPortal() {
  const url = window.location.href;
  if (url.includes('naukri.com')) return 'naukri';
  if (url.includes('indeed.com')) return 'indeed';
  if (url.includes('linkedin.com')) return 'linkedin';
  if (url.includes('foundit.in')) return 'foundit';
  if (url.includes('monsterindia.com')) return 'monster';
  return null;
}

// Extract text from first matching selector
function extractText(selectors) {
  if (!selectors) return null;
  
  // Handle both string and array selectors
  const selectorArray = Array.isArray(selectors) ? selectors : [selectors];
  
  for (const selector of selectorArray) {
    try {
      const element = document.querySelector(selector);
      if (element) {
        const text = element.innerText || element.textContent;
        if (text && text.trim().length > 0) {
          return text.trim();
        }
      }
    } catch (e) {
      // Skip invalid selector
    }
  }
  return null;
}

// Check if current page is a job details page
function isJobDetailsPage() {
  const url = window.location.href;
  const portal = getCurrentPortal();
  
  if (portal === 'naukri') {
    // Naukri job details pages usually have these patterns
    return url.includes('/job-details/') || 
           url.includes('/jobs/') || 
           url.includes('/job-listings-') ||
           document.querySelector('.job-details, .jd-header, [class*="jobDetail"], .job-description') !== null;
  }
  
  if (portal === 'indeed') {
    return url.includes('/job/') || url.includes('/viewjob') || url.includes('/jobs?');
  }
  
  if (portal === 'linkedin') {
    return url.includes('/jobs/view/') || url.includes('/jobs/collections/');
  }
  
  return false;
}

// Extract job details based on portal
function extractJobDetails() {
  const portal = getCurrentPortal();
  if (!portal) {
    console.log('No supported portal detected');
    return null;
  }

  console.log('🔍 ATS Scanner - Detected portal:', portal);
  console.log('📍 Current URL:', window.location.href);
  console.log('📄 Is job details page:', isJobDetailsPage());

  // Check if we're on a job details page
  if (!isJobDetailsPage()) {
    console.log('❌ Not a job details page - please click on a specific job');
    return { 
      error: 'NOT_JOB_PAGE',
      message: 'Please click on a specific job posting first' 
    };
  }

  const patterns = PORTAL_PATTERNS[portal];
  
  // Extract title
  let title = extractText(patterns.title);
  console.log('📌 Extracted title:', title);
  
  // Extract company
  let company = extractText(patterns.company);
  console.log('🏢 Extracted company:', company);
  
  // Extract location
  let location = extractText(patterns.location);
  console.log('📍 Extracted location:', location);
  
  // Extract description
  let description = extractText(patterns.description);
  console.log('📝 Extracted description length:', description?.length || 0);
  
  // If no description found with specific selectors, try fallback methods
  if (!description || description.length < 100) {
    console.log('⚠️ Description not found with specific selectors, trying fallback...');
    
    // Try to find any large text block that might be the job description
    const fallbackSelectors = [
      '[class*="description"]',
      '[class*="Description"]',
      '[class*="details"]',
      '[class*="Details"]',
      '[class*="job-detail"]',
      '[class*="JobDetail"]',
      'main',
      'article',
      '.content',
      '.job-content',
      '.job-section'
    ];
    
    for (const selector of fallbackSelectors) {
      const element = document.querySelector(selector);
      if (element) {
        const text = element.innerText || element.textContent;
        if (text && text.length > 200) {
          description = text;
          console.log('✅ Found description with fallback selector:', selector);
          break;
        }
      }
    }
  }
  
  // Clean up description
  if (description) {
    // Remove extra whitespace
    description = description.replace(/\s+/g, ' ').trim();
    // Remove common noise
    description = description.replace(/Apply\s*Now|Share\s*this\s*job|Report\s*this\s*job|Save\s*job/i, '');
    // Limit length
    if (description.length > 5000) {
      description = description.substring(0, 5000) + '...';
    }
  }
  
  // If we still don't have a description, try to get page title as fallback
  if (!description || description.length < 50) {
    description = document.title + ' - ' + (title || 'Job Posting');
  }
  
  // If we couldn't extract title or description, user might be on wrong page
  if (!title) {
    console.log('❌ Failed to extract job title');
    return { 
      error: 'EXTRACTION_FAILED',
      message: 'Could not extract job details. Try clicking on the job title first.' 
    };
  }
  
  // Clean up title - remove common suffixes
  if (title) {
    title = title.replace(/Job in|Jobs in|Job at|Careers|Opening|Vacancy/i, '').trim();
  }
  
  // Clean up company
  if (company) {
    company = company.replace(/at|@|-|,|\|/g, '').trim();
  }
  
  const result = {
    title: title || 'Unknown Position',
    company: company || 'Unknown Company',
    location: location || 'Location Not Specified',
    description: description || 'No description available',
    portal: portal,
    url: window.location.href,
    timestamp: new Date().toISOString()
  };
  
  console.log('✅ Successfully extracted job details:', result.title, 'at', result.company);
  return result;
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getJobDetails') {
    const jobDetails = extractJobDetails();
    sendResponse(jobDetails);
  }
  return true;
});

// Auto-detect job changes (for SPA navigation)
let lastUrl = location.href;
let lastJobCheck = false;

new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    lastJobCheck = isJobDetailsPage();
    console.log('🔄 Page changed - URL:', url, 'Is job page:', lastJobCheck);
    
    // Notify that job page changed
    chrome.runtime.sendMessage({ 
      action: 'jobPageChanged',
      url: url,
      isJobPage: lastJobCheck
    });
  }
}).observe(document, { subtree: true, childList: true });

// Log initial state
console.log('🚀 ATS Scanner Content Script Loaded');
console.log('🌐 Current URL:', window.location.href);
console.log('🎯 Portal:', getCurrentPortal());
console.log('📋 Is Job Details Page:', isJobDetailsPage());

// If we're on a job page, try to extract and log for debugging
if (isJobDetailsPage()) {
  setTimeout(() => {
    const details = extractJobDetails();
    console.log('📊 Auto-extracted job details:', details);
  }, 1000);
}