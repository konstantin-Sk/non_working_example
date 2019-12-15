import json
import asyncio
from nats.aio.client import Client as Nats


class MessageSender:
    def __init__(self, loop, nats_host="nats://127.0.0.1", nats_port="4222"):
        self.loop = loop

        self.nc = Nats()
        self.nats_addr = nats_host + ':' + nats_port
        self.subject = "tasks.log"

        self.async_initialized = False

    async def async_init(self):
        await self.nc.connect(self.nats_addr, loop=self.loop)
        self.async_initialized = True

    async def send_message(self, msg):
        if not self.async_initialized:
            await self.async_init()

        await self.nc.publish(self.subject, msg)


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    task_id = req
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_n_execute(loop, task_id))
    return req


async def init_n_execute(loop, task_id):
    nats_host = "nats://127.0.0.1"
    nats_port = "4222"

    ms = MessageSender(loop, nats_host=nats_host, nats_port=nats_port)

    await ms.send_message(json.dumps({"task_status": "STARTED",
                                      "task_id": task_id}).encode())


if __name__ == '__main__':
    handle("TEST_TEST")

