export type AuditExportOptions = {
  title: string;
  caseId: string;
  includeLogo: boolean;
};

const escapeHtml = (value: string) => value.replace(/[&<>'"]/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
}[char]!));

export function buildAuditHeader(options: AuditExportOptions, logo: string) {
  const title = options.title.trim() || 'Linux AiO – Performance Report';
  const caseId = options.caseId.trim();
  return `<header>${options.includeLogo && logo ? `<img src="${escapeHtml(logo)}" alt="Linux AiO" />` : ''}<div><h1>${escapeHtml(title)}</h1><p class="subtitle">Local audit export — raw output and process details are intentionally excluded.</p>${caseId ? `<p class="case-id"><b>Ticket / Support case:</b> ${escapeHtml(caseId)}</p>` : ''}</div></header>`;
}
