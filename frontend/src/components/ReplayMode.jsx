import React, { useState, useEffect } from 'react';
import { getDecision } from '../services/api';
import './ReplayMode.css';

function ReplayMode({ decision, onClose }) {
  const [fullDecision, setFullDecision] = useState(null);
  const [currentStep, setCurrentStep] = useState(-1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFullDecision();
  }, [decision.decision_id]);

  const loadFullDecision = async () => {
    try {
      const data = await getDecision(decision.decision_id);
      setFullDecision(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load decision:', err);
      setLoading(false);
    }
  };

  const handleStepClick = (index) => {
    setCurrentStep(index);
  };

  const getStepIcon = (stepType) => {
    const icons = {
      input: 'IN',
      reasoning: 'RS',
      decision: 'DC',
      action: 'AC',
      outcome: 'OUT'
    };
    return icons[stepType] || 'ST';
  };

  const getStepColor = (stepType) => {
    const colors = {
      input: 'var(--color-input)',
      reasoning: 'var(--color-reasoning)',
      decision: 'var(--color-decision-approve)',
      action: 'var(--color-action)',
      outcome: 'var(--color-outcome)'
    };
    return colors[stepType] || 'var(--color-outcome)';
  };

  if (loading) {
    return (
      <div className="replay-overlay">
        <div className="replay-modal">
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading decision...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!fullDecision) {
    return null;
  }

  return (
    <div className="replay-overlay" onClick={onClose}>
      <div className="replay-modal" onClick={(e) => e.stopPropagation()}>
        <div className="replay-header">
          <div>
            <h2>Replay Decision</h2>
            <p className="decision-id">{fullDecision.decision_id}</p>
          </div>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        <div className="replay-content">
          <div className="steps-list">
            {fullDecision.steps.map((step, index) => (
              <div
                key={index}
                className={`step-item ${index <= currentStep ? 'revealed' : 'hidden'} ${index === currentStep ? 'active' : ''}`}
                onClick={() => handleStepClick(index)}
                style={{
                  borderLeftColor: getStepColor(step.step_type),
                  animationDelay: `${index * 0.1}s`
                }}
              >
                <div className="step-header">
                  <span className="step-icon">{getStepIcon(step.step_type)}</span>
                  <span className="step-type">{step.step_type.toUpperCase()}</span>
                  <span className="step-number">#{index + 1}</span>
                </div>
                <div className="step-content">
                  {step.content}
                </div>
                {step.step_metadata && Object.keys(step.step_metadata).length > 0 && (
                  <div className="step-metadata">
                    <details>
                      <summary>View metadata</summary>
                      <pre>{JSON.stringify(step.step_metadata, null, 2)}</pre>
                    </details>
                  </div>
                )}
                <div className="step-timestamp">
                  {new Date(step.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>

          <div className="decision-summary">
            <h3>Decision Summary</h3>
            <div className="summary-item">
              <strong>Decision:</strong> {fullDecision.decision}
            </div>
            <div className="summary-item">
              <strong>Confidence:</strong> {(fullDecision.confidence * 100).toFixed(0)}%
            </div>
            <div className="summary-item">
              <strong>Source:</strong> {fullDecision.source}
            </div>
            {fullDecision.reasoning && (
              <div className="summary-item">
                <strong>Reasoning:</strong> {fullDecision.reasoning}
              </div>
            )}
            {fullDecision.outcome && (
              <div className="summary-item">
                <strong>Outcome:</strong> {fullDecision.outcome}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReplayMode;
