// Vote Page Module (continued)
const VotePage = {
  selectedVote: null,
  scoreLabels: [
    "Strongly Oppose",
    "Strongly Disagree",
    "Disagree",
    "Somewhat Disagree",
    "Slightly Against",
    "Neutral",
    "Slightly In Favor",
    "Somewhat Agree",
    "Agree",
    "Strongly Agree",
    "Fully Support",
  ],

  // Initialize vote page
  init: () => {
    VotePage.render();
    VotePage.attachEventListeners();
  },

  // Render vote page
  render: () => {
    const state = window.cachedState?.state || "IDLE";
    const container = document.getElementById("page-content");

    if (state !== "VOTING") {
      container.innerHTML = `
                <div class="vote-container fade-up">
                    <div class="page-title">Cast Your Ballot</div>
                    <div class="page-sub">Your identity (N1) is verified, but your ballot (N2 + Vote) remains completely anonymous.</div>
                    <div class="alert alert-amber">
                        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                        </svg>
                        <div><strong>Voting is not open.</strong><br><span style="font-family:var(--mono);font-size:0.78rem">Current state: ${state}</span></div>
                    </div>
                </div>
            `;
      return;
    }

    container.innerHTML = `
            <div class="vote-container fade-up">
                <div class="page-title">Cast Your Ballot</div>
                <div class="page-sub" style="margin-bottom:28px">Your identity (N1) is verified, but your ballot (N2 + Vote) remains completely anonymous.</div>
                <div class="vote-card">
                    <div style="padding-bottom:24px;border-bottom:1px solid var(--border);margin-bottom:24px">
                        <div class="vote-section-title">
                            <svg width="18" height="18" fill="none" stroke="var(--cyan)" viewBox="0 0 24 24" stroke-width="1.8">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            Authentication Codes
                        </div>
                        <div style="margin-bottom:14px">
                            <label>N1 Identity Code</label>
                            <input id="n1" placeholder="e.g. ALICE-N1-778"/>
                        </div>
                        <div>
                            <label>N2 Anonymity Code</label>
                            <input id="n2" placeholder="e.g. ALICE-N2-XYZ"/>
                        </div>
                    </div>
                    <div>
                        <div class="vote-section-title">
                            <svg width="18" height="18" fill="none" stroke="var(--green)" viewBox="0 0 24 24" stroke-width="1.8">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10"/>
                            </svg>
                            Select Score
                            <span style="font-size:0.72rem;font-weight:400;font-family:var(--mono);color:var(--text-muted)">Rate your choice from 0 to 10.</span>
                        </div>
                        <div class="score-grid" id="score-grid"></div>
                        <div id="score-preview" style="margin-top:10px;min-height:18px;font-size:0.75rem;font-family:var(--mono);color:var(--cyan)"></div>
                    </div>
                    <div id="vote-err" class="alert alert-red" style="display:none;margin-top:16px"></div>
                    <button class="submit-btn" id="submit-vote">
                        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                        </svg>
                        Blind, Sign &amp; Submit Ballot
                    </button>
                </div>
            </div>
        `;

    // Create score buttons
    const grid = document.getElementById("score-grid");
    for (let i = 0; i <= 10; i++) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = i;
      btn.className =
        "score-btn" + (VotePage.selectedVote === i ? " selected" : "");
      btn.onclick = () => {
        VotePage.selectedVote = i;
        VotePage.render();
      };
      grid.appendChild(btn);
    }

    if (VotePage.selectedVote !== null) {
      document.getElementById("score-preview").textContent = `${
        VotePage.selectedVote
      } = ${VotePage.scoreLabels[VotePage.selectedVote]}`;
    }
  },

  // Attach event listeners
  attachEventListeners: () => {
    const submitBtn = document.getElementById("submit-vote");
    if (!submitBtn) return;

    submitBtn.addEventListener("click", async () => {
      const n1 = document.getElementById("n1").value.trim();
      const n2 = document.getElementById("n2").value.trim();
      const err = document.getElementById("vote-err");

      if (!n1 || !n2 || VotePage.selectedVote === null) {
        err.textContent = "Please fill both codes and select a score.";
        err.style.display = "flex";
        return;
      }

      const btn = document.getElementById("submit-vote");
      btn.disabled = true;
      btn.textContent = "Processing cryptographic protocol...";

      try {
        await API.castVote({ n1, n2, vote: VotePage.selectedVote });

        document.querySelector(".vote-card").innerHTML = `
                    <div style="text-align:center;padding:40px 0" class="pop-in">
                        <div style="width:72px;height:72px;background:var(--green-dim);border:1px solid rgba(0,229,160,0.3);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 20px">
                            <svg width="32" height="32" fill="none" stroke="var(--green)" viewBox="0 0 24 24" stroke-width="2.5">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                            </svg>
                        </div>
                        <div style="font-size:1.6rem;font-weight:700;letter-spacing:-0.03em;margin-bottom:8px">Vote Recorded!</div>
                        <div style="color:var(--text-muted);font-size:0.82rem;font-family:var(--mono);margin-bottom:4px">Your vote has been anonymously registered via RSA blind signatures.</div>
                        <button class="btn btn-outline" style="margin-top:24px" id="back-home">← Back to Overview</button>
                    </div>
                `;

        document.getElementById("back-home")?.addEventListener("click", () => {
          window.app.navigateTo("home");
        });

        VotePage.selectedVote = null;
      } catch (error) {
        err.textContent = error.message;
        err.style.display = "flex";
        btn.disabled = false;
        btn.innerHTML = `
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                    </svg>
                    Blind, Sign & Submit Ballot
                `;
      }
    });
  },
};
