import socket
from typing import List

from is_wire.core import Channel, Message
from is_wire.core.utils import now


class CustomChannel(Channel):

    def consume_for(self, duration: float) -> List[Message]:
        deadline = now() + duration
        messages = []
        while True:
            try:
                message = self.consume_until(deadline=deadline)
                messages.append(message)
            except socket.timeout:
                break
        return messages

    def consume_until(self, deadline: float):
        timeout = max([deadline - now(), 0.0])
        return self.consume(timeout=timeout)
