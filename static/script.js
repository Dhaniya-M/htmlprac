// script.js (common for all pages)

const translationQueue = new Set();
let translationTimeout = null;
// Cache for language files
// Debounced translation function
function debouncedTranslate() {
  if (translationTimeout) {
    clearTimeout(translationTimeout);
  }
  translationTimeout = setTimeout(() => {
    const currentLang = localStorage.getItem("preferredLanguage") || "en";
    loadLanguage(currentLang);
    translationQueue.clear();
  }, 100);
}
const languageCache = {};
// Special handling for dynamic content
function handleDynamicContentTranslation() {
  // Translate after fetching market prices
  if (typeof fetchPrices === 'function') {
    const originalFetchPrices = fetchPrices;
    window.fetchPrices = function() {
      originalFetchPrices.apply(this);
      debouncedTranslate();
    };
  }
  
  // Translate after weather updates
  if (typeof fetchWeatherData === 'function') {
    const originalFetchWeather = fetchWeatherData;
    window.fetchWeatherData = function() {
      originalFetchWeather.apply(this);
      debouncedTranslate();
    };
  }
}

// Load language file and apply translations
async function loadLanguage(lang) {
  try {
    // Prevent translation if already in progress
    if (document.body.hasAttribute('data-translating')) {
      return;
    }

    // Use cached translation if available
    if (!languageCache[lang]) {
      try {
        const response = await fetch(`./lang/${lang}.json`);
        if (!response.ok) {
          console.warn(`Failed to load ${lang}.json, falling back to English`);
          lang = 'en';
          const enResponse = await fetch('./lang/en.json');
          if (!enResponse.ok) throw new Error('Failed to load fallback language');
          languageCache[lang] = await enResponse.json();
        } else {
          languageCache[lang] = await response.json();
        }
      } catch (e) {
        console.error('Language loading failed:', e);
        return; // Exit if we can't load any language file
      }
    }
    const translations = languageCache[lang];
    
    document.documentElement.dir = ['ar', 'he', 'fa'].includes(lang) ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;

    // Replace text based on data-key attribute
    document.querySelectorAll("[data-key]").forEach(el => {
      const key = el.getAttribute("data-key");
      const keyParts = key.split('.');
      let translation = translations;
      for (const part of keyParts) {
        if (translation && translation[part] !== undefined) {
          translation = translation[part];
        } else {
          if (!translationQueue.has(key)) {
            console.warn(`Translation missing for key: ${key}`);
            translationQueue.add(key);
          }
          translation = null;
          break;
        }
      }

      // Store original text if not already stored
      if (!el.getAttribute('data-original')) {
        el.setAttribute('data-original', el.textContent);
      }

      // For input placeholders
      if (el.tagName === "INPUT" && el.hasAttribute("placeholder")) {
        el.setAttribute("placeholder", translation || el.getAttribute('data-original') || el.getAttribute("placeholder"));
      } 
      // For select options
      else if (el.tagName === "OPTION") {
        el.text = translation || el.getAttribute('data-original') || el.text;
      }
      // For normal text content
      else {
        let finalText = translation || el.getAttribute('data-original') || el.textContent;
        if (finalText.includes('{user}') && window.username) {
          finalText = finalText.replace('{user}', window.username);
        }
        el.textContent = finalText;
        // Update title attribute if it exists
        if (el.hasAttribute('title')) {
          el.setAttribute('title', finalText);
        }
      }
    });
    // Handle dynamic content updates
    handleDynamicContentTranslation();
  } catch (error) {
    console.error("Error loading language:", error);
  }
}

// Language dropdown handler
function setupLanguageSelector() {
  // Find all language selectors in the page
  const selectors = document.querySelectorAll("#languageSelect, [data-role='language-selector']");
  const savedLang = localStorage.getItem("preferredLanguage") || "en";

  selectors.forEach(selector => {
    // Set initial value
    selector.value = savedLang;

    // Remove any existing listeners to prevent duplicates
    selector.removeEventListener("change", handleLanguageChange);
    
    selector.addEventListener("change", handleLanguageChange);
  });

  // Initial translation after a slight delay to ensure DOM is ready
  setTimeout(() => {
    loadLanguage(savedLang).catch(e => console.error('Initial translation failed:', e));
    
    // Reload dynamic content if needed
    if (typeof fetchPrices === 'function') {
      try {
        fetchPrices();
      } catch (e) {
        console.warn('Failed to fetch prices:', e);
      }
    }
    if (typeof fetchWeatherData === 'function') {
      try {
        fetchWeatherData();
      } catch (e) {
        console.warn('Failed to fetch weather:', e);
      }
    }
  }, 100);

  // Load the saved language when page loads
  loadLanguage(savedLang);
}

function handleLanguageChange(event) {
  const lang = event.target.value;
  localStorage.setItem("preferredLanguage", lang);
  // Also store in a cookie so server-side can read it on next request
  document.cookie = `preferred_lang=${lang}; path=/; max-age=${60*60*24*365}`;
  
  // Update all language selectors to the same value
  document.querySelectorAll("#languageSelect, [data-role='language-selector']")
    .forEach(selector => selector.value = lang);
  
  // Load new language
  loadLanguage(lang);
}

// Get username from PHP session
function getUserName() {
  const welcomeText = document.querySelector('[data-key="home.welcome"]');
  if (welcomeText) {
    const userMatch = welcomeText.textContent.match(/Welcome, (.+)!/);
    if (userMatch && userMatch[1]) {
      window.username = userMatch[1].trim();
    }
  }
}

  // Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  getUserName();
  setupLanguageSelector();
  
  let translateTimeout = null;
  let lastTranslation = Date.now();
  const TRANSLATION_THROTTLE = 500; // Minimum ms between translations
  
  // Apply translation when dynamic content is updated
  const observer = new MutationObserver((mutations) => {
    const currentTime = Date.now();
    if (currentTime - lastTranslation < TRANSLATION_THROTTLE) {
      // Skip if too soon after last translation
      return;
    }

    const currentLang = localStorage.getItem("preferredLanguage") || "en";
    const needsTranslation = mutations.some(mutation => {
      // Skip mutations caused by our own translations
      if (mutation.target.hasAttribute('data-translating')) {
        return false;
      }
      return mutation.type === "childList" && 
             (mutation.target.hasAttribute("data-key") || 
              [...mutation.addedNodes].some(node => 
                node.nodeType === 1 && (
                  node.hasAttribute("data-key") || 
                  node.querySelector("[data-key]")
                )
              ));
    });
    
    if (needsTranslation) {
      if (translateTimeout) {
        clearTimeout(translateTimeout);
      }
      translateTimeout = setTimeout(() => {
        document.body.setAttribute('data-translating', 'true');
        loadLanguage(currentLang).finally(() => {
          document.body.removeAttribute('data-translating');
          lastTranslation = Date.now();
        });
      }, 100);
    }
  });
  
  // Also translate when AJAX content is loaded, with throttling
  const originalXHR = window.XMLHttpRequest;
  window.XMLHttpRequest = function() {
    const xhr = new originalXHR();
    xhr.addEventListener('load', function() {
      const currentTime = Date.now();
      if (currentTime - lastTranslation >= TRANSLATION_THROTTLE) {
        setTimeout(() => {
          document.body.setAttribute('data-translating', 'true');
          loadLanguage(localStorage.getItem("preferredLanguage") || "en")
            .finally(() => {
              document.body.removeAttribute('data-translating');
              lastTranslation = Date.now();
            });
        }, 100);
      }
    });
    return xhr;
  };

  // Observe the entire document for changes
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
});