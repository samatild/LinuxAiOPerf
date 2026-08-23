import { describe, expect, it } from 'vitest';
import { adjacentTimestamp } from '../src/components/report/process_details/timestampNavigation';

describe('adjacentTimestamp', () => {
  const timestamps = ['10:00:00', '10:01:00', '10:02:00'];

  it('returns the next timestamp without passing the final sample', () => {
    expect(adjacentTimestamp(timestamps, '10:01:00', 1)).toBe('10:02:00');
    expect(adjacentTimestamp(timestamps, '10:02:00', 1)).toBe('10:02:00');
  });

  it('returns the previous timestamp without passing the first sample', () => {
    expect(adjacentTimestamp(timestamps, '10:01:00', -1)).toBe('10:00:00');
    expect(adjacentTimestamp(timestamps, '10:00:00', -1)).toBe('10:00:00');
  });
});
