// SIMPLE MODAL STATE TEST
// Run this in the console to check if the conditional rendering is working

console.log('🧪 Testing Modal State Conditions...');

// Simple function to check if modals should render
const checkModalConditions = () => {
    console.log('\n🔍 CHECKING MODAL CONDITIONS:');
    
    // Get current modal count
    const modals = document.querySelectorAll('div[style*="position: fixed"]');
    console.log(`📊 Current fixed position divs: ${modals.length}`);
    
    // Check for modal-related text in the page
    const pageText = document.body.textContent || '';
    const hasJobDetailsText = pageText.includes('Job Details');
    const hasJobResultsText = pageText.includes('Results for Job');
    
    console.log(`📝 Page contains "Job Details": ${hasJobDetailsText}`);
    console.log(`📝 Page contains "Results for Job": ${hasJobResultsText}`);
    
    // Look for modal elements more broadly
    const allElements = document.querySelectorAll('*');
    let modalElements = 0;
    
    Array.from(allElements).forEach(el => {
        const style = getComputedStyle(el);
        if (style.position === 'fixed' && style.zIndex >= 1000) {
            modalElements++;
            console.log('🎯 Found potential modal element:', el);
            console.log('Element style:', style.cssText);
        }
    });
    
    console.log(`📊 High z-index fixed elements: ${modalElements}`);
    
    return {
        modalCount: modals.length,
        hasJobDetailsText,
        hasJobResultsText,
        modalElements
    };
};

// Function to manually inject a test modal
const injectTestModal = () => {
    console.log('\n🧪 INJECTING TEST MODAL:');
    
    // Create a test modal
    const testModal = document.createElement('div');
    testModal.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(255,0,0,0.5);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
        ">
            <div style="
                background-color: white;
                padding: 20px;
                border: 3px solid red;
                border-radius: 8px;
            ">
                <h2>🧪 TEST MODAL</h2>
                <p>If you can see this, modal rendering works!</p>
                <button onclick="this.parentElement.parentElement.parentElement.remove()">Close Test</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(testModal);
    console.log('✅ Test modal injected - should be visible now');
    
    setTimeout(() => {
        console.log('🕐 Test modal still visible?', document.querySelector('h2:contains("TEST MODAL")') ? 'Yes' : 'No');
    }, 1000);
};

// Function to check React component state
const checkReactState = () => {
    console.log('\n🔬 CHECKING REACT COMPONENT STATE:');
    
    // Look for React state indicators in the DOM
    const buttons = document.querySelectorAll('button');
    const detailsButtons = Array.from(buttons).filter(btn => 
        btn.textContent && btn.textContent.includes('Details')
    );
    const resultsButtons = Array.from(buttons).filter(btn => 
        btn.textContent && btn.textContent.includes('View Results')
    );
    
    console.log(`🔘 Details buttons found: ${detailsButtons.length}`);
    console.log(`🔘 View Results buttons found: ${resultsButtons.length}`);
    
    // Check if buttons are enabled/disabled
    detailsButtons.forEach((btn, index) => {
        console.log(`Details button ${index + 1}: enabled=${!btn.disabled}, visible=${btn.offsetParent !== null}`);
    });
    
    resultsButtons.forEach((btn, index) => {
        console.log(`Results button ${index + 1}: enabled=${!btn.disabled}, visible=${btn.offsetParent !== null}`);
    });
};

// Main test function
const runModalStateTest = () => {
    console.log('🚀 RUNNING MODAL STATE TEST');
    console.log('='.repeat(50));
    
    checkModalConditions();
    checkReactState();
    
    console.log('\n💡 Commands available:');
    console.log('- checkModalConditions() - Check current modal state');
    console.log('- injectTestModal() - Inject a test modal to verify rendering works');
    console.log('- checkReactState() - Check React component state');
};

// Make functions available
window.checkModalConditions = checkModalConditions;
window.injectTestModal = injectTestModal;
window.checkReactState = checkReactState;
window.runModalStateTest = runModalStateTest;

console.log('🎯 Modal State Test loaded!');
console.log('💡 Run runModalStateTest() to check modal conditions');
console.log('💡 Run injectTestModal() to test if modal rendering works at all');
