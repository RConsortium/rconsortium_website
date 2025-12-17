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
  
  // Intercept the quarto-listing-loaded callback to fix category hash
  const originalQuartoListingLoaded = window['quarto-listing-loaded'];
  window['quarto-listing-loaded'] = function() {
    // Fix the hash before processing
    const hash = window.location.hash;
    if (hash) {
      // Parse the hash manually to fix base64-encoded categories
      const hashMatch = hash.match(/category=([^&]*)/);
      if (hashMatch) {
        const encodedCategory = hashMatch[1];
        const decodedCategory = decodeCategory(encodedCategory);
        
        // If we decoded it, update the URL hash with the decoded value
        if (decodedCategory !== encodedCategory) {
          const newHash = hash.replace(
            /category=[^&]*/,
            'category=' + encodeURIComponent(decodedCategory)
          );
          window.history.replaceState(null, null, newHash);
        }
      }
    }
    
    // Call the original function
    if (originalQuartoListingLoaded) {
      originalQuartoListingLoaded();
    }
  };
  
  // Also fix the hash on page load if it's already in the URL
  function fixHashOnLoad() {
    const hash = window.location.hash;
    if (hash) {
      const hashMatch = hash.match(/category=([^&]*)/);
      if (hashMatch) {
        const encodedCategory = hashMatch[1];
        const decodedCategory = decodeCategory(encodedCategory);
        
        if (decodedCategory !== encodedCategory) {
          const newHash = hash.replace(
            /category=[^&]*/,
            'category=' + encodeURIComponent(decodedCategory)
          );
          window.history.replaceState(null, null, newHash);
          // Trigger a hash change event to reload
          window.dispatchEvent(new Event('hashchange'));
        }
      }
    }
  }
  
  // Run on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixHashOnLoad);
  } else {
    fixHashOnLoad();
  }
  
  // Also listen for hash changes
  window.addEventListener('hashchange', fixHashOnLoad);
  
})();

