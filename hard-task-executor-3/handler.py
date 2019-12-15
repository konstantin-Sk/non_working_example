import json
import asyncio
from uuid import uuid4
from nats.aio.client import Client as Nats
from stan.aio.client import Client as Stan


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


async def hard_task():
    x = 0
    for _ in range(50000000):
        x += 1
    return x


async def task_executor(ms, task_id):
    await ms.send_message(json.dumps({"task_status": "STARTED",
                                      "task_id": task_id}).encode())
    await asyncio.sleep(.1)

    try:
        res = await hard_task()
    except Exception as e:
        await ms.send_message(json.dumps({"task_status": "FAILED",
                                          "message": repr(e),
                                          "task_id": task_id}).encode())
    else:
        await ms.send_message(json.dumps({"task_status": "FINISHED",
                                          "result": res,
                                          "task_id": task_id}).encode())


async def init_n_execute(loop, task_id):
    # listener_id = str(uuid4())
    nats_host="nats://127.0.0.1"
    nats_port="4222"
    # nats_addr = nats_host + ':' + nats_port
    # stan_cluster = "test-cluster"
    # nc = Nats()
    # sc = Stan()
    ms = MessageSender(loop, nats_host=nats_host, nats_port=nats_port)

    # await nc.connect(nats_addr, loop=loop)
    # await sc.connect(stan_cluster, "task-spawner-{}".format(listener_id),
    #                  nats=nc)
    #
    # await asyncio.sleep(0.1)
    #
    # await task_executor(ms, task_id)

    await ms.send_message(json.dumps({"task_status": "STARTED",
                                      "task_id": task_id}).encode())
