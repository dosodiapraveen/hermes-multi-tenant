import asyncio, sys, time
sys.path.insert(0, "/app")
from app.routers.webhook import run_hermes_runtime
async def main():
    for q in ["What are my reminders? Reply briefly.",
              "hello"]:
        t = time.time()
        r = await run_hermes_runtime("4fee15b6-e1a7-4a90-8b81-913fd6a19a74", q)
        dt = time.time() - t
        print(f"Q: {q!r}\n  latency={dt:.1f}s len={len(r or '')} reply={ (r or '')[:80]!r}\n")
asyncio.run(main())
