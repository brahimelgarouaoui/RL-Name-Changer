"""
Rocket League Name Changer - mitmproxy Addon and Controller Module
"""

import json
import asyncio
import logging
from threading import Thread, Event

try:
    from mitmproxy import http
    from mitmproxy.tools.dump import DumpMaster
    from mitmproxy.options import Options
except ImportError as e:
    logging.critical(f"Failed to import mitmproxy modules: {e}")
    raise

logger = logging.getLogger(__name__)


class NameSpoofAddon:
    """mitmproxy addon that intercepts and modifies display names."""

    def __init__(self, new_name):
        self.new_name = new_name
        logger.debug(f"Addon initialized with spoof name '{self.new_name}'")

    def update_name(self, new_name):
        """Update the spoofed name."""
        logger.info(f"Updating spoof name: {self.new_name} -> {new_name}")
        self.new_name = new_name

    def response(self, flow: http.HTTPFlow):
        """Process HTTP responses and modify displayName if found."""
        target_domains = [
            "epicgames.dev",
            "epicgames.com",
            "psyonix.com",
            "live.psynet.gg",
        ]
        if any(d in flow.request.pretty_host for d in target_domains):
            ctype = flow.response.headers.get("Content-Type", "")
            if "application/json" in ctype:
                self._process_json_body(flow)

    def _process_json_body(self, flow: http.HTTPFlow):
        """Process JSON response body and modify displayName."""
        try:
            body_data = flow.response.json()
        except json.JSONDecodeError:
            return

        if isinstance(body_data, list) and body_data and isinstance(body_data[0], dict):
            user_data = body_data[0]
            if "displayName" in user_data:
                old_name = user_data["displayName"]
                if old_name != self.new_name:
                    user_data["displayName"] = self.new_name
                    flow.response.content = json.dumps(
                        body_data, ensure_ascii=False
                    ).encode("utf-8")
                    flow.response.headers["Content-Length"] = str(
                        len(flow.response.content)
                    )
                    logger.info(
                        f"SPOOFED: {old_name} -> {self.new_name} ({flow.request.pretty_host})"
                    )


class ProxyController:
    """
    Controls the mitmproxy DumpMaster lifecycle in a background thread.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._thread = None
        self._loop = None
        self._started_evt = Event()
        self._stopped_evt = Event()
        self._name = None
        self._master = None
        self._addon = None

    def is_running(self):
        """Check if the proxy is currently running."""
        return (
            self._thread is not None
            and self._thread.is_alive()
            and self._started_evt.is_set()
            and not self._stopped_evt.is_set()
        )

    def start(self, spoof_name):
        """Start the proxy with the given spoof name."""
        if self.is_running():
            logger.warning("Proxy already running; ignoring start().")
            return True

        self._name = spoof_name
        self._started_evt.clear()
        self._stopped_evt.clear()

        def worker():
            logger.debug("Proxy thread starting...")
            try:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)

                async def run_proxy():
                    try:
                        options = Options(
                            listen_host=self.host,
                            listen_port=self.port,
                            mode=["regular"],
                        )
                        self._master = DumpMaster(options, with_termlog=False)
                        self._addon = NameSpoofAddon(spoof_name)
                        self._master.addons.add(self._addon)

                        # Mark as started before running
                        self._started_evt.set()
                        logger.info("Proxy running at %s:%s", self.host, self.port)

                        await self._master.run()
                        logger.debug("DumpMaster.run() returned normally.")
                    except Exception as e:
                        logger.error("Mitmproxy runtime error: %s", e)
                    finally:
                        logger.debug(
                            "Proxy thread cleanup: shutting down master if exists."
                        )
                        try:
                            if self._master:
                                self._master.shutdown()
                        except Exception:
                            pass
                        self._master = None
                        self._addon = None
                        self._stopped_evt.set()
                        logger.debug("Proxy thread cleanup finished.")

                self._loop.run_until_complete(run_proxy())

            except Exception as e:
                logger.error("Proxy thread top-level error: %s", e)
                self._stopped_evt.set()
            finally:
                try:
                    if self._loop and not self._loop.is_closed():
                        # Cancel pending tasks to avoid "Task was destroyed" warnings
                        pending = asyncio.all_tasks(self._loop)
                        for task in pending:
                            task.cancel()
                            try:
                                self._loop.run_until_complete(task)
                            except Exception:
                                pass
                        self._loop.stop()
                        self._loop.close()
                except Exception as e:
                    logger.debug("Error closing proxy event loop: %s", e)
                logger.debug("Proxy thread exiting.")

        self._thread = Thread(target=worker, name="MitmproxyThread", daemon=True)
        self._thread.start()

        # Wait for started flag
        if not self._started_evt.wait(timeout=3.0):
            logger.error("Proxy failed to report started within timeout.")
            return False
        logger.debug("Proxy start sequence marked as running.")
        return True

    def stop(self, timeout=5.0):
        """Stop the proxy with the given timeout."""
        if not self.is_running():
            logger.info("Proxy not running; nothing to stop.")
            self._stopped_evt.set()
            return

        logger.info("Stopping proxy (timeout %.1fs) ...", timeout)
        try:
            if self._master:
                self._master.shutdown()
        except Exception as e:
            logger.warning("Error calling master.shutdown(): %s", e)

        # Wait for thread to exit cleanly
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.error("Proxy thread did not stop within %.1fs.", timeout)
            else:
                logger.info("Proxy thread stopped cleanly.")

        # Mark stopped regardless, to avoid stale state
        self._stopped_evt.set()
        self._thread = None
        self._loop = None
        self._master = None
        self._addon = None
        logger.debug("ProxyController stop() finished.")

    def update_spoof_name(self, new_name):
        """Update the spoof name for the running proxy."""
        if self.is_running() and self._addon:
            self._addon.update_name(new_name)
            self._name = new_name
