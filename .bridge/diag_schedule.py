import asyncio, sys, time
sys.path.insert(0, "/app")
from app.routers.webhook import run_hermes_runtime

async def main():
    for q in ["what is in my schedule"]:
        t = time.time()
        r = await run_hermes_runtime("4fee15b6-e1a7-4a90-8b81-913fd6a19a74", q)
        dt = time.time() - t
        print(f"Q={q} TIME={dt:.1f}s REPLY_LEN={len(r or '')} REPLY_START={ (r or '')[:120] !r}")

asyncio.run(main())
