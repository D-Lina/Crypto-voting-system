// Results Page Module
const ResultsPage = {
  gradients: [
    "#ff4060",
    "#ff6040",
    "#ff9020",
    "#f5c300",
    "#c4d900",
    "#00d9a0",
    "#00c8b0",
    "#00b8d9",
    "#0090ff",
    "#7060ff",
    "#c050ff",
  ],
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

  // Initialize results page
  init: async () => {
    await ResultsPage.render();
  },

  // Render results page
  render: async () => {
    const container = document.getElementById("page-content");
    container.innerHTML = `
            <div class="fade-up">
                <div class="page-title">Election Results</div>
                <div class="page-sub" style="margin-bottom:28px">Cryptographically verified outcome of the voting session.</div>
                <div id="results-body">
                    <div class="skeleton pulse" style="height:120px;border-radius:14px;margin-bottom:20px"></div>
                    <div class="skeleton pulse" style="height:300px;border-radius:14px"></div>
                </div>
            </div>
        `;

    await ResultsPage.loadResults();
  },

  // Load results from API
  loadResults: async () => {
    try {
      const results = await API.getResults();

      if (results.state !== "COUNTED") {
        throw new Error(`Results not available. State: ${results.state}`);
      }

      const tally = results.tally || [];
      const total = results.total || 0;
      const valid = results.valid || 0;
      const invalid = results.invalid || 0;
      const avg = valid
        ? (tally.reduce((sum, t) => sum + t.vote * t.count, 0) / valid).toFixed(
            2
          )
        : "N/A";
      const maxCount = Math.max(...tally.map((t) => t.count), 1);

      // Create bars
      const bars = tally
        .sort((a, b) => a.vote - b.vote)
        .map((t) => {
          const percentage = ((t.count / maxCount) * 100).toFixed(1);
          return `
                        <div class="bar-row">
                            <div class="bar-x-label">${t.vote}</div>
                            <div class="bar-track">
                                <div class="bar-fill" style="width:0%;background:${
                                  ResultsPage.gradients[t.vote]
                                }" data-width="${percentage}%"></div>
                            </div>
                            <div class="bar-count">${t.count}</div>
                        </div>
                    `;
        })
        .join("");

      // Create audit table rows
      const auditRows =
        (results.ballots || [])
          .map(
            (b) => `
                    <tr>
                        <td>${Utils.truncate(b.n2, 10)}…</td>
                        <td style="color:var(--text)">${b.vote ?? "?"}</td>
                        <td>${
                          b.sig_valid
                            ? '<span class="badge badge-green">✓ VALID</span>'
                            : '<span class="badge badge-red">✗ INVALID</span>'
                        }</td>
                        <td>${
                          b.n2_valid
                            ? '<span class="badge badge-green">✓</span>'
                            : '<span class="badge badge-red">✗</span>'
                        }</td>
                        <td>${b.status || "—"}</td>
                    </tr>
                `
          )
          .join("") ||
        `
                    <tr>
                        <td colspan="5" style="text-align:center;color:var(--text-muted);padding:24px">No ballots found in the ballot box.</td>
                    </tr>
                `;

      const resultsBody = document.getElementById("results-body");
      resultsBody.innerHTML = `
                <div class="results-stats">
                    <div class="r-stat">
                        <div class="r-stat-label">Total Ballots</div>
                        <div class="r-stat-val">${total}</div>
                    </div>
                    <div class="r-stat">
                        <div class="r-stat-label">Valid Votes</div>
                        <div class="r-stat-val" style="color:var(--green)">${valid}</div>
                    </div>
                    <div class="r-stat">
                        <div class="r-stat-label">Invalid/Rejected</div>
                        <div class="r-stat-val" style="color:var(--red)">${invalid}</div>
                    </div>
                    <div class="r-stat">
                        <div class="r-stat-label">Average Score</div>
                        <div class="r-stat-val" style="color:var(--cyan)">${avg}</div>
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Score Distribution</div>
                    <div class="bar-chart">${bars}</div>
                </div>
                <div class="audit-card">
                    <div class="audit-header">
                        <svg width="16" height="16" fill="none" stroke="var(--cyan)" viewBox="0 0 24 24" stroke-width="1.8">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6-4h12m-6 0v-4"/>
                        </svg>
                        Decrypted Ballot Audit
                    </div>
                    <div style="overflow-x:auto">
                        <table class="audit-table">
                            <thead>
                                <tr>
                                    <th>N2 Code (Anonymity)</th>
                                    <th>Score Cast</th>
                                    <th>Blind Sig. Valid?</th>
                                    <th>N2 Valid?</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>${auditRows}</tbody>
                        </table>
                    </div>
                </div>
            `;

      // Animate bars after render
      setTimeout(() => {
        document.querySelectorAll("[data-width]").forEach((el) => {
          el.style.width = el.getAttribute("data-width");
        });
      }, 100);
    } catch (error) {
      const resultsBody = document.getElementById("results-body");
      resultsBody.innerHTML = `
                <div class="alert alert-amber">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                    </svg>
                    <div><strong>Cannot load results</strong><br><span style="font-family:var(--mono);font-size:0.78rem">${error.message}</span></div>
                </div>
            `;
    }
  },
};
