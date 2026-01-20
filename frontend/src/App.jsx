import React, { useState, useEffect } from 'react';
import Timeline from './components/Timeline';
import ReplayMode from './components/ReplayMode';
import FilterBar from './components/FilterBar';
import Stats from './components/Stats';
import { getDecisions, getStats, exportDecisionsCSV, exportDecisionsJSON } from './services/api';
import './App.css';

function App() {
  const [decisions, setDecisions] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedDecision, setSelectedDecision] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 50,
    offset: 0,
    hasMore: false
  });
  const [filters, setFilters] = useState({
    source: null,
    minConfidence: null,
    sort: 'desc',
    search: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [filters, pagination.offset]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [decisionsData, statsData] = await Promise.all([
        getDecisions({ ...filters, limit: pagination.limit, offset: pagination.offset }),
        getStats()
      ]);
      
      // Handle new API response format with pagination
      if (decisionsData.decisions) {
        setDecisions(decisionsData.decisions);
        setPagination(prev => ({
          ...prev,
          total: decisionsData.total,
          hasMore: decisionsData.has_more
        }));
      } else {
        // Fallback for old API format
        setDecisions(decisionsData);
      }
      
      setStats(statsData);
      setError(null);
    } catch (err) {
      setError('Failed to load data. Make sure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDecisionClick = (decision) => {
    setSelectedDecision(decision);
  };

  const handleCloseReplay = () => {
    setSelectedDecision(null);
  };

  const handleExportCSV = () => {
    exportDecisionsCSV(filters);
  };

  const handleExportJSON = () => {
    exportDecisionsJSON(filters);
  };

  const handleLoadMore = () => {
    setPagination(prev => ({
      ...prev,
      offset: prev.offset + prev.limit
    }));
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, offset: 0 })); // Reset pagination
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>AI Decision Timeline</h1>
          <p className="subtitle">Visual-first system for AI decision traceability</p>
        </div>
        <div className="header-actions">
          <button className="export-button" onClick={handleExportCSV} title="Export to CSV">
            Export CSV
          </button>
          <button className="export-button" onClick={handleExportJSON} title="Export to JSON">
            Export JSON
          </button>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <span>{error}</span>
          </div>
        )}

        {stats && <Stats stats={stats} />}

        <FilterBar filters={filters} onFilterChange={handleFilterChange} />

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading decisions...</p>
          </div>
        ) : (
          <>
            <Timeline 
              decisions={decisions} 
              onDecisionClick={handleDecisionClick}
            />
            
            {pagination.hasMore && (
              <div className="pagination-controls">
                <button className="load-more-button" onClick={handleLoadMore}>
                  Load More ({pagination.total - pagination.offset - decisions.length} remaining)
                </button>
              </div>
            )}
          </>
        )}

        {selectedDecision && (
          <ReplayMode 
            decision={selectedDecision} 
            onClose={handleCloseReplay}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>Built to make AI behavior understandable &bull; <a href="https://github.com/rodrigoguedes09/AI-decision-timeline-system" target="_blank" rel="noopener noreferrer">GitHub</a></p>
      </footer>
    </div>
  );
}

export default App;
