import asyncio, sys
sys.path.insert(0, "/app")
from app.routers.webhook import run_hermes_runtime
r = asyncio.run(run_hermes_runtime("4fee15b6-e1a7-4a90-8b81-913fd6a19a74", "What are my reminders?"))
print("====REPLY_START====")
print(repr(r)[:1500])
print("====REPLY_END====")
