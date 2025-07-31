// Comprehensive Modal Debugging Script - FIXED VERSION
// Paste this entire script into browser console after loading the page

console.log('🕵️ Starting comprehensive modal debugging...');

// Clear any previous instances
if (window.modalDebugger) {
  console.log('🔄 Clearing previous debugging session...');
  window.modalDebugger.cleanup();
}

// Create debug namespace
window.modalDebugger = {};

// 1. Check React DevTools availability
window.modalDebugger.checkReactDevTools = () => {
  if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
    console.log('✅ React DevTools detected');
  } else {
    console.log('⚠️ React DevTools not detected');
  }
};

// 2. Track all DOM mutations
window.modalDebugger.mutationObserver = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === 'childList') {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1 && node.tagName === 'DIV') {
          const style = window.getComputedStyle(node);
          if (style.position === 'fixed' && style.zIndex >= '1000') {
            console.log('🎯 MODAL ADDED TO DOM:', node);
            console.log('Modal innerHTML preview:', node.innerHTML.substring(0, 200));
            console.log('Modal style:', {
              position: style.position,
              zIndex: style.zIndex,
              display: style.display,
              visibility: style.visibility
            });
          }
        }
      });
      
      mutation.removedNodes.forEach((node) => {
        if (node.nodeType === 1 && node.tagName === 'DIV') {
          const hasModalAttributes = node.innerHTML && node.innerHTML.includes('position: fixed');
          if (hasModalAttributes) {
            console.log('🚫 MODAL REMOVED FROM DOM:', node);
          }
        }
      });
    }
  });
});

window.modalDebugger.mutationObserver.observe(document.body, {
  childList: true,
  subtree: true,
  attributes: true,
  attributeFilter: ['style']
});

// 3. Intercept all fetch requests
window.modalDebugger.originalFetch = window.fetch;
window.fetch = function(...args) {
  const url = args[0];
  const options = args[1] || {};
  
  console.log(`🌐 API Call: ${url}`);
  console.log('Request options:', options);
  
  return window.modalDebugger.originalFetch.apply(this, arguments)
    .then(response => {
      console.log(`📥 API Response: ${response.status} for ${url}`);
      
      // Clone the response to read it without consuming it
      const clonedResponse = response.clone();
      clonedResponse.json().then(data => {
        console.log(`📊 Response data for ${url}:`, data);
      }).catch(() => {
        // Not JSON, ignore
      });
      
      return response;
    })
    .catch(error => {
      console.log(`❌ API Error for ${url}:`, error);
      throw error;
    });
};

// 4. Monitor click events on buttons
window.modalDebugger.clickHandler = (event) => {
  if (event.target.tagName === 'BUTTON') {
    const buttonText = event.target.textContent.trim();
    console.log(`🖱️ Button clicked: "${buttonText}"`);
    
    if (buttonText.includes('Details') || buttonText.includes('View Results')) {
      console.log('🎯 MODAL TRIGGER BUTTON CLICKED!');
      console.log('Button element:', event.target);
      console.log('Button parent:', event.target.parentElement);
      
      // Check for modal after a short delay
      setTimeout(() => {
        const modals = document.querySelectorAll('div[style*="position: fixed"]');
        console.log(`📊 Modals found after button click: ${modals.length}`);
        if (modals.length === 0) {
          console.log('❌ NO MODAL APPEARED AFTER BUTTON CLICK!');
        }
      }, 500);
    }
  }
};

document.addEventListener('click', window.modalDebugger.clickHandler);

// 5. Check for JavaScript errors
window.modalDebugger.errorHandler = (event) => {
  console.log('🚨 JavaScript Error detected:');
  console.log('Error:', event.error);
  console.log('Message:', event.message);
  console.log('Source:', event.filename);
  console.log('Line:', event.lineno);
};

window.modalDebugger.rejectionHandler = (event) => {
  console.log('🚨 Unhandled Promise Rejection:');
  console.log('Reason:', event.reason);
};

window.addEventListener('error', window.modalDebugger.errorHandler);
window.addEventListener('unhandledrejection', window.modalDebugger.rejectionHandler);

// 6. Function to check current state
window.modalDebugger.checkCurrentState = () => {
  console.log('📊 Current DOM state check:');
  
  // Check for existing modals
  const modals = document.querySelectorAll('div[style*="position: fixed"]');
  console.log(`- Fixed position divs: ${modals.length}`);
  
  // Check for job rows
  const jobElements = document.querySelectorAll('[class*="job"], [data-job-id]');
  console.log(`- Job elements found: ${jobElements.length}`);
  
  // Check for buttons
  const detailsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('Details')
  );
  const resultsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('View Results')
  );
  console.log(`- Details buttons: ${detailsButtons.length}`);
  console.log(`- View Results buttons: ${resultsButtons.length}`);
  
  return { modals, detailsButtons, resultsButtons };
};

// 7. Manual testing function
window.modalDebugger.manualTest = () => {
  console.log('🧪 Starting manual test...');
  const { detailsButtons, resultsButtons } = window.modalDebugger.checkCurrentState();
  
  if (detailsButtons.length > 0) {
    console.log('Testing Details button...');
    detailsButtons[0].click();
  } else if (resultsButtons.length > 0) {
    console.log('Testing View Results button...');
    resultsButtons[0].click();
  } else {
    console.log('❌ No test buttons found');
  }
};

// 8. Cleanup function
window.modalDebugger.cleanup = () => {
  if (window.modalDebugger.mutationObserver) {
    window.modalDebugger.mutationObserver.disconnect();
  }
  if (window.modalDebugger.originalFetch) {
    window.fetch = window.modalDebugger.originalFetch;
  }
  if (window.modalDebugger.clickHandler) {
    document.removeEventListener('click', window.modalDebugger.clickHandler);
  }
  if (window.modalDebugger.errorHandler) {
    window.removeEventListener('error', window.modalDebugger.errorHandler);
  }
  if (window.modalDebugger.rejectionHandler) {
    window.removeEventListener('unhandledrejection', window.modalDebugger.rejectionHandler);
  }
  if (window.modalDebugger.stateInterval) {
    clearInterval(window.modalDebugger.stateInterval);
  }
};

// Run initial checks
window.modalDebugger.checkReactDevTools();
window.modalDebugger.checkCurrentState();

console.log('🎯 Debugging setup complete!');
console.log('Available functions:');
console.log('- modalDebugger.checkCurrentState() - Check current DOM state');
console.log('- modalDebugger.manualTest() - Manually test button clicks');
console.log('- modalDebugger.cleanup() - Clean up debugging session');

console.log('👀 Now watching for:');
console.log('- Button clicks');
console.log('- DOM changes (modals)');
console.log('- API calls');
console.log('- JavaScript errors');
console.log('- All console logs from the app');

// Auto-check state every 10 seconds (reduced frequency)
window.modalDebugger.stateInterval = setInterval(window.modalDebugger.checkCurrentState, 10000);
