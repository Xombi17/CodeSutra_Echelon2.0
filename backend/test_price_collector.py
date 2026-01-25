
import asyncio
import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))

async def test_pricing():
    print("Testing PriceCollector...")
    try:
        from data_collection import PriceCollector
        collector = PriceCollector()
        data = await collector.fetch_price_data()
        print(f"Price data: {data}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pricing())
