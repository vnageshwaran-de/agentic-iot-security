"""Light-weight metrics for the evaluation harness."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ClassificationReport:
    total: int
    correct: int
    by_family_total: dict[str, int]
    by_family_correct: dict[str, int]

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    def per_family_recall(self) -> dict[str, float]:
        return {
            fam: (self.by_family_correct.get(fam, 0) / n if n else 0.0)
            for fam, n in self.by_family_total.items()
        }


def update(report: ClassificationReport, predicted_family: str, gold_family: str) -> None:
    report.total += 1
    if predicted_family == gold_family:
        report.correct += 1
    report.by_family_total[gold_family] = report.by_family_total.get(gold_family, 0) + 1
    if predicted_family == gold_family:
        report.by_family_correct[gold_family] = report.by_family_correct.get(gold_family, 0) + 1


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * q
    f, c = int(k), min(int(k) + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)
