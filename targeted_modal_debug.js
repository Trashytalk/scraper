// TARGETED MODAL STATE DEBUGGING
// Run this after the main test to get more detailed state information

console.log('🔍 Running targeted modal state debugging...');

// Function to check React state and modal rendering
const debugModalState = () => {
    console.log('\n🔬 DETAILED STATE ANALYSIS:');
    
    // 1. Check for modals in DOM
    const modals = document.querySelectorAll('div[style*="position: fixed"]');
    console.log(`📊 Fixed position divs in DOM: ${modals.length}`);
    
    if (modals.length > 0) {
        modals.forEach((modal, index) => {
            console.log(`Modal ${index + 1}:`, modal);
            console.log(`Modal ${index + 1} style:`, modal.style.cssText);
            console.log(`Modal ${index + 1} display:`, getComputedStyle(modal).display);
            console.log(`Modal ${index + 1} visibility:`, getComputedStyle(modal).visibility);
            console.log(`Modal ${index + 1} z-index:`, getComputedStyle(modal).zIndex);
        });
    }
    
    // 2. Check for any hidden modals
    const hiddenModals = document.querySelectorAll('div[style*="display: none"]');
    console.log(`📊 Hidden divs (display: none): ${hiddenModals.length}`);
    
    // 3. Check for modal-related elements
    const modalKeywords = ['modal', 'dialog', 'popup', 'overlay'];
    modalKeywords.forEach(keyword => {
        const elements = document.querySelectorAll(`[class*="${keyword}"], [id*="${keyword}"]`);
        console.log(`📊 Elements with "${keyword}": ${elements.length}`);
    });
    
    // 4. Check for React state in the DOM
    console.log('\n🔍 SEARCHING FOR REACT STATE CLUES:');
    
    // Look for React fiber nodes (development mode)
    const reactElements = document.querySelectorAll('[data-reactroot], [data-react-fiber]');
    console.log(`React root elements: ${reactElements.length}`);
    
    // Look for any elements that might contain modal content
    const jobDetailTexts = Array.from(document.querySelectorAll('*')).filter(el => 
        el.textContent && el.textContent.includes('Job Details')
    );
    console.log(`Elements containing "Job Details": ${jobDetailTexts.length}`);
    
    // 5. Check for conditional rendering clues
    const allDivs = document.querySelectorAll('div');
    console.log(`📊 Total div elements: ${allDivs.length}`);
    
    // Look for React conditional rendering artifacts
    const reactComments = document.evaluate(
        '//comment()[contains(., "react")]',
        document,
        null,
        XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
        null
    );
    console.log(`React-related comments: ${reactComments.snapshotLength}`);
    
    return {
        modalCount: modals.length,
        hiddenModals: hiddenModals.length,
        totalDivs: allDivs.length,
        jobDetailElements: jobDetailTexts.length
    };
};

// Function to manually trigger modal functions and watch state
const debugModalFunctions = async () => {
    console.log('\n🧪 MANUALLY TESTING MODAL FUNCTIONS:');
    
    // Find a Details button
    const detailsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
        btn.textContent && btn.textContent.includes('Details')
    );
    
    if (detailsButtons.length === 0) {
        console.log('❌ No Details buttons found');
        return;
    }
    
    console.log(`Found ${detailsButtons.length} Details buttons`);
    
    // Monitor DOM changes
    let mutationCount = 0;
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutationCount++;
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1 && node.tagName === 'DIV') {
                        const style = getComputedStyle(node);
                        if (style.position === 'fixed') {
                            console.log('🎯 NEW FIXED POSITION DIV ADDED:', node);
                            console.log('Style:', style.cssText);
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true
    });
    
    console.log('🔄 Starting DOM mutation monitoring...');
    console.log('📊 Initial state:', debugModalState());
    
    // Click button and monitor
    console.log('🖱️ Clicking Details button...');
    detailsButtons[0].click();
    
    // Wait and check multiple times
    for (let i = 0; i < 5; i++) {
        await new Promise(resolve => setTimeout(resolve, 200));
        console.log(`⏱️ Check ${i + 1} (${(i + 1) * 200}ms):`, debugModalState());
    }
    
    console.log(`🔄 Total DOM mutations observed: ${mutationCount}`);
    observer.disconnect();
};

// Function to inspect React DevTools data
const inspectReactState = () => {
    console.log('\n🔬 REACT STATE INSPECTION:');
    
    // Check if React DevTools is available
    if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
        console.log('✅ React DevTools detected');
        
        // Try to access React fiber
        const reactFiber = document.querySelector('#root')._reactInternalFiber || 
                          document.querySelector('#root')._reactInternals;
        
        if (reactFiber) {
            console.log('✅ React fiber found:', reactFiber);
        } else {
            console.log('❌ Could not access React fiber');
        }
    } else {
        console.log('❌ React DevTools not available');
    }
    
    // Alternative: Look for React props/state in DOM
    const rootElement = document.querySelector('#root, [data-reactroot]');
    if (rootElement) {
        console.log('✅ React root element found:', rootElement);
        console.log('Root element keys:', Object.keys(rootElement));
        
        // Look for React properties
        const reactKeys = Object.keys(rootElement).filter(key => 
            key.startsWith('__react') || key.startsWith('_react')
        );
        console.log('React-related keys:', reactKeys);
    }
};

// Run all debugging functions
const runCompleteDebug = async () => {
    console.log('🚀 STARTING COMPLETE MODAL DEBUG ANALYSIS');
    console.log('='.repeat(60));
    
    console.log('\n1. Initial State Check:');
    debugModalState();
    
    console.log('\n2. React State Inspection:');
    inspectReactState();
    
    console.log('\n3. Manual Function Testing:');
    await debugModalFunctions();
    
    console.log('\n✅ Complete debug analysis finished!');
};

// Make functions available globally
window.debugModalState = debugModalState;
window.debugModalFunctions = debugModalFunctions;
window.inspectReactState = inspectReactState;
window.runCompleteDebug = runCompleteDebug;

console.log('🎯 Targeted debugging ready!');
console.log('Available functions:');
console.log('- debugModalState() - Check current modal state');
console.log('- debugModalFunctions() - Test modal functions with monitoring');
console.log('- inspectReactState() - Inspect React state');
console.log('- runCompleteDebug() - Run all debugging functions');
console.log('');
console.log('💡 Run runCompleteDebug() for comprehensive analysis');
