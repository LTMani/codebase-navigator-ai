"""
Technical Debt Calculator
Calculates technical debt principal in hours and financial cost using SQALE methodology.
"""

from typing import Dict, Any

class TechnicalDebtCalculator:
    HOURLY_DEV_RATE = 85.0  # Enterprise blended developer rate USD/hr

    @classmethod
    def estimate_file_debt(cls, complexity: int, duplication_pct: float, code_smell_count: int) -> Dict[str, Any]:
        # SQALE Debt hours model
        complexity_debt_hours = max(0.0, (complexity - 15) * 1.5)
        duplication_debt_hours = (duplication_pct / 100.0) * 8.0
        smell_debt_hours = code_smell_count * 0.5

        total_hours = round(complexity_debt_hours + duplication_debt_hours + smell_debt_hours, 2)
        total_cost_usd = round(total_hours * cls.HOURLY_DEV_RATE, 2)

        rating = "A"
        if total_hours > 40.0:
            rating = "E"
        elif total_hours > 20.0:
            rating = "D"
        elif total_hours > 10.0:
            rating = "C"
        elif total_hours > 4.0:
            rating = "B"

        return {
            "debt_hours": total_hours,
            "financial_cost_usd": total_cost_usd,
            "sqale_rating": rating,
            "breakdown": {
                "complexity_hours": round(complexity_debt_hours, 2),
                "duplication_hours": round(duplication_debt_hours, 2),
                "smell_hours": round(smell_debt_hours, 2)
            }
        }
