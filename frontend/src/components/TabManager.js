// Tab Manager for Enhanced OCR Results
export const initializeTabs = () => {
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupTabs);
  } else {
    setupTabs();
  }
};

const setupTabs = () => {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  if (tabButtons.length === 0) return;

  // Add click event listeners to tab buttons
  tabButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
      const targetTab = button.getAttribute('data-tab');
      switchTab(targetTab, tabButtons, tabPanels);
    });
  });

  // Initialize first tab as active if none are active
  const activeTab = document.querySelector('.tab-btn.active');
  if (!activeTab && tabButtons.length > 0) {
    tabButtons[0].click();
  }
};

const switchTab = (targetTab, tabButtons, tabPanels) => {
  // Remove active class from all tabs and panels
  tabButtons.forEach(btn => {
    btn.classList.remove('active');
    // Reset indicator width
    const indicator = btn.querySelector('.tab-indicator');
    if (indicator) {
      indicator.style.width = '0%';
    }
  });
  
  tabPanels.forEach(panel => {
    panel.classList.remove('active');
  });

  // Add active class to clicked tab
  const activeButton = document.querySelector(`[data-tab="${targetTab}"]`);
  const activePanel = document.getElementById(targetTab);
  
  if (activeButton && activePanel) {
    activeButton.classList.add('active');
    activePanel.classList.add('active');
    
    // Animate indicator
    const indicator = activeButton.querySelector('.tab-indicator');
    if (indicator) {
      setTimeout(() => {
        indicator.style.width = '100%';
      }, 50);
    }

    // Add smooth scroll to tab content
    activePanel.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'nearest' 
    });

    // Trigger custom animation for tab content
    activePanel.style.animation = 'none';
    setTimeout(() => {
      activePanel.style.animation = 'tabFadeIn 0.5s ease-out';
    }, 10);
  }
};

// Auto-initialize when module loads
initializeTabs();

// Re-initialize when new content is loaded (for dynamic content)
export const refreshTabs = () => {
  setTimeout(setupTabs, 100);
};