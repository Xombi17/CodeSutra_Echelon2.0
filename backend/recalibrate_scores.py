import asyncio
from narrative.lifecycle_tracker import lifecycle_tracker
from database import get_session, Narrative

async def recalibrate():
    print("🔄 Recalibrating all narrative strength scores...")
    session = get_session()
    try:
        narratives = session.query(Narrative).filter(Narrative.phase != 'death').all()
        for n in narratives:
            old_strength = n.strength
            new_strength = lifecycle_tracker.calculate_narrative_strength(n)
            n.strength = new_strength
            print(f"  ✨ {n.name}: {old_strength} -> {new_strength}")
        session.commit()
        print("\n✅ All scores updated in database!")
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(recalibrate())
