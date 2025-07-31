// Run this in browser console to manually test modal functions
// Make sure you're logged in first!

console.log('🧪 Manual Modal Test Starting...');

// Test 1: Check if functions exist
console.log('🔍 Checking if functions are available...');
console.log('- getJobDetails available:', typeof window.getJobDetails);
console.log('- getJobResults available:', typeof window.getJobResults);

// Test 2: Get current state
console.log('📊 Current React state:');
// Note: We can't directly access React state from console, but we can call the functions

// Test 3: Find existing jobs to test with
const findTestJob = () => {
  const jobRows = document.querySelectorAll('[data-job-id]');
  if (jobRows.length > 0) {
    const jobId = jobRows[0].getAttribute('data-job-id');
    console.log('🎯 Found test job ID:', jobId);
    return parseInt(jobId);
  } else {
    console.log('❌ No jobs found with data-job-id attribute');
    return null;
  }
};

// Test 4: Find buttons manually
const findButtons = () => {
  const detailsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('Details')
  );
  const resultsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('View Results')
  );
  
  console.log('🔍 Found buttons:');
  console.log(`- Details buttons: ${detailsButtons.length}`);
  console.log(`- View Results buttons: ${resultsButtons.length}`);
  
  return { detailsButtons, resultsButtons };
};

// Test 5: Simulate clicks
const testButtonClicks = () => {
  const { detailsButtons, resultsButtons } = findButtons();
  
  if (detailsButtons.length > 0) {
    console.log('🖱️ Simulating Details button click...');
    detailsButtons[0].click();
    
    setTimeout(() => {
      console.log('📊 Checking for modal after Details click...');
      const modals = document.querySelectorAll('div[style*="position: fixed"][style*="z-index: 1000"]');
      console.log(`Found ${modals.length} modals`);
    }, 500);
  }
  
  setTimeout(() => {
    if (resultsButtons.length > 0) {
      console.log('🖱️ Simulating View Results button click...');
      resultsButtons[0].click();
      
      setTimeout(() => {
        console.log('📊 Checking for modal after Results click...');
        const modals = document.querySelectorAll('div[style*="position: fixed"][style*="z-index: 1000"]');
        console.log(`Found ${modals.length} modals`);
      }, 500);
    }
  }, 2000);
};

// Run the tests
console.log('🚀 Running tests...');
findTestJob();
findButtons();

console.log('💡 Manual test functions available:');
console.log('- testButtonClicks() - Test clicking buttons');
console.log('- findButtons() - Find available buttons');

// Auto-run button test after 3 seconds
setTimeout(() => {
  console.log('🔄 Auto-running button click test...');
  testButtonClicks();
}, 3000);
