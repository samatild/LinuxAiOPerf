import { describe, expect, it } from 'vitest';
import { buildAuditHeader } from '../src/components/report/auditExportOptions';

describe('buildAuditHeader', () => {
  it('uses a custom title and displays a case identifier', () => {
    const html = buildAuditHeader({ title: 'Customer Performance Audit', caseId: 'SUP-1042', includeLogo: false }, 'https://example.test/logo.png');

    expect(html).toContain('Customer Performance Audit');
    expect(html).toContain('SUP-1042');
    expect(html).not.toContain('<img');
  });
});
