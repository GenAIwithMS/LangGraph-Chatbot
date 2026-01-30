import pickle
from typing import Optional, Any, Iterator, NamedTuple
from sqlalchemy import select
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointTuple
from database.config import DatabaseConfig
from database.models import Checkpoint as CheckpointModel, CheckpointWrite as CheckpointWriteModel


class MySQLCheckpointSaver(BaseCheckpointSaver):
    """SQLAlchemy-based checkpoint saver for LangGraph"""
    
    def __init__(self):
        """Initialize MySQL checkpoint saver with SQLAlchemy"""
        super().__init__()
        self.session_factory = DatabaseConfig.get_session_factory()
    
    def put(self, config: dict, checkpoint: Checkpoint, metadata: dict, new_versions: dict) -> dict:
        """Save a checkpoint to MySQL using SQLAlchemy"""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = checkpoint.get("parent_id")
        
        session = self.session_factory()
        try:
            # Serialize checkpoint and metadata
            checkpoint_blob = pickle.dumps(checkpoint)
            metadata_blob = pickle.dumps(metadata)
            
            # Check if checkpoint exists
            existing = session.query(CheckpointModel).filter_by(
                thread_id=thread_id,
                checkpoint_ns=checkpoint_ns,
                checkpoint_id=checkpoint_id
            ).first()
            
            if existing:
                # Update existing checkpoint
                existing.parent_checkpoint_id = parent_checkpoint_id
                existing.type = checkpoint.get("type")
                existing.checkpoint = checkpoint_blob
                existing.meta = metadata_blob
            else:
                # Insert new checkpoint
                new_checkpoint = CheckpointModel(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns,
                    checkpoint_id=checkpoint_id,
                    parent_checkpoint_id=parent_checkpoint_id,
                    type=checkpoint.get("type"),
                    checkpoint=checkpoint_blob,
                    meta=metadata_blob
                )
                session.add(new_checkpoint)
            
            session.commit()
            
            return {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id
                }
            }
        finally:
            session.close()
    
    def put_writes(self, config: dict, writes: list, task_id: str) -> None:
        """Save checkpoint writes to MySQL using SQLAlchemy"""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"]["checkpoint_id"]
        
        session = self.session_factory()
        try:
            for idx, (channel, value) in enumerate(writes):
                value_blob = pickle.dumps(value)
                
                # Check if write exists
                existing = session.query(CheckpointWriteModel).filter_by(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns,
                    checkpoint_id=checkpoint_id,
                    task_id=task_id,
                    idx=idx
                ).first()
                
                if existing:
                    # Update existing write
                    existing.type = type(value).__name__
                    existing.value = value_blob
                else:
                    # Insert new write
                    new_write = CheckpointWriteModel(
                        thread_id=thread_id,
                        checkpoint_ns=checkpoint_ns,
                        checkpoint_id=checkpoint_id,
                        task_id=task_id,
                        idx=idx,
                        channel=channel,
                        type=type(value).__name__,
                        value=value_blob
                    )
                    session.add(new_write)
            
            session.commit()
        finally:
            session.close()
    
    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple from MySQL using SQLAlchemy"""
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
        """Get a checkpoint from MySQL (convenience method)"""
        result = self.get_tuple(config)
        if result:
            return result[1]  # Return just the checkpoint
        return None
    
    def list(self, config: Optional[dict] = None) -> Iterator[CheckpointTuple]:
        """List all checkpoints, optionally filtered by config"""
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
