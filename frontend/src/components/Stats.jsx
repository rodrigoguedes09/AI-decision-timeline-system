import React from 'react';
import './Stats.css';

function Stats({ stats }) {
  if (!stats) return null;

  const { 
    total_decisions, 
    decisions_by_source, 
    average_confidence,
    low_confidence_count,
    low_confidence_percentage 
  } = stats;

  return (
    <div className="stats-container">
      <div className="stat-card">
        <div className="stat-icon">TOTAL</div>
        <div className="stat-content">
          <div className="stat-value">{total_decisions}</div>
          <div className="stat-label">Total Decisions</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon">AVG</div>
        <div className="stat-content">
          <div className="stat-value">{(average_confidence * 100).toFixed(1)}%</div>
          <div className="stat-label">Avg Confidence</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon">LOW</div>
        <div className="stat-content">
          <div className="stat-value">{low_confidence_count}</div>
          <div className="stat-label">Low Confidence ({low_confidence_percentage}%)</div>
        </div>
      </div>

      <div className="stat-card sources">
        <div className="stat-icon">SRC</div>
        <div className="stat-content">
          <div className="stat-label">By Source</div>
          <div className="source-breakdown">
            {Object.entries(decisions_by_source).map(([source, count]) => (
              <div key={source} className="source-item">
                <span className="source-name">{source}</span>
                <span className="source-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Stats;
