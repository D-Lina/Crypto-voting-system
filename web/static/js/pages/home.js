// Home Page Module
const HomePage = {
  // Cache DOM elements
  elements: {},

  // Initialize home page
  init: async () => {
    await HomePage.render();
    HomePage.attachEventListeners();
  },

  // Render home page
  render: () => {
    const state = window.cachedState || { state: "IDLE", voter_count: 0 };
    const s = state.state;
    const vc = state.voter_count;

    const html = `
            <div class="fade-up">
                <div class="hero-section">
                    <div class="hero-eyebrow">RSA Blind Signature Protocol</div>
                    <h1 class="hero-title">Secure <span class="c">Blind</span> <span class="g">Signature</span> <span class="p">Voting</span></h1>
                    <p class="hero-desc">A purely cryptographic voting system implementing RSA blind signatures to completely sever the link between voter identity and ballot content.</p>
                </div>

                <div class="feature-cards">
                    <div class="feature-card" style="--card-accent:var(--cyan)" id="fc-admin">
                        <div class="feature-card-icon" style="background:rgba(0,229,200,0.1)">
                            <svg width="22" height="22" fill="none" stroke="var(--cyan)" viewBox="0 0 24 24" stroke-width="1.8">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                            </svg>
                        </div>
                        <h3>Administrator</h3>
                        <p>Manage election lifecycle, generate keys, and issue blind signatures.</p>
                        <a class="feature-card-link" style="color:var(--cyan)" href="#">Enter Panel <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg></a>
                    </div>
                    <div class="feature-card" style="--card-accent:var(--green)" id="fc-vote">
                        <div class="feature-card-icon" style="background:rgba(0,229,160,0.1)">
                            <svg width="22" height="22" fill="none" stroke="var(--green)" viewBox="0 0 24 24" stroke-width="1.8">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
                            </svg>
                        </div>
                        <h3>Voter Portal</h3>
                        <p>Blind and encrypt your ballot, and submit it anonymously.</p>
                        <a class="feature-card-link" style="color:var(--green)" href="#">Cast Ballot <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg></a>
                    </div>
                    <div class="feature-card" style="--card-accent:var(--purple)" id="fc-results">
                        <div class="feature-card-icon" style="background:rgba(155,109,255,0.1)">
                            <svg width="22" height="22" fill="none" stroke="var(--purple)" viewBox="0 0 24 24" stroke-width="1.8">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                            </svg>
                        </div>
                        <h3>Tally &amp; Results</h3>
                        <p>View cryptographic proofs and election outcome once counting is complete.</p>
                        <a class="feature-card-link" style="color:var(--purple)" href="#">View Data <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg></a>
                    </div>
                </div>

                <div class="protocol-status">
                    <div class="protocol-status-title">
                        <svg width="18" height="18" fill="none" stroke="var(--cyan)" viewBox="0 0 24 24" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                        </svg>
                        Protocol Status
                    </div>
                    <div class="status-grid">
                        <div class="status-tile">
                            <div class="status-tile-val" style="color:var(--cyan)">${vc}</div>
                            <div class="status-tile-label">Eligible Voters</div>
                        </div>
                        <div class="status-tile">
                            <div class="status-tile-val" style="color:var(--green)" id="home-cast">0</div>
                            <div class="status-tile-label">Ballots Cast</div>
                        </div>
                        <div class="status-tile">
                            <div class="status-tile-val" style="color:${
                              s === "VOTING"
                                ? "var(--cyan)"
                                : s === "COUNTED"
                                ? "var(--green)"
                                : "var(--amber)"
                            };font-size:1.1rem">${s}</div>
                            <div class="status-tile-label">System State</div>
                        </div>
                        <div class="status-tile">
                            <div class="status-tile-val" style="color:var(--purple);font-size:1rem">RSA-2048</div>
                            <div class="status-tile-label">Security</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

    document.getElementById("page-content").innerHTML = html;
  },

  // Attach event listeners
  attachEventListeners: () => {
    document.getElementById("fc-admin")?.addEventListener("click", () => {
      window.app.navigateTo("admin");
    });

    document.getElementById("fc-vote")?.addEventListener("click", () => {
      window.app.navigateTo("vote");
    });

    document.getElementById("fc-results")?.addEventListener("click", () => {
      window.app.navigateTo("results");
    });
  },
};
