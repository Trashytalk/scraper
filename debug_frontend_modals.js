// Frontend Modal Debugging Script
// Copy and paste this into the browser console after the page loads

console.log('🔧 Starting frontend modal debugging...');

// 1. Check if React component is mounted and has access to state
const checkReactState = () => {
  console.log('📊 Checking React component state...');
  
  // Look for React DevTools or component instance
  const reactRoot = document.querySelector('#root');
  if (reactRoot) {
    console.log('✅ React root found');
    console.log('React root element:', reactRoot);
  } else {
    console.log('❌ React root not found');
  }
};

// 2. Monitor all fetch requests to see API calls
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('🌐 Fetch called with:', args[0], args[1]);
  return originalFetch.apply(this, arguments)
    .then(response => {
      console.log('📥 Fetch response:', response.status, response.url);
      return response;
    })
    .catch(error => {
      console.log('❌ Fetch error:', error);
      throw error;
    });
};

// 3. Check for any JavaScript errors
window.addEventListener('error', (event) => {
  console.log('🚨 JavaScript Error:', event.error);
});

// 4. Monitor DOM mutations to see if modals are being added/removed
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === 'childList') {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) { // Element node
          const element = node;
          if (element.style && element.style.position === 'fixed' && element.style.zIndex === '1000') {
            console.log('🎯 Modal detected in DOM:', element);
          }
        }
      });
    }
  });
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// 5. Function to simulate button clicks and monitor responses
const simulateButtonClick = (buttonText) => {
  console.log(`🖱️ Simulating click on button containing: "${buttonText}"`);
  
  const buttons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes(buttonText)
  );
  
  if (buttons.length > 0) {
    console.log(`Found ${buttons.length} buttons with text "${buttonText}"`);
    buttons.forEach((button, index) => {
      console.log(`Button ${index + 1}:`, button);
      // Don't actually click, just log for now
    });
  } else {
    console.log(`❌ No buttons found with text "${buttonText}"`);
  }
};

// 6. Function to check current modal state
const checkModalState = () => {
  console.log('🔍 Checking for existing modals in DOM...');
  
  const modals = document.querySelectorAll('div[style*="position: fixed"][style*="z-index: 1000"]');
  console.log(`Found ${modals.length} potential modals`);
  
  modals.forEach((modal, index) => {
    console.log(`Modal ${index + 1}:`, modal);
    console.log('Modal content:', modal.innerHTML.substring(0, 200) + '...');
  });
  
  return modals.length;
};

// Run initial checks
checkReactState();
console.log('📋 Available debugging functions:');
console.log('- simulateButtonClick("Details") - Find Details buttons');
console.log('- simulateButtonClick("View Results") - Find View Results buttons');
console.log('- checkModalState() - Check for existing modals');

console.log('🎯 Next steps:');
console.log('1. Create a batch job');
console.log('2. Run the job');
console.log('3. Try clicking Details or View Results');
console.log('4. Watch the console for logs');

// Auto-check modal state every 2 seconds
setInterval(() => {
  const modalCount = checkModalState();
  if (modalCount > 0) {
    console.log('📊 Modal found! State change detected.');
  }
}, 2000);
