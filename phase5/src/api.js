/**
 * Client for Phase 4 recommendations API.
 * Testable: buildRequestBody, parseResponse, fetchRecommendations.
 */

const defaultBaseUrl = import.meta.env?.VITE_API_URL ?? '';

function apiUrl(path, baseUrl = defaultBaseUrl) {
  return baseUrl ? `${baseUrl.replace(/\/$/, '')}${path}` : `/api${path}`;
}

/**
 * Fetch unique locations for dropdown.
 */
export async function fetchLocations(baseUrl = defaultBaseUrl) {
  const res = await fetch(apiUrl('/locations', baseUrl));
  if (!res.ok) throw new Error('Failed to load locations');
  const data = await res.json();
  return Array.isArray(data.locations) ? data.locations : [];
}

/**
 * Fetch unique cuisines for dropdown.
 */
export async function fetchCuisines(baseUrl = defaultBaseUrl) {
  const res = await fetch(apiUrl('/cuisines', baseUrl));
  if (!res.ok) throw new Error('Failed to load cuisines');
  const data = await res.json();
  return Array.isArray(data.cuisines) ? data.cuisines : [];
}

/**
 * Build request body for POST /recommendations.
 * @param {{ place: string, rating: number, price?: number, cuisine?: string }} params
 * @returns {{ place: string, rating: number, price?: number, cuisine?: string }}
 */
export function buildRequestBody({ place, rating, price, cuisine }) {
  const body = {
    place: String(place ?? '').trim(),
    rating: Number(rating),
  };
  if (price != null && price !== '') {
    const p = Number(price);
    if (!Number.isNaN(p) && p >= 0) body.price = p;
  }
  if (cuisine != null && String(cuisine).trim() !== '') {
    body.cuisine = String(cuisine).trim();
  }
  return body;
}

/**
 * Parse API response into a consistent shape.
 * @param {{ recommendations?: Array, raw_response?: string, summary?: string, candidates_count?: number }} data
 */
export function parseResponse(data) {
  if (!data || typeof data !== 'object') {
    return { recommendations: [], raw_response: '', summary: '', candidates_count: 0 };
  }
  const list = Array.isArray(data.recommendations) ? data.recommendations : [];
  return {
    recommendations: list.map((r) => ({
      name: r?.name ?? 'Unknown',
      reason: r?.reason ?? '',
      rating: r?.rating,
      cuisine: r?.cuisine ?? '',
      price: r?.price,
      address: r?.address ?? '',
    })),
    raw_response: typeof data.raw_response === 'string' ? data.raw_response : '',
    summary: typeof data.summary === 'string' ? data.summary : '',
    candidates_count: typeof data.candidates_count === 'number' ? data.candidates_count : 0,
  };
}

/**
 * Fetch recommendations from the backend.
 * @param {{ place: string, rating: number, price?: number, cuisine?: string }} params
 * @param {string} baseUrl - API base URL (e.g. http://localhost:8000 or '' for same-origin /api)
 * @returns {Promise<{ recommendations: Array<{ name: string, reason: string }>, raw_response: string, candidates_count: number }>}
 */
export async function fetchRecommendations(params, baseUrl = defaultBaseUrl) {
  const body = buildRequestBody(params);
  const url = apiUrl('/recommendations', baseUrl);
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  const data = await res.json();
  return parseResponse(data);
}
