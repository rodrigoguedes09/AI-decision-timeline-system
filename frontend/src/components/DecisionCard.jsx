import React from 'react';
import './DecisionCard.css';

function DecisionCard({ decision, onClick, index }) {
  const getSourceIcon = (source) => {
    const icons = {
      rule: 'RULE',
      llm: 'AI',
      hybrid: 'HYBRID',
      manual: 'MANUAL'
    };
    return icons[source] || 'OTHER';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'high';
    if (confidence >= 0.7) return 'medium';
    return 'low';
  };

  const getDecisionColor = (decision) => {
    const text = decision.toLowerCase();
    if (text.includes('approve') || text.includes('accept')) return 'approve';
    if (text.includes('reject') || text.includes('deny')) return 'reject';
    if (text.includes('escalate') || text.includes('review')) return 'warning';
    return 'neutral';
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  return (
    <div 
      className={`decision-card decision-${getDecisionColor(decision.decision)}`}
      onClick={onClick}
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      <div className="card-header">
        <div className="card-title">
          <span className="source-icon">{getSourceIcon(decision.source)}</span>
          <h3>{decision.decision}</h3>
        </div>
        <span className="timestamp">{formatTime(decision.timestamp)}</span>
      </div>

      <div className="card-body">
        <div className="confidence-bar">
          <div className="confidence-label">
            <span>Confidence</span>
            <span className={`confidence-value confidence-${getConfidenceColor(decision.confidence)}`}>
              {(decision.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="confidence-track">
            <div 
              className={`confidence-fill confidence-${getConfidenceColor(decision.confidence)}`}
              style={{ width: `${decision.confidence * 100}%` }}
            ></div>
          </div>
        </div>

        {decision.tags && decision.tags.length > 0 && (
          <div className="tags">
            {decision.tags.map((tag, i) => (
              <span key={i} className="tag">{tag}</span>
            ))}
          </div>
        )}

        {decision.outcome && (
          <div className="outcome">
            <strong>Outcome:</strong> {decision.outcome}
          </div>
        )}

        <div className="card-footer">
          <span className="step-count">
            {decision.step_count} {decision.step_count === 1 ? 'step' : 'steps'}
          </span>
          <button className="replay-button">
            Replay
          </button>
        </div>
      </div>
    </div>
  );
}

export default DecisionCard;
