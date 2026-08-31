from modules.matches.domain.match_substitution import MatchSubstitution


class MatchSubstitutionRepository:
    def has_entered(self, squad_player_id) -> bool:
        return MatchSubstitution.objects.filter(player_in_id=squad_player_id).exists()

    def save(self, substitution: MatchSubstitution) -> None:
        substitution.save()
