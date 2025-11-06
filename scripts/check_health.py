import asyncio

import httpx


async def main() -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        print(response.status_code, response.json())


if __name__ == "__main__":
    asyncio.run(main())
