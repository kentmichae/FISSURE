#!/usr/bin/env python3
"""Debug FISSURE Server startup to find crash point."""
import sys, asyncio, traceback
sys.path.insert(0, "/home/nebulaone/spark-dev-workspace/FISSURE")
sys.path.insert(0, "/home/nebulaone/spark-dev-workspace/FISSURE/fissure-venv/lib/python3.11/site-packages")

print("[1] Setting env...")
import os
os.environ['DISPLAY'] = ':99'
os.environ['QT_API'] = 'pyqt6'
os.environ['MPL_BACKEND'] = 'agg'

print("[2] Checking imports...")
try:
    import fissure.comms
    print("  ✓ fissure.comms")
except Exception as e:
    print(f"  ✗ fissure.comms: {e}")
    sys.exit(1)

try:
    import fissure.utils
    print("  ✓ fissure.utils")
except Exception as e:
    print(f"  ✗ fissure.utils: {e}")
    sys.exit(1)

print("[3] Constructing HiprFisr...")
try:
    from fissure.Server.HiprFisr import HiprFisr
    from fissure.comms import Address
    addr = Address(protocol='ipc', address='fissure')
    hiprfisr = HiprFisr(addr, dashboard_expected=False)
    print("  ✓ HiprFisr instance created")
    print(f"  Sensors on port: 6100/6101")
except Exception as e:
    print(f"  ✗ HiprFisr: {e}")
    traceback.print_exc()
    sys.exit(1)

print("[4] Constructing PD...")
try:
    from fissure.Server.ProtocolDiscovery import ProtocolDiscovery
    pd = ProtocolDiscovery()
    print("  ✓ PD instance created")
except Exception as e:
    print(f"  ✗ PD: {e}")
    traceback.print_exc()
    sys.exit(1)

print("[5] Constructing TSI...")
try:
    from fissure.Server.TargetSignalIdentification import TargetSignalIdentification
    tsi = TargetSignalIdentification()
    print("  ✓ TSI instance created")
except Exception as e:
    print(f"  ✗ TSI: {e}")
    traceback.print_exc()
    sys.exit(1)

print("[6] Starting tasks...")
async def begin(name, obj):
    print(f"  → {name}.begin()...")
    try:
        await obj.begin()
        print(f"  ← {name}.begin() completed (should not happen in loop)")
        return True
    except Exception as e:
        print(f"  ← {name}.begin() CRASHED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

async def main():
    tasks = [
        asyncio.create_task(begin("HiprFisr", hiprfisr)),
        asyncio.create_task(begin("PD", pd)),
        asyncio.create_task(begin("TSI", tsi)),
    ]
    await asyncio.sleep(2)  # Allow startup

an = asyncio.new_event_loop()
asyncio.set_event_loop(an)
an.run_until_complete(main())
