import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';

function mockFetchByUrl() {
  globalThis.fetch.mockImplementation((url) => {
    if (url.includes('/locations'))
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ locations: ['Banashankari', 'JP Nagar'] }) });
    if (url.includes('/cuisines'))
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ cuisines: ['North Indian', 'Chinese'] }) });
    if (url.includes('/recommendations'))
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ recommendations: [], raw_response: '', candidates_count: 0 }) });
    return Promise.reject(new Error('Unexpected URL'));
  });
}

function mockFetchRecommendations(data) {
  globalThis.fetch.mockImplementation((url) => {
    if (url.includes('/locations'))
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ locations: ['Banashankari'] }) });
    if (url.includes('/cuisines'))
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ cuisines: [] }) });
    if (url.includes('/recommendations'))
      return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
    return Promise.reject(new Error('Unexpected URL'));
  });
}

describe('App', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('renders form with locality and rating fields', async () => {
    mockFetchByUrl();
    render(<App />);
    await screen.findByLabelText(/select locality/i, {}, { timeout: 3000 });
    expect(screen.getByLabelText(/min rating/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /get recommendations/i })).toBeInTheDocument();
  });

  it('shows error when locality is empty on submit', async () => {
    globalThis.fetch.mockImplementation((url) => {
      if (url.includes('/locations')) return Promise.resolve({ ok: true, json: () => Promise.resolve({ locations: [] }) });
      if (url.includes('/cuisines')) return Promise.resolve({ ok: true, json: () => Promise.resolve({ cuisines: [] }) });
      return Promise.reject(new Error('Unexpected URL'));
    });
    render(<App />);
    const locationField = await screen.findByLabelText(/select locality/i, {}, { timeout: 3000 });
    expect(locationField.value).toBe('');
    fireEvent.click(screen.getByRole('button', { name: /get recommendations/i }));
    await waitFor(() => expect(screen.getByText(/please select a locality/i)).toBeInTheDocument());
  });

  it('calls API and displays recommendations on success', async () => {
    mockFetchRecommendations({ recommendations: [{ name: 'Restaurant A', reason: 'Great rating.' }], raw_response: 'OK', candidates_count: 5 });
    render(<App />);
    await screen.findByLabelText(/select locality/i, {}, { timeout: 3000 });
    fireEvent.click(screen.getByRole('button', { name: /get recommendations/i }));
    await waitFor(() => expect(screen.getByText('Restaurant A')).toBeInTheDocument());
    expect(screen.getByText('Great rating.')).toBeInTheDocument();
  });

  it('shows empty state when no recommendations returned', async () => {
    mockFetchRecommendations({ recommendations: [], raw_response: 'No matches.', candidates_count: 0 });
    render(<App />);
    await screen.findByLabelText(/select locality/i, {}, { timeout: 3000 });
    fireEvent.click(screen.getByRole('button', { name: /get recommendations/i }));
    expect(await screen.findByText(/no recommendations found/i, {}, { timeout: 3000 })).toBeInTheDocument();
  });
});
