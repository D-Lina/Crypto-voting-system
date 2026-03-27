// Utility functions
const Utils = {
  // Format date
  formatDate: (date) => {
    return new Date(date).toLocaleString();
  },

  // Truncate string
  truncate: (str, length = 10) => {
    if (!str) return "—";
    return str.length > length ? str.substring(0, length) + "…" : str;
  },

  // Show error message
  showError: (container, message) => {
    if (!container) return;
    container.innerHTML = `
            <div class="alert alert-red">
                <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                <div><strong>Error</strong><br><span style="font-family:var(--mono);font-size:0.78rem">${message}</span></div>
            </div>
        `;
  },

  // Show success message
  showSuccess: (container, message) => {
    if (!container) return;
    container.innerHTML = `
            <div class="alert alert-green">
                <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                </svg>
                <div><strong>Success</strong><br><span style="font-family:var(--mono);font-size:0.78rem">${message}</span></div>
            </div>
        `;
  },

  // Show loading skeleton
  showLoading: (container) => {
    if (!container) return;
    container.innerHTML =
      '<div class="skeleton pulse" style="height:200px;border-radius:14px"></div>';
  },

  // Generate random ID
  generateId: () => {
    return Math.random().toString(36).substr(2, 9);
  },

  // Copy to clipboard
  copyToClipboard: async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      console.error("Failed to copy:", err);
      return false;
    }
  },

  // Debounce function
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
};
