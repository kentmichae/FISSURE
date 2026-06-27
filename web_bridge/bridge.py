#!/usr/bin/env python3
"""
FISSURE ZMQ-to-WebSocket Bridge
Connects to HIPRFISR Router sockets and broadcasts messages to WebSocket clients.
"""

import asyncio
import json
import logging
import os
import sys
import signal as sig

# Add fissure to path
sys.path.insert(0, "/home/nebulaone/spark-dev-workspace/FISSURE")
sys.path.insert(0, "/home/nebulaone/spark-dev-workspace/FISSURE/fissure-venv/lib/python3.11/site-packages")

import zmq
import zmq.asyncio

from aiohttp import web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("fissure-bridge")


# ── Configuration ──────────────────────────────────────────────────────────

HB_ADDR = "tcp://127.0.0.1:6100"  # HIPRFISR heartbeat channel
MSG_ADDR = "tcp://127.0.0.1:6101"  # HIPRFISR message channel
WS_HOST = "0.0.0.0"
WS_PORT = int(os.environ.get("BRIDGE_PORT", "8765"))
HEARTBEAT_INTERVAL = 5  # seconds

# ── WebSocket clients ─────────────────────────────────────────────────────

active_clients: set[web.WebSocketResponse] = set()

# ── ZMQ Setup ─────────────────────────────────────────────────────────────

zmq_ctx = zmq.asyncio.Context()
zmq_hb_sock: zmq.asyncio.Socket = zmq_ctx.socket(zmq.SUB)
zmq_msg_sock: zmq.asyncio.Socket = zmq_ctx.socket(zmq.SUB)

# Subscribe to everything
zmq_hb_sock.setsockopt(zmq.SUBSCRIBE, b"")
zmq_msg_sock.setsockopt(zmq.SUBSCRIBE, b"")

heartbeat_count = 0
total_messages = 0
last_hb_time = 0
active_sessions = 0
active_attacks = 0

# ── Stats Endpoint ─────────────────────────────────────────────────────────

async def handle_stats(request):
    """Return current server stats as JSON."""
    data = {
        "heartbeat_count": heartbeat_count,
        "total_messages": total_messages,
        "last_hb_time": last_hb_time,
        "active_sessions": active_sessions,
        "active_attacks": active_attacks,
        "clients": len(active_clients),
        "bridge_port": WS_PORT,
        "hb_addr": HB_ADDR,
        "msg_addr": MSG_ADDR,
    }
    return web.json_response(data)


# ── WebSocket Route ─────────────────────────────────────────────────────────

