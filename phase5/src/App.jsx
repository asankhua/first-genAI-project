import { useState, useEffect } from 'react';
import { fetchRecommendations, fetchLocations, fetchCuisines } from './api';

const RATING_OPTIONS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0];

const PRICE_RANGES = [
  { value: '', label: 'Select price range...' },
  { value: '300', label: 'Up to ₹300' },
  { value: '600', label: '₹300 - ₹600' },
  { value: '900', label: '₹600 - ₹900' },
  { value: '1200', label: '₹900 - ₹1200' },
  { value: '1500', label: '₹1200 - ₹1500' },
  { value: '2000', label: '₹1500 - ₹2000' },
  { value: '3000', label: '₹2000+' },
];

export default function App() {
  const [place, setPlace] = useState('');
  const [rating, setRating] = useState(3.0);
  const [price, setPrice] = useState('');
  const [cuisine, setCuisine] = useState('');
  const [locations, setLocations] = useState([]);
  const [cuisines, setCuisines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingOptions, setLoadingOptions] = useState(true);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    Promise.all([fetchLocations(), fetchCuisines()])
      .then(([locs, cuis]) => {
        setLocations(locs);
        setCuisines(cuis);
        if (locs.length > 0 && !place) setPlace(locs[0]);
      })
      .catch(() => setLocations([]))
      .finally(() => setLoadingOptions(false));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setResult(null);
    const placeTrim = place.trim();
    if (!placeTrim) {
      setError('Please select a locality.');
      return;
    }
    setLoading(true);
    try {
      const data = await fetchRecommendations({
        place: placeTrim,
        rating: Number(rating),
        price: price === '' ? undefined : Number(price),
        cuisine: cuisine.trim() || undefined,
      });
      setResult(data);
    } catch (err) {
      const msg = err.message || 'Failed to load recommendations.';
      setError(msg === 'Failed to fetch' || msg.includes('network')
        ? 'Could not connect to the server. Make sure the backend is running on port 8000.'
        : msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="zomato-app">
      <header className="app-header">
        <h1 className="app-title">
          Zomato AI <span className="title-accent">Recommender</span>
        </h1>
        <p className="app-subtitle">Helping you find the best places to eat in Bangalore city</p>
        <div className="app-stats">
          <span className="stat-item">
            <span className="stat-icon stat-icon-pin">📍</span>
            <strong>{locations.length}</strong> Localities
          </span>
          <span className="stat-sep">|</span>
          <span className="stat-item">
            <span className="stat-icon stat-icon-chef">👨‍🍳</span>
            <strong>{cuisines.length}</strong> Cuisines
          </span>
        </div>
      </header>

      <div className="form-section">
        <form onSubmit={handleSubmit} className="recommendation-form">
          <div className="form-row">
            <div className="form-col">
              <div className="field-group">
                <label htmlFor="place" className="field-label required">
                  <span className="field-icon">📍</span> Select locality
                </label>
                {locations.length > 0 ? (
                  <select
                    id="place"
                    value={place}
                    onChange={(e) => setPlace(e.target.value)}
                    disabled={loading || loadingOptions}
                    className="field-input field-select"
                  >
                    <option value="">Select locality...</option>
                    {locations.map((loc) => (
                      <option key={loc} value={loc}>{loc}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    id="place"
                    type="text"
                    value={place}
                    onChange={(e) => setPlace(e.target.value)}
                    placeholder="Select locality..."
                    disabled={loading}
                    className="field-input"
                  />
                )}
              </div>
              <div className="field-group">
                <label htmlFor="cuisine" className="field-label">
                  <span className="field-icon">👨‍🍳</span> Cuisines (Multi-select)
                </label>
                <select
                  id="cuisine"
                  value={cuisine}
                  onChange={(e) => setCuisine(e.target.value)}
                  disabled={loading}
                  className="field-input field-select"
                >
                  <option value="">Select cuisines...</option>
                  {cuisines.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-col">
              <div className="field-group">
                <label htmlFor="price" className="field-label required">
                  <span className="field-icon">💰</span> Price Range
                </label>
                <select
                  id="price"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  disabled={loading}
                  className="field-input field-select"
                >
                  {PRICE_RANGES.map((opt) => (
                    <option key={opt.value || 'any'} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div className="field-group">
                <label htmlFor="rating" className="field-label">
                  <span className="field-icon">⭐</span> Min Rating
                </label>
                <select
                  id="rating"
                  value={rating}
                  onChange={(e) => setRating(Number(e.target.value))}
                  disabled={loading}
                  className="field-input field-select"
                >
                  {RATING_OPTIONS.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          <button type="submit" className="btn-recommend" disabled={loading || loadingOptions}>
            {loading ? 'Analyzing...' : <>Get Recommendations ✨</>}
          </button>
        </form>
      </div>

      {loading && (
        <div className="results-section">
          <div className="loading-state">
            <div className="spinner" />
            <p>AI is analyzing restaurants for you...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="results-section error-section">
          <p className="error-msg">{error}</p>
        </div>
      )}

      {result && !loading && (
        <div className="results-section">
          {result.recommendations.length === 0 ? (
            <div className="empty-state">
              <p className="empty-msg">No recommendations found for your criteria.</p>
              <p className="empty-hint">Try lowering the minimum rating (most restaurants are below 5.0) or relaxing the price range.</p>
            </div>
          ) : (
            <>
              {result.summary && (
                <div className="results-summary">
                  {result.summary}
                </div>
              )}
              <div className="rec-tiles">
                {result.recommendations.map((rec, i) => (
                  <div key={i} className="rec-tile">
                    <div className="rec-tile-header">
                      <h3 className="rec-tile-name">{rec.name}</h3>
                      {rec.rating != null && (
                        <span className="rec-tile-rating">⭐ {rec.rating}</span>
                      )}
                    </div>
                    {rec.cuisine && (
                      <div className="rec-tile-row">
                        <span className="rec-tile-icon">🍴</span>
                        {rec.cuisine}
                      </div>
                    )}
                    {rec.price != null && rec.price > 0 && (
                      <div className="rec-tile-row">
                        <span className="rec-tile-icon">💰</span>
                        Avg. ₹{rec.price} for two
                      </div>
                    )}
                    {rec.address && (
                      <div className="rec-tile-row">
                        <span className="rec-tile-icon">📍</span>
                        {rec.address}
                      </div>
                    )}
                    <div className="rec-tile-why">
                      <strong>Why you'll like it:</strong>
                      <p>{rec.reason}</p>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      <footer className="app-footer">POWERED BY GROQ AI</footer>
    </div>
  );
}
