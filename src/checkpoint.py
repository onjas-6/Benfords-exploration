"""
Checkpoint and state management with atomic operations.
Provides crash-safe persistence of processing state.
"""

import orjson
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import os


@dataclass
class ProcessingState:
    """State of the Wikipedia processing job."""

    version: int = 1
    started_at: str = ""
    total_chunks: int = 0
    completed_chunks: List[int] = None
    failed_chunks: Dict[int, Dict[str, Any]] = None
    in_progress_chunks: List[int] = None
    stats: Dict[str, int] = None

    def __post_init__(self):
        if self.completed_chunks is None:
            self.completed_chunks = []
        if self.failed_chunks is None:
            self.failed_chunks = {}
        if self.in_progress_chunks is None:
            self.in_progress_chunks = []
        if self.stats is None:
            self.stats = {"articles": 0, "numbers": 0}
        if not self.started_at:
            self.started_at = datetime.utcnow().isoformat() + "Z"


class StateManager:
    """Manages processing state with atomic file operations."""

    def __init__(self, state_path: Path):
        """
        Initialize state manager.

        Args:
            state_path: Path to state JSON file
        """
        self.state_path = state_path
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state: Optional[ProcessingState] = None

    def load(self) -> ProcessingState:
        """
        Load state from disk or create new state.

        Returns:
            ProcessingState object
        """
        if self.state_path.exists():
            try:
                with open(self.state_path, "rb") as f:
                    data = orjson.loads(f.read())
                    self._state = ProcessingState(**data)
                    return self._state
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
                print("Starting fresh...")

        # Create new state
        self._state = ProcessingState()
        return self._state

    def save(self, state: ProcessingState) -> bool:
        """
        Atomically save state to disk.

        Args:
            state: ProcessingState to save

        Returns:
            True if successful
        """
        try:
            self._state = state

            # Write to temporary file first
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=self.state_path.parent, delete=False
            ) as tmp_file:
                tmp_path = Path(tmp_file.name)
                tmp_file.write(orjson.dumps(asdict(state), option=orjson.OPT_INDENT_2))

            # Atomic rename (POSIX guarantees atomicity)
            os.replace(tmp_path, self.state_path)
            return True

        except Exception as e:
            print(f"Error saving state: {e}")
            if "tmp_path" in locals() and tmp_path.exists():
                tmp_path.unlink()
            return False

    def mark_chunk_started(self, chunk_id: int) -> bool:
        """Mark a chunk as in progress."""
        if not self._state:
            return False

        if chunk_id not in self._state.in_progress_chunks:
            self._state.in_progress_chunks.append(chunk_id)

        return self.save(self._state)

    def mark_chunk_completed(self, chunk_id: int, articles: int, numbers: int) -> bool:
        """
        Mark a chunk as completed.

        Args:
            chunk_id: Chunk identifier
            articles: Number of articles processed
            numbers: Number of numbers extracted

        Returns:
            True if successful
        """
        if not self._state:
            return False

        # Remove from in_progress
        if chunk_id in self._state.in_progress_chunks:
            self._state.in_progress_chunks.remove(chunk_id)

        # Add to completed
        if chunk_id not in self._state.completed_chunks:
            self._state.completed_chunks.append(chunk_id)

        # Remove from failed if it was there (check string key)
        if str(chunk_id) in self._state.failed_chunks:
            del self._state.failed_chunks[str(chunk_id)]

        # Update stats
        self._state.stats["articles"] += articles
        self._state.stats["numbers"] += numbers

        return self.save(self._state)

    def mark_chunk_failed(self, chunk_id: int, error: str, retries: int = 0) -> bool:
        """
        Mark a chunk as failed.

        Args:
            chunk_id: Chunk identifier
            error: Error message
            retries: Number of retry attempts

        Returns:
            True if successful
        """
        if not self._state:
            return False

        # Remove from in_progress
        if chunk_id in self._state.in_progress_chunks:
            self._state.in_progress_chunks.remove(chunk_id)

        # Add to failed (use string key for JSON serialization)
        self._state.failed_chunks[str(chunk_id)] = {
            "error": str(error),
            "retries": retries,
            "failed_at": datetime.utcnow().isoformat() + "Z",
        }

        return self.save(self._state)

    def get_pending_chunks(self) -> Set[int]:
        """Get set of chunk IDs that still need processing."""
        if not self._state:
            return set()

        all_chunks = set(range(self._state.total_chunks))
        completed = set(self._state.completed_chunks)
        return all_chunks - completed

    def get_failed_chunks(self) -> Dict[int, int]:
        """Get dict of failed chunk IDs to retry counts."""
        if not self._state:
            return {}

        return {
            int(chunk_id): info.get("retries", 0)
            for chunk_id, info in self._state.failed_chunks.items()
        }

    @property
    def state(self) -> Optional[ProcessingState]:
        """Get current state."""
        return self._state


def atomic_write_file(path: Path, data: bytes) -> bool:
    """
    Write data to a file atomically.

    Args:
        path: Target file path
        data: Data to write

    Returns:
        True if successful
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temp file
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write(data)

        # Atomic rename
        os.replace(tmp_path, path)
        return True

    except Exception as e:
        print(f"Error writing file {path}: {e}")
        if "tmp_path" in locals() and tmp_path.exists():
            tmp_path.unlink()
        return False


# Test function
if __name__ == "__main__":
    import tempfile

    # Test state management
    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = Path(tmpdir) / "test_state.json"
        manager = StateManager(state_path)

        # Create new state
        state = manager.load()
        state.total_chunks = 10
        manager.save(state)

        print("Testing checkpoint system:")
        print("-" * 60)
        print(f"✓ Created state with {state.total_chunks} chunks")

        # Mark some chunks as completed
        manager.mark_chunk_started(0)
        manager.mark_chunk_completed(0, articles=1000, numbers=15000)
        print(f"✓ Marked chunk 0 as completed")

        manager.mark_chunk_started(1)
        manager.mark_chunk_failed(1, error="Test error", retries=1)
        print(f"✓ Marked chunk 1 as failed")

        # Load state again
        manager2 = StateManager(state_path)
        state2 = manager2.load()

        print(f"✓ Reloaded state from disk")
        print(f"  Completed chunks: {state2.completed_chunks}")
        print(f"  Failed chunks: {list(state2.failed_chunks.keys())}")
        print(f"  Stats: {state2.stats}")

        pending = manager2.get_pending_chunks()
        print(f"✓ Pending chunks: {len(pending)} remaining")
