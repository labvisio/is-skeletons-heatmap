import socket
from typing import List

from is_wire.core import Channel, Message
from is_wire.core.utils import now


class CustomChannel(Channel):
    def __init__(
        self, uri: str = "amqp://guest:guest@localhost:5672", exchange: str = "is"
    ) -> None:
        super().__init__(uri=uri, exchange=exchange)
        self._deadline = now()
        self._running = False

    def consume_for(self, period: float) -> List[Message]:
        if not self._running:
            self._deadline = now()
            self._running = True
        self._deadline = self._deadline + period
        messages = []
        while True:
            try:
                message = self.consume_until(deadline=self._deadline)
                messages.append(message)
            except socket.timeout:
                break
        return messages

    def consume_until(self, deadline: float) -> Message:
        timeout = max([deadline - now(), 0.0])
        return self.consume(timeout=timeout)
