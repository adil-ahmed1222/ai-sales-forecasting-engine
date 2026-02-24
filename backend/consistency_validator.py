"""Consistency validator to ensure alignment between signals and messaging."""
from typing import Dict, Any


def validate_and_adjust(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure forecast direction, risk and insight are coherent.

    If contradictions are found, add an `explanation` field and adjust insight tone.
    """
    # Copy to avoid mutating caller's data
    out = dict(payload)
    risk = out.get('risk_label')
    volatility = out.get('volatility_percent')
    preds = out.get('predictions', [])
    last = out.get('last_actual')

    # Forecast direction
    direction = None
    if preds and last is not None:
        avg = sum(preds) / len(preds)
        pct = (avg - last) / last if last != 0 else 0.0
        direction = 'up' if pct > 0 else ('down' if pct < 0 else 'flat')
        out['forecast_direction_pct'] = pct

    explanation = []
    # If forecast up but risk high, flag instability
    if direction == 'up' and risk == 'High':
        explanation.append('Forecast projects growth but composite risk is High — investigate instability in revenue drivers.')

    # If volatility very high but forecast predicts smooth growth, warn
    if volatility is not None and volatility > 40 and direction == 'up':
        explanation.append('High volatility (>40%) reduces confidence in upward forecast; results may be sensitive to recent noise.')

    # Attach explanation if any
    if explanation:
        out['consistency_explanation'] = ' '.join(explanation)

    return out
