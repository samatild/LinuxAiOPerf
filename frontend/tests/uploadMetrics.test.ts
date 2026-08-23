import { describe, expect, it } from 'vitest';
import { uploadMetrics } from '../src/components/upload/uploadMetrics';

describe('uploadMetrics', () => {
  it('calculates percent, transfer speed, and ETA from upload progress', () => {
    expect(uploadMetrics(50_000_000, 200_000_000, 1_000, 11_000)).toEqual({
      percent: 25,
      bytesPerSecond: 5_000_000,
      etaSeconds: 30,
    });
  });

  it('does not claim an ETA before time has elapsed', () => {
    expect(uploadMetrics(0, 200_000_000, 1_000, 1_000)).toEqual({
      percent: 0,
      bytesPerSecond: 0,
      etaSeconds: null,
    });
  });
});
