// Fix for category links - handles base64-encoded category URLs
// This ensures category links work on the published site

(function() {
  'use strict';
  
  // Function to decode a potentially base64-encoded category value
  function decodeCategory(categoryValue) {
    if (!categoryValue) return categoryValue;
    
    // First, try URL decoding
    let decoded = categoryValue;
    try {
      decoded = decodeURIComponent(categoryValue);
    } catch (e) {
      // Not URL encoded or already decoded
      decoded = categoryValue;
    }
    
    // Check if it looks like base64 (no spaces, base64 chars, length >= 4)
    const looksLikeBase64 = !/[\s]/.test(decoded) && 
                            /^[A-Za-z0-9+/]*={0,2}$/.test(decoded) && 
                            decoded.length >= 4;
    
    if (looksLikeBase64) {
      try {
        const base64Decoded = atob(decoded);
        // Verify it's valid text
        if (/^[\x20-\x7E\s]*$/.test(base64Decoded) && base64Decoded.length > 0) {
          return base64Decoded;
        }
      } catch (e) {
        // Base64 decode failed, return URL-decoded value
      }
    }
    
    return decoded;
  }
  
  // Fix hash function that runs before quarto-listing processes it
  function fixHashBeforeProcessing() {
    const hash = window.location.hash;
    if (hash && hash.includes('category=')) {
      const hashMatch = hash.match(/category=([^&]*)/);
      if (hashMatch) {
        const encodedCategory = hashMatch[1];
        const decodedCategory = decodeCategory(encodedCategory);
        
        // If we decoded it, update the URL hash with the decoded value
        if (decodedCategory !== encodedCategory && decodedCategory !== encodedCategory.replace(/%3D/g, '=')) {
          const newHash = hash.replace(
            /category=[^&]*/,
            'category=' + encodeURIComponent(decodedCategory)
          );
          // Use replaceState to avoid triggering navigation
          window.history.replaceState(null, null, newHash);
          return true; // Indicates we fixed it
        }
      }
    }
    return false;
  }
  
  // Intercept the quarto-listing-loaded callback to fix category hash
  const originalQuartoListingLoaded = window['quarto-listing-loaded'];
  window['quarto-listing-loaded'] = function() {
    // Fix the hash BEFORE the original function processes it
    const wasFixed = fixHashBeforeProcessing();
    
    // Call the original function
    if (originalQuartoListingLoaded) {
      originalQuartoListingLoaded();
    }
    
    // If we fixed the hash, trigger category activation again with the correct value
    if (wasFixed) {
      setTimeout(function() {
        const hash = window.location.hash;
        if (hash) {
          const hashMatch = hash.match(/category=([^&]*)/);
          if (hashMatch) {
            const category = decodeURIComponent(hashMatch[1]);
            if (window.quartoListingCategory && window['quarto-listing-loaded']) {
              // Small delay to ensure listing is ready
              setTimeout(function() {
                window.quartoListingCategory(category);
              }, 100);
            }
          }
        }
      }, 200);
    }
  };
  
  // Fix hash immediately on page load
  function fixHashOnLoad() {
    const wasFixed = fixHashBeforeProcessing();
    if (wasFixed) {
      // If we fixed it, wait a bit then trigger the category activation
      setTimeout(function() {
        const hash = window.location.hash;
        if (hash) {
          const hashMatch = hash.match(/category=([^&]*)/);
          if (hashMatch) {
            const category = decodeURIComponent(hashMatch[1]);
            // Wait for quarto-listing to be ready
            const checkReady = setInterval(function() {
              if (window.quartoListingCategory && window['quarto-listing-loaded']) {
                clearInterval(checkReady);
                window.quartoListingCategory(category);
              }
            }, 50);
            // Stop checking after 5 seconds
            setTimeout(function() {
              clearInterval(checkReady);
            }, 5000);
          }
        }
      }, 500);
    }
  }
  
  // Run on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixHashOnLoad);
  } else {
    fixHashOnLoad();
  }
  
  // Also listen for hash changes
  window.addEventListener('hashchange', function() {
    fixHashBeforeProcessing();
  });
  
})();

