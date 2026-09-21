from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from modules.recommendations.constants import (
    INTEREST_HALF_LIFE_DAYS,
    MAX_ACTIVE_SECONDS_PER_CONTENT_DAY,
    SECTION_SIZE,
)
from modules.recommendations.domain.content_reference import ContentKind, RecommendationContent


@dataclass(frozen=True, slots=True)
class InterestWeights:
    teams: dict[str, float]
    tournaments: dict[str, float]
    seen: frozenset[str]


class RecommendationPolicy:
    @staticmethod
    def profile(activities, contents: dict[str, RecommendationContent], now: datetime):
        teams, tournaments = defaultdict(float), defaultdict(float)
        seen = set()
        daily_active_seconds = defaultdict(int)
        for activity in activities:
            key = f"{activity.content_kind}:{activity.content_id}"
            content = contents.get(key)
            if content is None:
                continue
            age_days = max(0, (now - activity.occurred_at).total_seconds() / 86400)
            daily_key = (key, activity.occurred_at.date())
            remaining = MAX_ACTIVE_SECONDS_PER_CONTENT_DAY - daily_active_seconds[daily_key]
            active_seconds = min(activity.active_seconds, max(0, remaining))
            daily_active_seconds[daily_key] += active_seconds
            weight = (int(activity.counts_as_visit) + active_seconds / 60) * (
                0.5 ** (age_days / INTEREST_HALF_LIFE_DAYS)
            )
            seen.add(key)
            for team_id in content.team_ids:
                teams[str(team_id)] += weight / len(content.team_ids)
            for tournament_id in content.tournament_ids:
                tournaments[str(tournament_id)] += weight
        return InterestWeights(dict(teams), dict(tournaments), frozenset(seen))

    @staticmethod
    def recommend(contents, profile: InterestWeights, now: datetime) -> dict:
        ranked = []
        for content in contents:
            if content.reference.kind == ContentKind.PLAYER:
                continue
            team_score = max((profile.teams.get(str(i), 0) for i in content.team_ids), default=0)
            tournament_score = (
                max((profile.tournaments.get(str(i), 0) for i in content.tournament_ids), default=0)
                * 0.7
            )
            affinity = team_score + tournament_score
            freshness = (
                1 / (1 + abs((now - content.date).total_seconds()) / 86400) if content.date else 0
            )
            reason = "recent_content"
            if affinity:
                reason = (
                    "team_interest" if team_score >= tournament_score else "tournament_interest"
                )
            elif content.live:
                reason = "live_match"
            ranked.append(
                {
                    "kind": content.reference.kind,
                    "id": str(content.reference.id),
                    "score": round(affinity + freshness + int(content.live), 6),
                    "affinity": affinity,
                    "reason": reason,
                    "key": content.reference.key,
                }
            )
        ranked.sort(key=lambda item: (-item["score"], item["key"]))
        sections = {
            "news": [item for item in ranked if item["kind"] == ContentKind.NEWS][:SECTION_SIZE],
            "matches": [item for item in ranked if item["kind"] == ContentKind.MATCH][
                :SECTION_SIZE
            ],
            "tournaments": [item for item in ranked if item["kind"] == ContentKind.TOURNAMENT][
                :SECTION_SIZE
            ],
        }
        displayed = {item["key"] for items in sections.values() for item in items}
        discoveries = [
            item
            for item in ranked
            if item["key"] not in displayed and item["key"] not in profile.seen
        ]
        discoveries.sort(key=lambda item: (item["affinity"], -item["score"], item["key"]))
        sections["discovery"] = [
            {**item, "reason": "discovery"} for item in discoveries[:SECTION_SIZE]
        ]
        return {
            section: [
                {key: item[key] for key in ("kind", "id", "score", "reason")} for item in items
            ]
            for section, items in sections.items()
        }
