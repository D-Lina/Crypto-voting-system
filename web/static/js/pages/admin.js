
// Admin Page Module
const AdminPage = {
  // State
  isAuthenticated: false,

  // Initialize admin page
  init: async () => {
    if (window.activePin) {
      AdminPage.isAuthenticated = true;
      await AdminPage.renderDashboard();
    } else {
      AdminPage.renderGate();
    }
    AdminPage.attachEventListeners();
  },

  // Render admin gate (PIN entry)
  renderGate: () => {
    const html = `
            <div class="admin-gate fade-up">
                <div class="admin-gate-icon">
                    <svg width="36" height="36" fill="none" stroke="var(--amber)" viewBox="0 0 24 24" stroke-width="1.8">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6-4h12m-6 0v-4m0 4h4m-4 0H6"/>
                    </svg>
                </div>
                <div class="page-title">Admin Access</div>
                <div class="page-sub">Enter your administrator PIN to continue</div>
                <input type="password" id="pin-input" placeholder="••••••" maxlength="6"
                    style="text-align:center;letter-spacing:0.3em;font-size:1.3rem;margin-bottom:12px"/>
                <button class="btn btn-full" style="background:linear-gradient(135deg,var(--amber),#f7c26a);color:#000;font-weight:700" id="pin-btn">
                    Unlock Admin Panel
                </button>
                <div id="pin-err" style="display:none;color:var(--red);font-size:0.78rem;margin-top:12px;font-family:var(--mono)"></div>
            </div>
        `;

    document.getElementById("page-content").innerHTML = html;
  },

  // Render admin dashboard
  renderDashboard: async () => {
    const html = `
            <div class="fade-up">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:28px">
                    <div>
                        <div class="page-title">Admin Dashboard</div>
                        <div class="page-sub" style="margin-bottom:0">Manage the cryptographic voting session lifecycle.</div>
                    </div>
                    <button id="admin-signout" class="btn btn-outline" style="font-size:0.78rem">Sign out</button>
                </div>
                <div id="admin-body" class="admin-layout">
                    <div class="skeleton pulse" style="height:400px;border-radius:14px"></div>
                    <div style="display:flex;flex-direction:column;gap:16px">
                        <div class="skeleton pulse" style="height:160px;border-radius:14px"></div>
                        <div class="skeleton pulse" style="height:140px;border-radius:14px"></div>
                    </div>
                </div>
            </div>
        `;

    document.getElementById("page-content").innerHTML = html;
    await AdminPage.updateDashboard();
  },

  // Update dashboard content
  updateDashboard: async () => {
    try {
      const status = await API.getAdminStatus();
      const state = status.state;
      const vc = status.voter_count || 0;

      // Update keys display
      if (status.admin_n) {
        window.adminKeys = {
          admin_e: status.admin_e,
          admin_n: status.admin_n,
        };
        AdminPage.updateKeysDisplay();
      }

      const states = ["IDLE", "VOTING", "CLOSED", "COUNTED"];
      const ai = states.indexOf(state);

      const stepsHtml = states
        .map((s, i) => {
          const done = i < ai;
          const active = i === ai;
          let action = "";

          if (s === "IDLE" && state === "IDLE") {
            action = `
                        <div style="margin-top:20px;padding-top:20px;border-top:1px solid var(--border)">
                            <label>Voter List (N1,N2 per line)</label>
                            <textarea id="voter-list" rows="4" style="font-size:0.78rem;margin-bottom:10px">VOTER001,BALLOT001\nVOTER002,BALLOT002\nVOTER003,BALLOT003</textarea>
                            <div class="setup-grid" style="margin-bottom:12px">
                                <div><label>Admin Prime p</label><input id="ap" type="number" value="61"/></div>
                                <div><label>Admin Prime q</label><input id="aq" type="number" value="53"/></div>
                                <div><label>Counter Prime p</label><input id="cp" type="number" value="47"/></div>
                                <div><label>Counter Prime q</label><input id="cq" type="number" value="59"/></div>
                            </div>
                            <button id="btn-setup" class="btn btn-cyan">Setup &amp; Open Election</button>
                        </div>
                    `;
          } else if (s === "VOTING" && state === "VOTING") {
            action = `
                        <div style="margin-top:16px">
                            <div style="font-size:1.8rem;font-weight:700;font-family:var(--mono);color:var(--cyan);margin-bottom:4px">${vc}</div>
                            <div style="font-size:0.72rem;font-family:var(--mono);color:var(--text-muted);margin-bottom:14px">Registered voters</div>
                            <button id="btn-close" class="btn" style="background:linear-gradient(135deg,var(--amber),#f7c26a);color:#000;font-weight:700">Close Voting</button>
                        </div>
                    `;
          } else if (s === "CLOSED" && state === "CLOSED") {
            action = `
                        <div style="margin-top:16px">
                            <div style="font-size:0.78rem;font-family:var(--mono);color:var(--text-muted);margin-bottom:14px">Voting is closed. Count all ballots to reveal results.</div>
                            <button id="btn-count" class="btn btn-cyan">Count &amp; Reveal Results</button>
                        </div>
                    `;
          } else if (s === "COUNTED" && state === "COUNTED") {
            action = `
                        <div style="margin-top:16px">
                            <button class="btn btn-purple" id="btn-view-res">View Data</button>
                        </div>
                    `;
          }

          return `
                    <div class="step-item${active ? " active" : ""}">
                        <div>
                            <div class="step-num">${i + 1}. ${
            s.charAt(0) + s.slice(1).toLowerCase()
          } Phase</div>
                            <div class="step-name">${
                              [
                                "Setup Election",
                                "Polling Phase",
                                "Counting Phase",
                                "View Results",
                              ][i]
                            }</div>
                            <div class="step-desc">${
                              [
                                "Initialize voters and generate RSA keys.",
                                "Accepting blinded ballots from eligible voters.",
                                "Decrypt and tally accepted ballots.",
                                "Explore cryptographic audit trail and final tally.",
                              ][i]
                            }</div>
                            ${action}
                        </div>
                        <div class="step-check${
                          done ? " done" : active ? " active-step" : ""
                        }">
                            ${
                              done
                                ? `<svg width="14" height="14" fill="none" stroke="var(--green)" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>`
                                : active
                                ? `<svg width="14" height="14" fill="none" stroke="var(--cyan)" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>`
                                : ""
                            }
                        </div>
                    </div>
                `;
        })
        .join("");

      const rightPanels = `
                <div class="keys-panel">
                    <div class="keys-card">
                        <div class="keys-card-title">Keys &amp; Crypto</div>
                        <div class="key-row">
                            <label>Admin Public Key (n)</label>
                            <div class="key-display" id="kd-admin-n">${
                              window.adminKeys?.admin_n || "—"
                            }</div>
                        </div>
                        <div class="key-row">
                            <label>Counter Public Key (n)</label>
                            <div class="key-display" id="kd-counter-n">${
                              status.counter_n || "—"
                            }</div>
                        </div>
                    </div>
                    <div class="danger-card">
                        <div class="danger-title">
                            <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                            Danger Zone
                        </div>
                        <div class="danger-desc">Resetting will clear all ballots, generated keys, and audit logs. This cannot be undone.</div>
                        <button id="btn-reset" class="btn btn-danger" style="font-size:0.78rem">↺ Reset System</button>
                    </div>
                </div>
            `;

      const adminBody = document.getElementById("admin-body");
      if (adminBody) {
        adminBody.innerHTML = `
                    <div class="session-control">
                        <div class="session-title">
                            <span class="status-dot" style="width:8px;height:8px;margin:0"></span>
                            Session Control
                        </div>
                        ${stepsHtml}
                    </div>
                    ${rightPanels}
                `;

        AdminPage.bindDashboardEvents();
      }
    } catch (error) {
      const adminBody = document.getElementById("admin-body");
      if (adminBody) {
        adminBody.innerHTML = `<div class="alert alert-red">${error.message}</div>`;
      }
    }
  },

  // Bind dashboard events
  bindDashboardEvents: () => {
    document
      .getElementById("btn-setup")
      ?.addEventListener("click", async () => {
        const lines = document
          .getElementById("voter-list")
          .value.split("\n")
          .filter((l) => l.includes(","));
        const voters = lines.map((l) => {
          const [n1, n2] = l.split(",").map((s) => s.trim());
          return { n1, n2 };
        });

        await API.setupElection({
          pin: window.activePin,
          voters,
          admin_primes: [
            parseInt(document.getElementById("ap").value),
            parseInt(document.getElementById("aq").value),
          ],
          counter_primes: [
            parseInt(document.getElementById("cp").value),
            parseInt(document.getElementById("cq").value),
          ],
        });

        await AdminPage.updateDashboard();
      });

    document
      .getElementById("btn-close")
      ?.addEventListener("click", async () => {
        await API.closeVoting(window.activePin);
        await AdminPage.updateDashboard();
      });

    document
      .getElementById("btn-count")
      ?.addEventListener("click", async () => {
        await API.countVotes(window.activePin);
        await AdminPage.updateDashboard();
      });

    document.getElementById("btn-view-res")?.addEventListener("click", () => {
      window.app.navigateTo("results");
    });

    document
      .getElementById("btn-reset")
      ?.addEventListener("click", async () => {
        if (
          confirm(
            "⚠️ Permanently delete ALL ballots and reset. Cannot be undone."
          )
        ) {
          await API.resetSystem(window.activePin);
          window.adminKeys = null;
          AdminPage.updateKeysDisplay();
          await AdminPage.updateDashboard();
        }
      });
  },

  // Update keys display in sidebar
  updateKeysDisplay: () => {
    const el = document.getElementById("keys-display");
    if (!window.adminKeys) {
      el.innerHTML =
        '<span style="color:var(--text-muted)">No keys generated</span>';
      return;
    }
    el.innerHTML = `
            <div class="key-val">Admin_e: ${window.adminKeys.admin_e}</div>
            <div class="key-val">Admin_n: ${window.adminKeys.admin_n}</div>
        `;
  },

  // Attach event listeners
  attachEventListeners: () => {
    if (!AdminPage.isAuthenticated) {
      const pinBtn = document.getElementById("pin-btn");
      const pinInput = document.getElementById("pin-input");

      pinBtn?.addEventListener("click", async () => {
        const pin = pinInput.value;
        try {
          await API.verifyAdminPin(pin);
          window.activePin = pin;
          AdminPage.isAuthenticated = true;
          await AdminPage.init();
        } catch (error) {
          const errEl = document.getElementById("pin-err");
          errEl.textContent = error.message;
          errEl.style.display = "block";
        }
      });

      pinInput?.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          document.getElementById("pin-btn").click();
        }
      });
    } else {
      const signoutBtn = document.getElementById("admin-signout");
      signoutBtn?.addEventListener("click", () => {
        window.activePin = null;
        window.adminKeys = null;
        AdminPage.isAuthenticated = false;
        AdminPage.updateKeysDisplay();
        AdminPage.init();
      });
    }
  },
};
