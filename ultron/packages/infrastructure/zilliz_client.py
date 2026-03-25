"""
Ultron v3 — Zilliz Client (Multi-Account Pool)
Manages 15 Zilliz Cloud accounts for 15M total vectors.
Features: auto-discovery, capacity-based routing, parallel search, failover.
Includes tenacity retry/backoff and Ghost alerts on total failure.
"""

import asyncio
import logging
import os
from typing import Any, Optional

from pymilvus import MilvusClient
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("ultron.zilliz")


class ZillizPool:
    """
    Manages multiple Zilliz Cloud accounts as a unified pool.
    Routes inserts to accounts with available capacity.
    Searches all healthy accounts in parallel and merges results.
    """

    MAX_ACCOUNTS = 15

    def __init__(self) -> None:
        self._clients: dict[str, MilvusClient] = {}
        self._healthy: dict[str, bool] = {}
        self._usage_tracker: dict[str, int] = {}
        self._load_accounts_from_env()
        self._connect_all()

    def _load_accounts_from_env(self) -> None:
        """Read ZILLIZ_URI_1..15 and ZILLIZ_TOKEN_1..15 from environment."""
        self._accounts: list[dict[str, str]] = []

        for i in range(1, self.MAX_ACCOUNTS + 1):
            uri = os.getenv(f"ZILLIZ_URI_{i}", "")
            token = os.getenv(f"ZILLIZ_TOKEN_{i}", "")

            if uri and token:
                self._accounts.append({
                    "id": f"account_{i}",
                    "uri": uri,
                    "token": token,
                })

        logger.info(f"Loaded {len(self._accounts)} Zilliz accounts from env")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def _connect_all(self) -> None:
        """Create MilvusClient connections to all available accounts with retry."""
        for account in self._accounts:
            try:
                client = MilvusClient(
                    uri=account["uri"],
                    token=account["token"],
                )
                self._clients[account["id"]] = client
                self._healthy[account["id"]] = True
                self._usage_tracker[account["id"]] = 0
                logger.info(f"Connected to {account['id']}")
            except Exception as e:
                self._healthy[account["id"]] = False
                logger.error(f"Failed to connect to {account['id']}: {e}")

    @property
    def healthy_count(self) -> int:
        """Number of currently healthy Zilliz accounts."""
        return sum(1 for h in self._healthy.values() if h)

    def get_collection_with_space(
        self,
        collection_name: str,
        required_slots: int = 1,
    ) -> Optional[tuple[str, MilvusClient]]:
        """
        Returns the (account_id, client) with most available capacity.
        Rotates based on usage tracker to balance load.
        """
        healthy_accounts = [
            (aid, self._usage_tracker.get(aid, 0))
            for aid, is_healthy in self._healthy.items()
            if is_healthy and aid in self._clients
        ]

        if not healthy_accounts:
            return None

        # Select account with lowest usage
        healthy_accounts.sort(key=lambda x: x[1])
        best_id = healthy_accounts[0][0]
        return best_id, self._clients[best_id]

    async def _send_all_down_alert(self, operation: str, detail: str) -> None:
        """Send a Ghost alert when all Zilliz accounts are down."""
        try:
            from packages.interface.escalation import send_ghost_alert
            await send_ghost_alert(
                alert_type="ZILLIZ_ALL_DOWN",
                context={
                    "error": f"All Zilliz accounts unhealthy during {operation}",
                    "detail": detail,
                    "healthy_count": 0,
                    "total_accounts": len(self._accounts),
                },
            )
        except Exception as alert_err:
            logger.error(f"Failed to send ZILLIZ_ALL_DOWN alert: {alert_err}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def _insert_with_retry(
        self, client: MilvusClient, collection: str, data: list[dict]
    ) -> dict:
        """Insert with tenacity retry/backoff on transient failures."""
        return client.insert(collection_name=collection, data=data)

    async def insert(
        self,
        collection: str,
        data: list[dict],
    ) -> list[str]:
        """
        Insert data into the best available account.
        On failure, rotates to the next account.
        Alerts Ghost if all accounts are down.
        """
        ids: list[str] = []

        result = self.get_collection_with_space(collection, len(data))
        if not result:
            logger.error("No healthy Zilliz accounts available!")
            await self._send_all_down_alert("insert", f"collection={collection}, records={len(data)}")
            return ids

        account_id, client = result

        try:
            insert_result = await self._insert_with_retry(client, collection, data)
            self._usage_tracker[account_id] = (
                self._usage_tracker.get(account_id, 0) + len(data)
            )
            ids = insert_result.get("ids", []) if isinstance(insert_result, dict) else []
            return ids

        except Exception as e:
            logger.error(f"Insert failed on {account_id}: {e}")
            self._healthy[account_id] = False

            # Try next account
            result2 = self.get_collection_with_space(collection, len(data))
            if result2:
                fallback_id, fallback_client = result2
                try:
                    insert_result = await self._insert_with_retry(fallback_client, collection, data)
                    self._usage_tracker[fallback_id] = (
                        self._usage_tracker.get(fallback_id, 0) + len(data)
                    )
                    return insert_result.get("ids", []) if isinstance(insert_result, dict) else []
                except Exception as e2:
                    logger.error(f"Fallback insert also failed on {fallback_id}: {e2}")
                    self._healthy[fallback_id] = False
            else:
                await self._send_all_down_alert("insert_fallback", f"collection={collection}")

            return ids

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def _search_one_with_retry(
        self,
        account_id: str,
        collection: str,
        query_vector: list[float],
        top_k: int,
        filter_expr: str,
    ) -> list[dict]:
        """Search a single account with retry/backoff."""
        client = self._clients[account_id]
        results = client.search(
            collection_name=collection,
            data=[query_vector],
            limit=top_k,
            filter=filter_expr or None,
            output_fields=["*"],
        )
        return results[0] if results else []

    async def search(
        self,
        collection: str,
        query_vector: list[float],
        filter_expr: str = "",
        top_k: int = 10,
    ) -> list[dict]:
        """
        Search all healthy accounts in parallel, merge and deduplicate results.
        Returns top-k results by score across all accounts.
        Alerts Ghost if no healthy accounts available.
        """
        async def _search_one(account_id: str) -> list[dict]:
            try:
                return await self._search_one_with_retry(
                    account_id, collection, query_vector, top_k, filter_expr
                )
            except Exception as e:
                logger.warning(f"Search failed on {account_id}: {e}")
                self._healthy[account_id] = False
                return []

        healthy_ids = [
            aid for aid, h in self._healthy.items() if h and aid in self._clients
        ]

        if not healthy_ids:
            logger.error("No healthy Zilliz accounts for search")
            await self._send_all_down_alert("search", f"collection={collection}")
            return []

        # Search all in parallel
        tasks = [_search_one(aid) for aid in healthy_ids]
        all_results = await asyncio.gather(*tasks)

        # Merge and deduplicate by ID
        merged: dict[str, dict] = {}
        for results in all_results:
            for item in results:
                item_id = str(item.get("id", ""))
                score = item.get("distance", 0.0)

                if item_id not in merged or score > merged[item_id].get("distance", 0.0):
                    merged[item_id] = item

        # Sort by score descending and return top-k
        sorted_results = sorted(
            merged.values(),
            key=lambda x: x.get("distance", 0.0),
            reverse=True,
        )
        return sorted_results[:top_k]

    async def create_collection_if_not_exists(
        self,
        name: str,
        schema: dict[str, Any],
    ) -> None:
        """
        Create a collection on all healthy accounts if it doesn't exist.
        Idempotent — checks existence before creating.
        """
        for account_id, client in self._clients.items():
            if not self._healthy.get(account_id):
                continue

            try:
                existing = client.list_collections()
                if name not in existing:
                    client.create_collection(
                        collection_name=name,
                        schema=schema,
                    )
                    logger.info(f"Created collection '{name}' on {account_id}")
            except Exception as e:
                logger.error(f"Failed to create collection on {account_id}: {e}")

    def get_health_report(self) -> dict[str, bool]:
        """Return health status of all accounts."""
        return dict(self._healthy)
