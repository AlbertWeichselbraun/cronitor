import asyncio
from nio import AsyncClient

from cronitor.notifier import Notifier


class MatrixNotifier(Notifier):

    def __init__(self, config: dict[str, str]):
        self.config = config

    @staticmethod
    async def send_matrix_message(homeserver, user_id, access_token, room_id, message):
        '''
        Sends the given message to the given matrix server.
        '''
        client = AsyncClient(homeserver)
        client.access_token = access_token
        client.user_id = user_id

        await client.room_send(
            room_id,
            message_type='m.room.message',
            content={
                'msgtype': 'm.text',
                'body': message
            })
        await client.close()

    def send_notification(self, msg):
        asyncio.get_event_loop().run_until_complete(
            self.send_matrix_message(homeserver=self.config['matrix_homeserver'],
                                     user_id=self.config['matrix_user_id'],
                                     access_token=self.config['matrix_access_token'],
                                     room_id=self.config['matrix_room_id'],
                                     message=msg)
        )

