from modules.matches.domain.penalty_attempt import PenaltyAttempt


class PenaltyAttemptRepository:
    def save(self, penalty_attempt: PenaltyAttempt) -> None:
        penalty_attempt.save()
