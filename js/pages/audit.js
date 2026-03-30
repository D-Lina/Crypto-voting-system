// Audit Page Module
const AuditPage = {
  // Initialize audit page
  init: async () => {
    await AuditPage.render();
  },

  // Render audit page
  render: async () => {
    const container = document.getElementById("page-content");
    container.innerHTML = `
            <div class="fade-up">
                <div class="page-title">Audit Log</div>
                <div class="page-sub" style="margin-bottom:28px">Cryptographic hash chain of all system events.</div>
                <div class="audit-card">
                    <div class="audit-header">
                        <svg width="16" height="16" fill="none" stroke="var(--cyan)" viewBox="0 0 24 24" stroke-width="1.8">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                        System Audit Trail
                    </div>
                    <div id="audit-body" style="max-height:500px;overflow-y:auto">
                        <div class="skeleton pulse" style="height:200px;margin:16px"></div>
                    </div>
                </div>
            </div>
        `;

    await AuditPage.loadAudit();
  },

  // Load audit trail from API
  loadAudit: async () => {
    try {
      const data = await API.getAuditTrail();
      const items = data.trail || [];

      const auditBody = document.getElementById("audit-body");

      if (items.length === 0) {
        auditBody.innerHTML = `
                    <div style="color:var(--text-muted);font-family:var(--mono);font-size:0.78rem;padding:24px;text-align:center">
                        No audit events recorded.
                    </div>
                `;
        return;
      }

      auditBody.innerHTML = `
                <table class="audit-table" style="width:100%">
                    <thead>
                        <tr>
                            <th>Hash</th>
                            <th>Action</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${items
                          .map(
                            (item) => `
                            <tr>
                                <td>${Utils.truncate(item.hash, 12)}…</td>
                                <td>${item.action || ""}</td>
                                <td>${Utils.formatDate(item.timestamp)}</td>
                            </tr>
                        `
                          )
                          .join("")}
                    </tbody>
                </table>
            `;
    } catch (error) {
      const auditBody = document.getElementById("audit-body");
      auditBody.innerHTML = `
                <div class="alert alert-amber" style="margin:16px">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                    </svg>
                    <div><strong>Cannot load audit trail</strong><br><span style="font-family:var(--mono);font-size:0.78rem">${error.message}</span></div>
                </div>
            `;
    }
  },
};
