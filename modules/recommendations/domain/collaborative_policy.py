from collections import defaultdict
from math import sqrt

from modules.recommendations.constants import (
    COLLABORATIVE_MAX_BONUS,
    COLLABORATIVE_MAX_NEIGHBORS,
    COLLABORATIVE_MIN_SHARED_CONTENT,
    COLLABORATIVE_MIN_SIMILARITY,
    COLLABORATIVE_MIN_SUPPORT,
)


class CollaborativePolicy:
    @staticmethod
    def recommend(target: dict[str, float], peers: dict[str, dict[str, float]]) -> dict[str, float]:
        target = {key: value for key, value in target.items() if value > 0}
        target_norm = sqrt(sum(value * value for value in target.values()))
        if not target_norm:
            return {}
        neighbors = []
        for visitor_id, vector in peers.items():
            vector = {key: value for key, value in vector.items() if value > 0}
            shared = target.keys() & vector.keys()
            if len(shared) < COLLABORATIVE_MIN_SHARED_CONTENT:
                continue
            norm = sqrt(sum(value * value for value in vector.values()))
            similarity = sum(target[key] * vector[key] for key in shared) / (target_norm * norm)
            if similarity >= COLLABORATIVE_MIN_SIMILARITY:
                neighbors.append((similarity, visitor_id, vector, norm))
        neighbors.sort(key=lambda neighbor: (-neighbor[0], neighbor[1]))
        support, scores = defaultdict(int), defaultdict(float)
        selected = neighbors[:COLLABORATIVE_MAX_NEIGHBORS]
        total_similarity = sum(neighbor[0] for neighbor in selected)
        for similarity, _, vector, norm in selected:
            for key, value in vector.items():
                if key in target:
                    continue
                support[key] += 1
                scores[key] += similarity * value / norm
        return {
            key: min(COLLABORATIVE_MAX_BONUS, COLLABORATIVE_MAX_BONUS * score / total_similarity)
            for key, score in scores.items()
            if support[key] >= COLLABORATIVE_MIN_SUPPORT
        }
