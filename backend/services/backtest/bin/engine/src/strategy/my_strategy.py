from core.engine_state import EngineState
from .base import Strategy
from orders import Signal, OrderType


class Strategy1(Strategy):

    FLAT = "FLAT"
    LONG = "LONG"
    SHORT = "SHORT"

    def __init__(
        self,
        kind: str,
        params: dict
    ):
        super().__init__(
            kind,
            params,
        )

        self.position_state: str = self.FLAT

    def to_dict(self):
        return {
            "kind": self.kind,
            "params": self.params,
            "position_state": self.position_state,
        }

    def set_state(
        self,
        state: dict
    ) -> None:

        position_state = state.get("position_state")

        if position_state is not None:
            self.position_state = position_state

    def evaluate(
        self,
        state: EngineState
    ):

        tf = state.timeframes.get("1m")

        ema_55 = tf.get_series(
            "EMA",
            "EMA 55"
        )

        ema_200 = tf.get_series(
            "EMA",
            "EMA 200"
        )

        if not ema_55.history or not ema_200.history:
            return None

        previous_55 = ema_55.history[-1]
        previous_200 = ema_200.history[-1]

        current_55 = ema_55.live
        current_200 = ema_200.live

        cross_up = (
            previous_55.value <= previous_200.value
            and current_55.value > current_200.value
        )

        cross_down = (
            previous_55.value >= previous_200.value
            and current_55.value < current_200.value
        )

        # --------------------------------------------------
        # FLAT
        # --------------------------------------------------

        if self.position_state == self.FLAT:

            if cross_up:
                self.position_state = self.LONG

                return Signal(
                    action="BUY",
                    quantity=1,
                    order_type=OrderType.MARKET,
                )

            if cross_down:
                self.position_state = self.SHORT

                return Signal(
                    action="SELL",
                    quantity=1,
                    order_type=OrderType.MARKET,
                )

            return None

        # --------------------------------------------------
        # LONG
        # --------------------------------------------------

        if self.position_state == self.LONG:

            # No se puede abrir otra posición.
            # El cruce bajista únicamente cierra LONG.
            if cross_down:
                self.position_state = self.FLAT

                return Signal(
                    action="EXIT",
                )

            return None

        # --------------------------------------------------
        # SHORT
        # --------------------------------------------------

        if self.position_state == self.SHORT:

            # No se puede abrir otra posición.
            # El cruce alcista únicamente cierra SHORT.
            if cross_up:
                self.position_state = self.FLAT

                return Signal(
                    action="EXIT",
                )

            return None

        return None
