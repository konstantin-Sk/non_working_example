import json
import asyncio
from nats.aio.client import Client as Nats
from datetime import datetime


# this class simulates some remote listener that interested in receiving
# messages with information about tasks status
class MessageListener:
    def __init__(self, _loop, nats_host="nats://127.0.0.1", nats_port="4222"):
        self.loop = _loop

        self.nc = Nats()
        self.nats_addr = nats_host + ':' + nats_port
        self.subject = "tasks.log"

        self.async_initialized = False

    async def async_init(self):
        await self.nc.connect(self.nats_addr, loop=self.loop)
        self.async_initialized = True

    @staticmethod
    async def subscribe_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = json.loads(msg.data.decode())
        # print time to show time difference between receiving a messages
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Received a message on '{subject} {reply}': {data} in TIME: {cur_time}".format(
            subject=subject, reply=reply, data=data, cur_time=current_time))

    async def listen(self):
        print("REMOTE LISTENER: STARTED LISTENING {}".format(self.subject))
        if not self.async_initialized:
            await self.async_init()

        await self.nc.subscribe(self.subject, cb=self.subscribe_handler)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    task_listener = MessageListener(loop)
    loop.run_until_complete(task_listener.listen())
    loop.run_forever()
