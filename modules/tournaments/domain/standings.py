from collections import Counter, defaultdict


def rank_group(team_ids, matches, tie_break_order):
    """Puntos, DG, GF, mini-tabla entre empatados, victorias, disciplina y sorteo registrado."""
    rows = {
        team_id: dict(wins=0, draws=0, losses=0, goals_for=0, goals_against=0)
        for team_id in team_ids
    }
    discipline = dict.fromkeys(team_ids, 0)

    for match in matches:
        home, away = rows[match.home_team_id], rows[match.away_team_id]
        home_score, away_score = match.home_goal_count, match.away_goal_count
        home["goals_for"] += home_score
        home["goals_against"] += away_score
        away["goals_for"] += away_score
        away["goals_against"] += home_score
        discipline[match.home_team_id] += (
            match.home_yellow_card_count + 3 * match.home_red_card_count
        )
        discipline[match.away_team_id] += (
            match.away_yellow_card_count + 3 * match.away_red_card_count
        )

        if home_score == away_score:
            home["draws"] += 1
            away["draws"] += 1
        else:
            winner, loser = (home, away) if home_score > away_score else (away, home)
            winner["wins"] += 1
            loser["losses"] += 1

    buckets = defaultdict(list)

    for team_id, row in rows.items():
        buckets[
            (
                row["wins"] * 3 + row["draws"],
                row["goals_for"] - row["goals_against"],
                row["goals_for"],
            )
        ].append(team_id)

    keys = {}
    manual = {team_id: index for index, team_id in enumerate(tie_break_order)}
    has_manual_order = set(manual) == {str(team_id) for team_id in team_ids} and len(manual) == len(
        team_ids
    )

    for basic, tied in buckets.items():
        head_to_head = {team_id: [0, 0, 0] for team_id in tied}

        for match in matches:
            if match.home_team_id not in head_to_head or match.away_team_id not in head_to_head:
                continue

            for team_id, scored, conceded in (
                (match.home_team_id, match.home_goal_count, match.away_goal_count),
                (match.away_team_id, match.away_goal_count, match.home_goal_count),
            ):
                values = head_to_head[team_id]
                values[0] += 3 if scored > conceded else 1 if scored == conceded else 0
                values[1] += scored - conceded
                values[2] += scored

        for team_id in tied:
            keys[team_id] = (
                *basic,
                *head_to_head[team_id],
                rows[team_id]["wins"],
                -discipline[team_id],
            )

    counts = Counter(keys.values())
    ordered = sorted(
        team_ids,
        key=lambda team_id: (
            *(-value for value in keys[team_id]),
            manual[str(team_id)] if has_manual_order else 0,
            str(team_id),
        ),
    )

    return tuple(
        (team_id, rows[team_id], counts[keys[team_id]] > 1 and not has_manual_order)
        for team_id in ordered
    )
