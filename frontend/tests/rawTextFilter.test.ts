import { describe, expect, it } from 'vitest';
import { filterRawText } from '../src/components/ui/rawTextFilter';

describe('filterRawText', () => {
  it('keeps matching lines case-insensitively while preserving their order', () => {
    expect(filterRawText('sda ext4\ndm-0 xfs\nsdb ext4', 'DM-0')).toBe('dm-0 xfs');
  });

  it('returns the full text when the query is empty', () => {
    expect(filterRawText('one\ntwo', '')).toBe('one\ntwo');
  });
});
