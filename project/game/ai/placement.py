import utils.decisions_constants as log
from utils.decisions_logger import DecisionsLogger


class PlacementHandler:
    def __init__(self, player):
        self.player = player
        self.table = player.table

    def get_allowed_danger_modifier(self) -> int:
        placement = self._get_current_placement()
        placement_evaluation = self._get_placement_evaluation(placement)

        if placement_evaluation == Placement.VERY_COMFORTABLE_FIRST:
            if self.is_late_round:
                DecisionsLogger.debug(
                    log.PLACEMENT_DANGER_MODIFIER,
                    "Very comfortable first and late round",
                    {"placement": placement, "placement_evaluation": placement_evaluation},
                )
                return Placement.NO_RISK_DANGER_MODIFIER

            DecisionsLogger.debug(
                log.PLACEMENT_DANGER_MODIFIER,
                "Very comfortable first and NOT late round",
                {"placement": placement, "placement_evaluation": placement_evaluation},
            )
            return Placement.MODERATE_DANGER_MODIFIER

        if placement_evaluation == Placement.COMFORTABLE_FIRST:
            if self.is_late_round:
                DecisionsLogger.debug(
                    log.PLACEMENT_DANGER_MODIFIER,
                    "Comfortable first and late round",
                    {"placement": placement, "placement_evaluation": placement_evaluation},
                )
                return Placement.MODERATE_DANGER_MODIFIER

        return Placement.DEFAULT_DANGER_MODIFIER

    # TODO: different logic for tournament games
    def must_riichi(self, has_yaku, num_waits, cost_with_riichi, cost_with_damaten) -> int:
        # now we only change our decisions for oorasu
        if not self.is_oorasu:
            return Placement.DEFAULT_RIICHI_DECISION

        placement = self._get_current_placement()
        if not placement:
            return Placement.DEFAULT_RIICHI_DECISION

        placement_evaluation = self._get_placement_evaluation(placement)

        logger_context = {
            "placement": placement,
            "placement_evaluation": placement_evaluation,
            "has_yaku": has_yaku,
            "num_waits": num_waits,
            "cost_with_riichi": cost_with_riichi,
            "cost_with_damaten": cost_with_damaten,
            "round_step": self.player.round_step,
        }

        if placement["place"] == 1:
            if has_yaku:
                DecisionsLogger.debug(log.PLACEMENT_RIICHI_OR_DAMATEN, "1st place, has yaku", logger_context)
                return Placement.MUST_DAMATEN

            # no yaku but we can just sit here and chill
            if placement_evaluation >= Placement.VERY_COMFORTABLE_FIRST:
                DecisionsLogger.debug(
                    log.PLACEMENT_RIICHI_OR_DAMATEN, "1st place, very comfortable first", logger_context
                )
                return Placement.MUST_DAMATEN

            if placement_evaluation >= Placement.COMFORTABLE_FIRST:
                # just chill
                if num_waits < 6 or self.player.round_step > 11:
                    DecisionsLogger.debug(
                        log.PLACEMENT_RIICHI_OR_DAMATEN,
                        "1st place, comfortable first, late round, < 6 waits",
                        logger_context,
                    )
                    return Placement.MUST_DAMATEN

        if placement["place"] == 2:
            if cost_with_damaten < placement["diff_with_1st"] <= cost_with_riichi:
                if placement["diff_with_4th"] >= Placement.COMFORTABLE_DIFF_FOR_RISK:
                    DecisionsLogger.debug(
                        log.PLACEMENT_RIICHI_OR_DAMATEN, "2st place, we are good to risk", logger_context
                    )
                    return Placement.MUST_RIICHI

        # TODO: special rules for 3rd place
        if placement["place"] == 4:
            # TODO: consider going for better hand
            if cost_with_damaten < placement["diff_with_3rd"]:
                DecisionsLogger.debug(log.PLACEMENT_RIICHI_OR_DAMATEN, "4st place, let's riichi", logger_context)
                return Placement.MUST_RIICHI

        # general rule:
        if placement["place"] != 4 and has_yaku:
            if placement["diff_with_next_up"] > cost_with_riichi * 2 and placement["diff_with_next_down"] <= 1000:
                DecisionsLogger.debug(log.PLACEMENT_RIICHI_OR_DAMATEN, "not 4st place and has yaku", logger_context)
                return Placement.MUST_DAMATEN

        return Placement.DEFAULT_RIICHI_DECISION

    def _get_placement_evaluation(self, placement) -> int:
        if not placement:
            return Placement.NEUTRAL

        if placement["place"] == 1:
            assert placement["diff_with_2nd"] >= 0
            if placement["diff_with_2nd"] >= Placement.VERY_COMFORTABLE_DIFF:
                return Placement.VERY_COMFORTABLE_FIRST

            if placement["diff_with_2nd"] >= Placement.COMFORTABLE_FIRST:
                return Placement.COMFORTABLE_FIRST

        return Placement.NEUTRAL

    def _get_current_placement(self):
        if not self.points_initialized:
            return None

        players_by_points = self.table.get_players_sorted_by_scores()
        current_place = players_by_points.index(self.player)

        return {
            "place": current_place + 1,
            "diff_with_1st": abs(self.player.scores - players_by_points[0].scores),
            "diff_with_2nd": abs(self.player.scores - players_by_points[1].scores),
            "diff_with_3rd": abs(self.player.scores - players_by_points[2].scores),
            "diff_with_4th": abs(self.player.scores - players_by_points[3].scores),
            "diff_with_next_up": abs(self.player.scores - players_by_points[max(0, current_place - 1)].scores),
            "diff_with_next_down": abs(self.player.scores - players_by_points[min(3, current_place + 1)].scores),
        }

    @property
    def points_initialized(self):
        if [x for x in self.table.get_players_sorted_by_scores() if x.scores is None]:
            return False
        return True

    @property
    def is_oorasu(self):
        # TODO: consider tonpu
        return self.table.round_wind_number >= 7

    @property
    def is_late_round(self):
        # TODO: consider tonpu
        return self.table.round_wind_number >= 6


class DummyPlacementHandler(PlacementHandler):
    """
    Use this class in config if you want to disable placement logic for bot
    """

    def get_allowed_danger_modifier(self) -> int:
        return Placement.NO_RISK_DANGER_MODIFIER

    def must_riichi(self, has_yaku, num_waits, cost_with_riichi, cost_with_damaten) -> int:
        return Placement.DEFAULT_RIICHI_DECISION

    def _get_placement_evaluation(self, placement) -> int:
        return Placement.NEUTRAL


class Placement:
    # TODO: account for honbas and riichi sticks on the table
    VERY_COMFORTABLE_DIFF = 24100
    COMFORTABLE_DIFF_FOR_RISK = 18100
    COMFORTABLE_DIFF = 12100

    # player position in the game
    # must go in ascending order from bad to good, so we can use <, > operators with them
    NEUTRAL = 0
    COMFORTABLE_FIRST = 1
    VERY_COMFORTABLE_FIRST = 2

    # riichi definitions
    DEFAULT_RIICHI_DECISION = 0
    MUST_RIICHI = 1
    MUST_DAMATEN = 2

    # danger modifier
    NO_RISK_DANGER_MODIFIER = -3
    MODERATE_DANGER_MODIFIER = -2
    DEFAULT_DANGER_MODIFIER = 0