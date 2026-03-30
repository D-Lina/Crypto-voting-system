
// Main Application
const App = {
  currentPage: "home",
  pollTimer: null,

  // Initialize app
  init: () => {
    App.setupNetworkCanvas();
    App.renderNav();
    App.navigateTo("home");
    App.startPolling();
  },

  // Setup network animation canvas
  setupNetworkCanvas: () => {
    const canvas = document.getElementById("network-canvas");
    const ctx = canvas.getContext("2d");
    let nodes = [];
    const COUNT = 60;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resize();
    window.addEventListener("resize", resize);

    for (let i = 0; i < COUNT; i++) {
      nodes.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 2 + 1,
      });
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      nodes.forEach((n) => {
        n.x += n.vx;
        n.y += n.vy;
        if (n.x < 0 || n.x > canvas.width) n.vx *= -1;
        if (n.y < 0 || n.y > canvas.height) n.vy *= -1;
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(0,200,180,0.7)";
        ctx.fill();
      });

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const d = Math.sqrt(dx * dx + dy * dy);
          if (d < 120) {
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.strokeStyle = `rgba(0,200,180,${(1 - d / 120) * 0.25})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(draw);
    };

    draw();
  },

  // Render navigation sidebar
  renderNav: () => {
    const nav = document.getElementById("sidebar-nav");
    const items = [
      {
        id: "home",
        label: "Overview",
        icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
      },
      {
        id: "admin",
        label: "Admin Panel",
        icon: "M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z",
      },
      {
        id: "vote",
        label: "Cast Vote",
        icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
      },
      {
        id: "results",
        label: "Results",
        icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10",
      },
      {
        id: "audit",
        label: "Audit Log",
        icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
      },
    ];

    nav.innerHTML = items
      .map(
        (item) => `
            <a class="nav-item${
              App.currentPage === item.id ? " active" : ""
            }" data-page="${item.id}" href="#">
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="${
                      item.icon
                    }"/>
                </svg>
                ${item.label}
            </a>
        `
      )
      .join("");

    nav.querySelectorAll("[data-page]").forEach((el) => {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        App.navigateTo(el.dataset.page);
      });
    });
  },

  // Navigate to page
  navigateTo: async (page) => {
    if (App.pollTimer) clearInterval(App.pollTimer);
    App.currentPage = page;
    App.renderNav();

    // Render appropriate page
    switch (page) {
      case "home":
        await HomePage.init();
        break;
      case "admin":
        await AdminPage.init();
        break;
      case "vote":
        await VotePage.init();
        break;
      case "results":
        await ResultsPage.init();
        break;
      case "audit":
        await AuditPage.init();
        break;
    }

    App.startPolling();
    await App.fetchStatus();
  },

  // Fetch election status
  fetchStatus: async () => {
    try {
      const status = await API.getElectionStatus();
      window.cachedState = {
        state: status.state,
        voter_count: status.voter_count || 0,
        ballots_cast: status.ballots_cast || 0,
      };
      App.updateTopBar();

      // Update home page if it's active
      if (App.currentPage === "home") {
        const homeCast = document.getElementById("home-cast");
        if (homeCast) {
          homeCast.textContent = window.cachedState.ballots_cast;
        }
      }
    } catch (error) {
      console.warn("Failed to fetch status:", error);
    }
  },

  // Update top bar
  updateTopBar: () => {
    const state = window.cachedState?.state || "IDLE";
    const dot = document.getElementById("state-dot");
    const label = document.getElementById("state-label");
    const tbCast = document.getElementById("tb-cast");
    const tbTotal = document.getElementById("tb-total");

    label.textContent = `SYSTEM: ${state}`;
    dot.className =
      "status-dot" +
      (state === "VOTING"
        ? ""
        : state === "COUNTED"
        ? ""
        : state === "CLOSED"
        ? " amber"
        : "");

    if (tbCast) tbCast.textContent = window.cachedState?.ballots_cast || 0;
    if (tbTotal) tbTotal.textContent = window.cachedState?.voter_count || 0;
  },

  // Start polling for status updates
  startPolling: () => {
    if (App.pollTimer) clearInterval(App.pollTimer);
    App.pollTimer = setInterval(() => App.fetchStatus(), 5000);
  },
};

// Global variables
window.activePin = null;
window.adminKeys = null;
window.cachedState = { state: "IDLE", voter_count: 0 };
window.app = App;

// Initialize app when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
