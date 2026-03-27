
// API Base URL
const API_BASE = "/pyapi";

// API Service
const API = {
  // Generic fetch with error handling
  async fetch(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    // Add admin PIN if this is an admin endpoint
    if (
      path.includes("/admin/") &&
      path !== "/admin/verify-pin" &&
      window.activePin
    ) {
      headers["X-Admin-Pin"] = window.activePin;
    }

    try {
      const response = await fetch(API_BASE + path, {
        ...options,
        headers,
      });

      let data;
      try {
        data = await response.json();
      } catch (e) {
        data = { error: "Invalid server response" };
      }

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API Error (${path}):`, error);
      throw error;
    }
  },

  // Election endpoints
  getElectionStatus: () => {
    return API.fetch("/election/status");
  },

  // Admin endpoints
  verifyAdminPin: (pin) => {
    return API.fetch("/admin/verify-pin", {
      method: "POST",
      body: JSON.stringify({ pin }),
    });
  },

  getAdminStatus: () => {
    return API.fetch("/admin/status");
  },

  setupElection: (data) => {
    return API.fetch("/admin/setup", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  closeVoting: (pin) => {
    return API.fetch("/admin/close", {
      method: "POST",
      body: JSON.stringify({ pin }),
    });
  },

  countVotes: (pin) => {
    return API.fetch("/admin/count", {
      method: "POST",
      body: JSON.stringify({ pin }),
    });
  },

  resetSystem: (pin) => {
    return API.fetch("/admin/reset", {
      method: "POST",
      body: JSON.stringify({ pin }),
    });
  },

  getAuditTrail: () => {
    return API.fetch("/admin/audit");
  },

  // Vote endpoint
  castVote: (voteData) => {
    return API.fetch("/vote", {
      method: "POST",
      body: JSON.stringify(voteData),
    });
  },

  // Results endpoint
  getResults: () => {
    return API.fetch("/results");
  },
};
