import React from 'react';
import './FilterBar.css';

function FilterBar({ filters, onFilterChange }) {
  const handleSourceChange = (e) => {
    const value = e.target.value === '' ? null : e.target.value;
    onFilterChange({ ...filters, source: value });
  };

  const handleConfidenceChange = (e) => {
    const value = e.target.value === '' ? null : parseFloat(e.target.value);
    onFilterChange({ ...filters, minConfidence: value });
  };

  const handleSortChange = (e) => {
    onFilterChange({ ...filters, sort: e.target.value });
  };

  const handleSearchChange = (e) => {
    const value = e.target.value === '' ? null : e.target.value;
    onFilterChange({ ...filters, search: value });
  };

  const handleReset = () => {
    onFilterChange({
      source: null,
      minConfidence: null,
      sort: 'desc',
      search: null
    });
  };

  return (
    <div className="filter-bar">
      <div className="filter-group search-group">
        <label htmlFor="search">Search</label>
        <input
          type="text"
          id="search"
          placeholder="Search decisions, reasoning, outcomes..."
          value={filters.search || ''}
          onChange={handleSearchChange}
          className="search-input"
        />
      </div>

      <div className="filter-group">
        <label htmlFor="source">Source</label>
        <select 
          id="source"
          value={filters.source || ''} 
          onChange={handleSourceChange}
        >
          <option value="">All sources</option>
          <option value="rule">Rule-based</option>
          <option value="llm">LLM</option>
          <option value="hybrid">Hybrid</option>
          <option value="manual">Manual</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="confidence">Min Confidence</label>
        <select 
          id="confidence"
          value={filters.minConfidence || ''} 
          onChange={handleConfidenceChange}
        >
          <option value="">Any confidence</option>
          <option value="0.9">90%+ (High)</option>
          <option value="0.7">70%+ (Medium)</option>
          <option value="0.5">50%+ (Low)</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="sort">Sort by</label>
        <select 
          id="sort"
          value={filters.sort} 
          onChange={handleSortChange}
        >
          <option value="desc">Newest first</option>
          <option value="asc">Oldest first</option>
        </select>
      </div>

      <button className="reset-button" onClick={handleReset}>
        Reset Filters
      </button>
    </div>
  );
}

export default FilterBar;
