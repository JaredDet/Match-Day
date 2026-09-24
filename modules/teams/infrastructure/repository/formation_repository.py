from modules.teams.domain.formation import TeamFormation


class FormationRepository:
    def list(self, team_id):
        return list(TeamFormation.objects.filter(team_id=team_id))

    def get_for_update(self, formation_id, team_id):
        return (
            TeamFormation.objects.select_for_update()
            .filter(id=formation_id, team_id=team_id)
            .first()
        )

    def save(self, formation):
        if formation.is_default:
            TeamFormation.objects.filter(team_id=formation.team_id, is_default=True).exclude(
                id=formation.id
            ).update(is_default=False)
        formation.save()

    def delete(self, formation):
        formation.delete()
