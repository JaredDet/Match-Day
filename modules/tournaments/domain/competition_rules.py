from modules.matches.domain.match import MatchStatus
from modules.tournaments.domain.phase import PhaseStatus
from modules.tournaments.errors import TournamentErrors


class CompetitionRules:
    @staticmethod
    def ensure_mutable(phase, *, has_started: bool, has_successors: bool) -> None:
        if (
            phase.generated
            or phase.status != PhaseStatus.SCHEDULED
            or has_started
            or has_successors
        ):
            raise TournamentErrors.StructureLocked

    @staticmethod
    def validate_entrants(team_ids, registered_ids) -> None:
        count = len(team_ids)

        if count < 2 or count > 64 or count & (count - 1) or len(set(team_ids)) != count:
            raise TournamentErrors.InvalidBracket

        if not set(team_ids).issubset(registered_ids):
            raise TournamentErrors.TeamNotRegistered

    @staticmethod
    def winner(match):
        if match.status != MatchStatus.FINISHED:
            return None

        if match.home_goal_count != match.away_goal_count:
            return (
                match.home_team_id
                if match.home_goal_count > match.away_goal_count
                else match.away_team_id
            )

        shootout = getattr(match, "penalty_shootout", None)

        if (
            shootout is None
            or shootout.status != "finished"
            or shootout.winner_team_side not in ("home", "away")
        ):
            return None

        return match.home_team_id if shootout.winner_team_side == "home" else match.away_team_id
