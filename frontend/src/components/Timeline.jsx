import React from 'react';
import DecisionCard from './DecisionCard';
import './Timeline.css';

function Timeline({ decisions, onDecisionClick }) {
  if (!decisions || decisions.length === 0) {
    return (
      <div className="timeline-empty">
        <div className="empty-state">
          <h2>No Decisions Yet</h2>
          <p>Create some decisions or load demo data to see them here.</p>
          <code>python scripts/load_demo_data.py</code>
        </div>
      </div>
    );
  }

  return (
    <div className="timeline-container">
      <div className="timeline-header">
        <h2>Decision Timeline</h2>
        <span className="decision-count">{decisions.length} decisions</span>
      </div>
      
      <div className="timeline">
        <div className="timeline-line"></div>
        
        {decisions.map((decision, index) => (
          <div key={decision.decision_id} className="timeline-item">
            <div className="timeline-marker"></div>
            <DecisionCard 
              decision={decision} 
              onClick={() => onDecisionClick(decision)}
              index={index}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export default Timeline;
