
// === AUTOMATED MODAL TEST SCRIPT ===
console.log('🧪 Starting automated modal tests...');

// Test Configuration
const TEST_JOB_ID = 94;

// Simple debugging setup
document.addEventListener('click', (event) => {
  if (event.target.tagName === 'BUTTON') {
    const buttonText = event.target.textContent.trim();
    console.log(`🖱️ Button clicked: "${buttonText}"`);
    
    if (buttonText.includes('Details') || buttonText.includes('View Results')) {
      console.log('🎯 MODAL TRIGGER BUTTON CLICKED!');
      
      setTimeout(() => {
        const modals = document.querySelectorAll('div[style*="position: fixed"]');
        console.log(`📊 Modals found: ${modals.length}`);
        if (modals.length === 0) {
          console.log('❌ NO MODAL APPEARED!');
        } else {
          console.log('✅ Modal appeared successfully!');
          console.log('Modal element:', modals[0]);
        }
      }, 500);
    }
  }
});

// API call monitoring
const origFetch = window.fetch;
window.fetch = function(...args) {
  const url = args[0];
  console.log(`🌐 API Call: ${url}`);
  
  return origFetch.apply(this, arguments)
    .then(response => {
      console.log(`📥 API Response: ${response.status} for ${url}`);
      return response;
    })
    .catch(error => {
      console.log(`❌ API Error: ${error}`);
      throw error;
    });
};

// Test functions
window.testDetailsButton = () => {
  console.log('🔍 Testing Details button...');
  const detailsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('Details')
  );
  
  if (detailsButtons.length > 0) {
    console.log(`Found ${detailsButtons.length} Details buttons`);
    detailsButtons[0].click();
  } else {
    console.log('❌ No Details buttons found');
  }
};

window.testResultsButton = () => {
  console.log('📊 Testing View Results button...');
  const resultsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('View Results')
  );
  
  if (resultsButtons.length > 0) {
    console.log(`Found ${resultsButtons.length} View Results buttons`);
    resultsButtons[0].click();
  } else {
    console.log('❌ No View Results buttons found');
  }
};

window.checkModalState = () => {
  const modals = document.querySelectorAll('div[style*="position: fixed"]');
  console.log(`Current modals: ${modals.length}`);
  return modals;
};

window.runFullTest = () => {
  console.log('🚀 Running full modal test sequence...');
  
  // Test 1: Check current state
  console.log('Step 1: Checking current state...');
  checkModalState();
  
  // Test 2: Test Details button
  setTimeout(() => {
    console.log('Step 2: Testing Details button...');
    testDetailsButton();
    
    // Test 3: Test Results button (after Details test)
    setTimeout(() => {
      console.log('Step 3: Testing Results button...');
      testResultsButton();
      
      setTimeout(() => {
        console.log('🏁 Test sequence complete!');
        console.log('Final modal state:');
        checkModalState();
      }, 2000);
    }, 3000);
  }, 1000);
};

console.log('✅ Browser testing ready!');
console.log('Commands available:');
console.log('- testDetailsButton() - Test Details modal');
console.log('- testResultsButton() - Test Results modal');
console.log('- checkModalState() - Check for existing modals');
console.log('- runFullTest() - Run complete test sequence');
console.log('');
console.log('🎯 Test job ID: 94');
console.log('💡 After logging in with admin/admin123, run: runFullTest()');
