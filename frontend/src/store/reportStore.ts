import type { ReportData } from '../types/report';

// Module-level store — no size limit, no serialization.
// Data lives for the browser session; cleared on page reload (user must re-upload).
let _data: ReportData | null = null;

export function setReportData(data: ReportData) { _data = data; }
export function getReportData(): ReportData | null { return _data; }
export function clearReportData() { _data = null; }