async def websocket_handler(request):
    """WebSocket endpoint for browser clients."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    active_clients.add(ws)
    logger.info("Client connected. Total clients: %d", len(active_clients))
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    payload = json.loads(msg.data)
                    await handle_client_command(payload, ws)
                except json.JSONDecodeError:
                    await ws.send_json({"error": "Invalid JSON"})
            elif msg.type == web.WSMsgType.ERROR:
                logger.error("WS error: %s", ws.exception())
    finally:
        active_clients.discard(ws)
        logger.info("Client disconnected. Total clients: %d", len(active_clients))
    return ws


async def handle_client_command(payload, ws):
    """Handle inbound commands from browser to HIPRFISR server."""
    global active_sessions, active_attacks
    cmd_type = payload.get("type", "")
    msg_name = payload.get("MessageName", cmd_type)

    msg_obj = {
        "MessageName": msg_name,
        "Source": "WebGUI",
        "Identifier": "web-bridge",
        "Destination": "HiprFisr",
        "Type": "Commands",
        "Parameters": payload.get("parameters", {}),
        "Time": __import__('time').time(),
    }

    # Forward to HIPRFISR via ZMQ
    try:
        await asyncio.wait_for(
            asyncio.shield(zmq_msg_sock.send_json(msg_obj)),
            timeout=1.0,
        )
        await ws.send_json({"type": "ack", "MessageName": msg_name})
    except Exception as e:
        await ws.send_json({"type": "error", "MessageName": msg_name, "error": str(e)})

    # Update session/attack counters from command type
    if cmd_type == "SessionStart":
        active_sessions += 1
    elif cmd_type == "SessionEnd":
        active_sessions = max(0, active_sessions - 1)
    elif "Attack" in msg_name or cmd_type == "Attack":
        active_attacks = max(0, active_attacks - 1)


# ── ZMQ Forwarders ─────────────────────────────────────────────────────────

async def forward_zmq_msgs(sock: zmq.asyncio.Socket, kind: str):
    """Continuously read ZMQ messages and broadcast to all WebSocket clients."""
    global total_messages, heartbeat_count, last_hb_time

    while True:
        try:
            frames = await sock.recv_multipart()
            body = frames[-1].decode("utf-8", errors="replace")
            try:
                msg = json.loads(body)
            except json.JSONDecodeError:
                msg = {"_raw": body, "_channel": kind}

            msg["_channel"] = kind
            msg["_source"] = kind

            if kind == "HB" and str(msg.get("Heartbeat", "").lower()) == "true":
                heartbeat_count += 1
                last_hb_time = __import__('time').time()

            # Track active entities from heartbeat
            src = msg.get("Source", "")
            if src and "Sensor Node" in src:
                pass  # could track nodes here

            payload = {
                "type": kind,
                "message": msg,
                "timestamp": __import__('time').time(),
            }
            total_messages += 1

            # Broadcast to all connected websocket clients
            dead = set()
            for client in active_clients:
                try:
                    await client.send_json(payload)
                except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError, Exception):
                    dead.add(client)
            active_clients -= dead

        except zmq.Again:
            await asyncio.sleep(0.01)
        except Exception as e:
            logger.error("ZMQ forwarder (%s) error: %s", kind, e, exc_info=True)
            await asyncio.sleep(1)


# ── Health Check Ping ──────────────────────────────────────────────────────

async def ping_hiprfisr():
    """Periodically ping HIPRFISR to keep connection alive."""
    while True:
        try:
            pulse = {
                "MessageName": "Ping",
                "Source": "WebBridge",
                "Identifier": "web-bridge",
                "Heartbeat": "true",
                "Type": "Heartbeats",
                "Time": __import__('time').time(),
            }
            await zmq_msg_sock.send_json(pulse, flags=zmq.NOBLOCK)
        except (zmq.Again, Exception):
            pass
        await asyncio.sleep(HEARTBEAT_INTERVAL)


# ── App Setup ──────────────────────────────────────────────────────────────

async def start_zmq(app: web.Application):
    """Initialize ZMQ sockets and start forwarders."""
    logger.info(f"Connecting ZMQ HB to {HB_ADDR}")
    zmq_hb_sock.connect(HB_ADDR)
    logger.info(f"Connecting ZMQ MSG to {MSG_ADDR}")
    zmq_msg_sock.connect(MSG_ADDR)

    logger.info(f"Starting ZMQ forwarders...")
    hb_task = asyncio.create_task(forward_zmq_msgs(zmq_hb_sock, "HB"))
    msg_task = asyncio.create_task(forward_zmq_msgs(zmq_msg_sock, "MSG"))
    ping_task = asyncio.create_task(ping_hiprfisr())

    app["tasks"] = [hb_task, msg_task, ping_task]
    logger.info("Bridge started. Monitoring HIPRFISR on 6100/6101")


async def stop_zmq(app: web.Application):
    """Shut down ZMQ sockets."""
    logger.info("Shutting down bridge...")
    for task in app.get("tasks", []):
        task.cancel()
    try:
        await asyncio.gather(*app.get("tasks", []), return_exceptions=True)
    except asyncio.CancelledError:
        pass
    zmq_hb_sock.close()
    zmq_msg_sock.close()
    zmq_ctx.term()


def create_app():
    """Create the aiohttp application."""
    app = web.Application()
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get("/stats", handle_stats)
    app.on_startup.append(start_zmq)
    app.on_shutdown.append(stop_zmq)
    return app


# ── Main ────────────────────────────────────────────────────────────────────

async def main():
    logger.info(f"Starting FISSURE ZMQ-to-WebSocket Bridge on port {WS_PORT}")
    logger.info(f"ZMQ HB: {HB_ADDR}  MSG: {MSG_ADDR}")
    
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WS_HOST, WS_PORT)
    await site.start()
    
    logger.info(f"Website UI: http://localhost:{WS_PORT}/index.html")
    logger.info(f"WebSocket:  ws://localhost:{WS_PORT}/ws")
    logger.info(f"Stats:      http://localhost:{WS_PORT}/stats")
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bridge stopped by user")
