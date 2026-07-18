import pickle
import threading
import time
from typing import Optional, Any, Iterator
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointTuple
from app.database.config import DatabaseConfig
from app.database.models import Checkpoint as CheckpointModel, CheckpointWrite as CheckpointWriteModel


_thread_locks: dict[str, threading.RLock] = {}
_thread_locks_guard = threading.Lock()

MAX_CONCURRENCY_RETRIES = 3


def _lock_for(thread_id: str) -> threading.RLock:
    with _thread_locks_guard:
        lock = _thread_locks.get(thread_id)
        if lock is None:
            lock = threading.RLock()
            _thread_locks[thread_id] = lock
        return lock


class SQLiteCheckpointSaver(BaseCheckpointSaver):
    def __init__(self):
        super().__init__()
        self.session_factory = DatabaseConfig.get_session_factory()

    def _run(self, thread_id: str, fn):
        lock = _lock_for(thread_id)
        last_exc = None
        for attempt in range(MAX_CONCURRENCY_RETRIES):
            session = self.session_factory()
            try:
                with lock:
                    result = fn(session)
                    session.commit()
                    return result
            except SQLAlchemyError as e:
                try:
                    session.rollback()
                except Exception:
                    pass
                last_exc = e
                time.sleep(0.05 * (attempt + 1))
                continue
            finally:
                session.close()
        raise last_exc

    def put(self, config: dict, checkpoint: Checkpoint, metadata: dict, new_versions: dict) -> dict:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = checkpoint.get("parent_id")

        def _op(session):
            checkpoint_blob = pickle.dumps(checkpoint)
            metadata_blob = pickle.dumps(metadata)

            existing = session.query(CheckpointModel).filter_by(
                thread_id=thread_id,
                checkpoint_ns=checkpoint_ns,
                checkpoint_id=checkpoint_id
            ).first()

            if existing:
                existing.parent_checkpoint_id = parent_checkpoint_id
                existing.type = checkpoint.get("type")
                existing.checkpoint = checkpoint_blob
                existing.meta = metadata_blob
            else:
                session.add(CheckpointModel(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns,
                    checkpoint_id=checkpoint_id,
                    parent_checkpoint_id=parent_checkpoint_id,
                    type=checkpoint.get("type"),
                    checkpoint=checkpoint_blob,
                    meta=metadata_blob
                ))

            return {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id
                }
            }

        return self._run(thread_id, _op)

    def put_writes(self, config: dict, writes: list, task_id: str) -> None:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"]["checkpoint_id"]

        def _op(session):
            checkpoint_exists = session.query(CheckpointModel).filter_by(
                thread_id=thread_id,
                checkpoint_ns=checkpoint_ns,
                checkpoint_id=checkpoint_id
            ).first()

            if not checkpoint_exists:
                placeholder_checkpoint = {
                    "id": checkpoint_id,
                    "v": 1,
                    "ts": "",
                    "channel_values": {},
                    "channel_versions": {},
                    "versions_seen": {}
                }
                session.add(CheckpointModel(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns,
                    checkpoint_id=checkpoint_id,
                    parent_checkpoint_id=None,
                    type=None,
                    checkpoint=pickle.dumps(placeholder_checkpoint),
                    meta=pickle.dumps({})
                ))
                session.flush()

            with session.no_autoflush:
                for idx, (channel, value) in enumerate(writes):
                    value_blob = pickle.dumps(value)

                    existing = session.query(CheckpointWriteModel).filter_by(
                        thread_id=thread_id,
                        checkpoint_ns=checkpoint_ns,
                        checkpoint_id=checkpoint_id,
                        task_id=task_id,
                        idx=idx
                    ).first()

                    if existing:
                        existing.type = type(value).__name__
                        existing.value = value_blob
                    else:
                        session.add(CheckpointWriteModel(
                            thread_id=thread_id,
                            checkpoint_ns=checkpoint_ns,
                            checkpoint_id=checkpoint_id,
                            task_id=task_id,
                            idx=idx,
                            channel=channel,
                            type=type(value).__name__,
                            value=value_blob
                        ))

        self._run(thread_id, _op)

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"].get("checkpoint_id")

        session = self.session_factory()
        try:
            if checkpoint_id:
                result = session.query(CheckpointModel).filter_by(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns,
                    checkpoint_id=checkpoint_id
                ).first()
            else:
                result = session.query(CheckpointModel).filter_by(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns
                ).order_by(CheckpointModel.checkpoint_id.desc()).first()

            if result:
                checkpoint = pickle.loads(result.checkpoint)
                metadata = pickle.loads(result.meta)
                config_with_id = {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": checkpoint["id"] if not checkpoint_id else checkpoint_id
                    }
                }
                return CheckpointTuple(
                    config=config_with_id,
                    checkpoint=checkpoint,
                    metadata=metadata,
                    parent_config=None
                )
            return None
        finally:
            session.close()

    def get(self, config: dict) -> Optional[Checkpoint]:
        result = self.get_tuple(config)
        if result:
            return result.checkpoint
        return None

    def list(self, config: Optional[dict] = None) -> Iterator[CheckpointTuple]:
        session = self.session_factory()
        try:
            query = session.query(CheckpointModel)

            if config and "thread_id" in config.get("configurable", {}):
                thread_id = config["configurable"]["thread_id"]
                checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
                query = query.filter_by(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns
                ).order_by(CheckpointModel.checkpoint_id.desc())
            else:
                query = query.order_by(
                    CheckpointModel.thread_id,
                    CheckpointModel.checkpoint_id.desc()
                )

            for result in query:
                checkpoint = pickle.loads(result.checkpoint)
                metadata = pickle.loads(result.meta)
                config_dict = {
                    "configurable": {
                        "thread_id": result.thread_id,
                        "checkpoint_ns": result.checkpoint_ns,
                        "checkpoint_id": result.checkpoint_id
                    }
                }
                yield CheckpointTuple(
                    config=config_dict,
                    checkpoint=checkpoint,
                    metadata=metadata,
                    parent_config=None
                )
        finally:
            session.close()
