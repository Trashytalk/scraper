// SIMPLE Modal Debugging Script - Copy & Paste This!
console.log('🕵️ Simple modal debugging started...');

// Track button clicks
document.addEventListener('click', (event) => {
  if (event.target.tagName === 'BUTTON') {
    const buttonText = event.target.textContent.trim();
    console.log(`🖱️ Button clicked: "${buttonText}"`);
    
    if (buttonText.includes('Details') || buttonText.includes('View Results')) {
      console.log('🎯 MODAL TRIGGER BUTTON CLICKED!');
      
      // Check for modal after click
      setTimeout(() => {
        const modals = document.querySelectorAll('div[style*="position: fixed"]');
        console.log(`📊 Modals found: ${modals.length}`);
        if (modals.length === 0) {
          console.log('❌ NO MODAL APPEARED!');
        } else {
          console.log('✅ Modal found:', modals[0]);
        }
      }, 500);
    }
  }
});

// Track API calls
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

// Quick test functions
window.testButtons = () => {
  const detailsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('Details')
  );
  const resultsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('View Results')
  );
  
  console.log(`Found ${detailsButtons.length} Details buttons, ${resultsButtons.length} Results buttons`);
  
  if (detailsButtons.length > 0) {
    console.log('Testing first Details button...');
    detailsButtons[0].click();
  }
};

window.checkModals = () => {
  const modals = document.querySelectorAll('div[style*="position: fixed"]');
  console.log(`Current modals: ${modals.length}`);
  return modals;
};

console.log('✅ Simple debugging ready!');
console.log('Commands: testButtons(), checkModals()');
