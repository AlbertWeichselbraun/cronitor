import asyncio
from nio import AsyncClient

from cronvisio.notifier import Notifier


class MatrixNotifier(Notifier):

    def __init__(self, homeserver: str, user_id: str, access_token: str, room_id: str):
        self.homeserver = homeserver
        self.user_id = user_id
        self.access_token = access_token
        self.room_id = room_id

    @staticmethod
    async def send_matrix_message(homeserver, user_id, access_token, room_id, message):
        """
        Sends the given message to the given matrix server.
        """
        client = AsyncClient(homeserver)
        client.access_token = access_token
        client.user_id = user_id

        await client.room_send(
            room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message},
        )
        await client.close()

    def send_notifications(self, messages):
        for msg in messages:
            if isinstance(msg, str):
                asyncio.get_event_loop().run_until_complete(
                    self.send_matrix_message(
                        homeserver=self.homeserver,
                        user_id=self.user_id,
                        access_token=self.access_token,
                        room_id=self.room_id,
                        message=msg,
                    )
                )
            else:
                for m in msg:
                    asyncio.get_event_loop().run_until_complete(
                        self.send_matrix_message(
                            homeserver=self.homeserver,
                            user_id=self.user_id,
                            access_token=self.access_token,
                            room_id=self.room_id,
                            message=m,
                        )
                    )
