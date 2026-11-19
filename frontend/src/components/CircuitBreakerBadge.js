import React from 'react';
export default function CircuitBreakerBadge({ state }) { return <span className={`badge-${state.toLowerCase()}`}>{state}</span>; }