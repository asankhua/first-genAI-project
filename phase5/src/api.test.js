import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { buildRequestBody, parseResponse, fetchRecommendations, fetchLocations, fetchCuisines } from './api';

describe('buildRequestBody', () => {
  it('includes place and rating', () => {
    expect(buildRequestBody({ place: 'Bangalore', rating: 4 })).toEqual({
      place: 'Bangalore',
      rating: 4,
    });
  });

  it('trims place and omits empty optional fields', () => {
    expect(buildRequestBody({ place: '  Delhi  ', rating: 3.5 })).toEqual({
      place: 'Delhi',
      rating: 3.5,
    });
  });

  it('includes price when provided and non-negative', () => {
    expect(buildRequestBody({ place: 'Mumbai', rating: 4, price: 1000 })).toEqual({
      place: 'Mumbai',
      rating: 4,
      price: 1000,
    });
  });

  it('includes cuisine when provided and non-empty', () => {
    expect(buildRequestBody({ place: 'Pune', rating: 4, cuisine: 'North Indian' })).toEqual({
      place: 'Pune',
      rating: 4,
      cuisine: 'North Indian',
    });
  });

  it('omits price when empty or invalid', () => {
    expect(buildRequestBody({ place: 'X', rating: 4, price: '' })).toEqual({ place: 'X', rating: 4 });
    expect(buildRequestBody({ place: 'X', rating: 4, price: -1 })).toEqual({ place: 'X', rating: 4 });
  });
});

describe('parseResponse', () => {
  it('returns empty structure for null or non-object', () => {
    expect(parseResponse(null)).toEqual({ recommendations: [], raw_response: '', summary: '', candidates_count: 0 });
    expect(parseResponse(undefined)).toEqual({ recommendations: [], raw_response: '', summary: '', candidates_count: 0 });
  });

  it('parses full API response', () => {
    const data = {
      recommendations: [{ name: 'R1', reason: 'Great food.' }, { name: 'R2', reason: 'Good value.' }],
      raw_response: 'Full text',
      summary: 'Intro text',
      candidates_count: 10,
    };
    expect(parseResponse(data)).toEqual({
      recommendations: [
        { name: 'R1', reason: 'Great food.', rating: undefined, cuisine: '', price: undefined, address: '' },
        { name: 'R2', reason: 'Good value.', rating: undefined, cuisine: '', price: undefined, address: '' },
      ],
      raw_response: 'Full text',
      summary: 'Intro text',
      candidates_count: 10,
    });
  });

  it('normalizes missing recommendation fields', () => {
    expect(parseResponse({ recommendations: [{ name: 'A' }, {}] })).toEqual({
      recommendations: [
        { name: 'A', reason: '', rating: undefined, cuisine: '', price: undefined, address: '' },
        { name: 'Unknown', reason: '', rating: undefined, cuisine: '', price: undefined, address: '' },
      ],
      raw_response: '',
      summary: '',
      candidates_count: 0,
    });
  });
});

describe('fetchRecommendations', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('POSTs to baseUrl/recommendations with JSON body', async () => {
    const mockRes = { ok: true, json: () => Promise.resolve({ recommendations: [], raw_response: '', candidates_count: 0 }) };
    globalThis.fetch.mockResolvedValue(mockRes);
    await fetchRecommendations({ place: 'City', rating: 4 }, 'http://localhost:8000');
    expect(globalThis.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/recommendations',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ place: 'City', rating: 4 }),
      })
    );
  });

  it('returns parsed response on success', async () => {
    const data = {
      recommendations: [{ name: 'Cafe A', reason: 'Good.' }],
      raw_response: 'OK',
      candidates_count: 1,
    };
    globalThis.fetch.mockResolvedValue({ ok: true, json: () => Promise.resolve(data) });
    const result = await fetchRecommendations({ place: 'X', rating: 4 }, 'http://api');
    expect(result).toEqual({
      recommendations: [{ name: 'Cafe A', reason: 'Good.', rating: undefined, cuisine: '', price: undefined, address: '' }],
      raw_response: 'OK',
      summary: '',
      candidates_count: 1,
    });
  });

  it('throws on non-ok response', async () => {
    globalThis.fetch.mockResolvedValue({ ok: false, status: 500, text: () => Promise.resolve('Server error') });
    await expect(fetchRecommendations({ place: 'X', rating: 4 }, 'http://api')).rejects.toThrow();
  });
});

describe('fetchLocations', () => {
  beforeEach(() => vi.stubGlobal('fetch', vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it('returns locations array', async () => {
    globalThis.fetch.mockResolvedValue({ ok: true, json: () => Promise.resolve({ locations: ['A', 'B'] }) });
    const out = await fetchLocations('http://api');
    expect(out).toEqual(['A', 'B']);
  });
});

describe('fetchCuisines', () => {
  beforeEach(() => vi.stubGlobal('fetch', vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it('returns cuisines array', async () => {
    globalThis.fetch.mockResolvedValue({ ok: true, json: () => Promise.resolve({ cuisines: ['North Indian'] }) });
    const out = await fetchCuisines('http://api');
    expect(out).toEqual(['North Indian']);
  });
});
