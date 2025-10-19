#!/usr/bin/env python3
"""
State management for workflow orchestration.
Provides persistence, versioning, and recovery.
"""

import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import pickle
import base64

class WorkflowState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class PhaseState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class StateManager:
    def __init__(self, db_path: Path = Path("./state/workflows.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._initialize_db()

    def _initialize_db(self):
        """Create database schema."""
        cursor = self.conn.cursor()

        # Workflows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                metadata TEXT
            )
        ''')

        # Phases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                phase_name TEXT NOT NULL,
                phase_number INTEGER NOT NULL,
                state TEXT NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                output TEXT,
                error TEXT,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id)
            )
        ''')

        # Checkpoints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                checkpoint_name TEXT NOT NULL,
                phase_number INTEGER NOT NULL,
                state_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id)
            )
        ''')

        # State variables table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS state_vars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                var_name TEXT NOT NULL,
                var_value TEXT,
                var_type TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id),
                UNIQUE(workflow_id, var_name)
            )
        ''')

        self.conn.commit()

    def create_workflow(self, name: str, metadata: Dict = None) -> str:
        """Create a new workflow instance."""
        workflow_id = self._generate_workflow_id(name)
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO workflows (id, name, state, metadata)
            VALUES (?, ?, ?, ?)
        ''', (workflow_id, name, WorkflowState.PENDING.value,
              json.dumps(metadata) if metadata else None))

        self.conn.commit()
        return workflow_id

    def _generate_workflow_id(self, name: str) -> str:
        """Generate unique workflow ID."""
        timestamp = datetime.now().isoformat()
        content = f"{name}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def update_workflow_state(self, workflow_id: str, state: WorkflowState):
        """Update workflow state."""
        cursor = self.conn.cursor()

        completed_at = datetime.now() if state == WorkflowState.COMPLETED else None

        cursor.execute('''
            UPDATE workflows
            SET state = ?, updated_at = CURRENT_TIMESTAMP, completed_at = ?
            WHERE id = ?
        ''', (state.value, completed_at, workflow_id))

        self.conn.commit()

    def start_phase(self, workflow_id: str, phase_name: str, phase_number: int):
        """Mark a phase as started."""
        cursor = self.conn.cursor()

        # Check if phase exists
        cursor.execute('''
            SELECT id FROM phases
            WHERE workflow_id = ? AND phase_name = ?
        ''', (workflow_id, phase_name))

        result = cursor.fetchone()

        if result:
            # Update existing phase
            cursor.execute('''
                UPDATE phases
                SET state = ?, started_at = CURRENT_TIMESTAMP
                WHERE workflow_id = ? AND phase_name = ?
            ''', (PhaseState.RUNNING.value, workflow_id, phase_name))
        else:
            # Create new phase
            cursor.execute('''
                INSERT INTO phases (workflow_id, phase_name, phase_number, state, started_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (workflow_id, phase_name, phase_number, PhaseState.RUNNING.value))

        self.conn.commit()

    def complete_phase(self, workflow_id: str, phase_name: str, output: Any = None):
        """Mark a phase as completed."""
        cursor = self.conn.cursor()

        output_str = self._serialize_output(output) if output else None

        cursor.execute('''
            UPDATE phases
            SET state = ?, completed_at = CURRENT_TIMESTAMP, output = ?
            WHERE workflow_id = ? AND phase_name = ?
        ''', (PhaseState.COMPLETED.value, output_str, workflow_id, phase_name))

        self.conn.commit()

    def fail_phase(self, workflow_id: str, phase_name: str, error: str):
        """Mark a phase as failed."""
        cursor = self.conn.cursor()

        cursor.execute('''
            UPDATE phases
            SET state = ?, completed_at = CURRENT_TIMESTAMP, error = ?
            WHERE workflow_id = ? AND phase_name = ?
        ''', (PhaseState.FAILED.value, error, workflow_id, phase_name))

        self.conn.commit()

    def create_checkpoint(self, workflow_id: str, checkpoint_name: str,
                         phase_number: int, state_data: Dict):
        """Create a checkpoint."""
        cursor = self.conn.cursor()

        state_json = json.dumps(state_data, default=str)

        cursor.execute('''
            INSERT INTO checkpoints (workflow_id, checkpoint_name, phase_number, state_data)
            VALUES (?, ?, ?, ?)
        ''', (workflow_id, checkpoint_name, phase_number, state_json))

        self.conn.commit()

    def restore_checkpoint(self, workflow_id: str, checkpoint_name: Optional[str] = None) -> Dict:
        """Restore from checkpoint."""
        cursor = self.conn.cursor()

        if checkpoint_name:
            cursor.execute('''
                SELECT state_data FROM checkpoints
                WHERE workflow_id = ? AND checkpoint_name = ?
                ORDER BY created_at DESC LIMIT 1
            ''', (workflow_id, checkpoint_name))
        else:
            # Get latest checkpoint
            cursor.execute('''
                SELECT state_data FROM checkpoints
                WHERE workflow_id = ?
                ORDER BY created_at DESC LIMIT 1
            ''', (workflow_id,))

        result = cursor.fetchone()

        if result:
            return json.loads(result[0])
        return {}

    def set_state_variable(self, workflow_id: str, var_name: str,
                          var_value: Any, var_type: str = None):
        """Set a state variable."""
        cursor = self.conn.cursor()

        if var_type is None:
            var_type = type(var_value).__name__

        value_str = self._serialize_output(var_value)

        cursor.execute('''
            INSERT OR REPLACE INTO state_vars (workflow_id, var_name, var_value, var_type)
            VALUES (?, ?, ?, ?)
        ''', (workflow_id, var_name, value_str, var_type))

        self.conn.commit()

    def get_state_variable(self, workflow_id: str, var_name: str) -> Any:
        """Get a state variable."""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT var_value, var_type FROM state_vars
            WHERE workflow_id = ? AND var_name = ?
        ''', (workflow_id, var_name))

        result = cursor.fetchone()

        if result:
            return self._deserialize_output(result[0], result[1])
        return None

    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get complete workflow status."""
        cursor = self.conn.cursor()

        # Get workflow info
        cursor.execute('''
            SELECT name, state, created_at, updated_at, completed_at, metadata
            FROM workflows WHERE id = ?
        ''', (workflow_id,))

        workflow = cursor.fetchone()

        if not workflow:
            return None

        # Get phases
        cursor.execute('''
            SELECT phase_name, phase_number, state, started_at, completed_at, output, error
            FROM phases WHERE workflow_id = ?
            ORDER BY phase_number
        ''', (workflow_id,))

        phases = cursor.fetchall()

        # Get state variables
        cursor.execute('''
            SELECT var_name, var_value, var_type
            FROM state_vars WHERE workflow_id = ?
        ''', (workflow_id,))

        variables = cursor.fetchall()

        return {
            'id': workflow_id,
            'name': workflow[0],
            'state': workflow[1],
            'created_at': workflow[2],
            'updated_at': workflow[3],
            'completed_at': workflow[4],
            'metadata': json.loads(workflow[5]) if workflow[5] else None,
            'phases': [
                {
                    'name': p[0],
                    'number': p[1],
                    'state': p[2],
                    'started_at': p[3],
                    'completed_at': p[4],
                    'output': self._deserialize_output(p[5]) if p[5] else None,
                    'error': p[6]
                }
                for p in phases
            ],
            'variables': {
                v[0]: self._deserialize_output(v[1], v[2])
                for v in variables
            }
        }

    def list_workflows(self, state: Optional[WorkflowState] = None) -> List[Dict]:
        """List all workflows, optionally filtered by state."""
        cursor = self.conn.cursor()

        if state:
            cursor.execute('''
                SELECT id, name, state, created_at, updated_at
                FROM workflows WHERE state = ?
                ORDER BY updated_at DESC
            ''', (state.value,))
        else:
            cursor.execute('''
                SELECT id, name, state, created_at, updated_at
                FROM workflows
                ORDER BY updated_at DESC
            ''')

        workflows = cursor.fetchall()

        return [
            {
                'id': w[0],
                'name': w[1],
                'state': w[2],
                'created_at': w[3],
                'updated_at': w[4]
            }
            for w in workflows
        ]

    def _serialize_output(self, output: Any) -> str:
        """Serialize output for storage."""
        try:
            # Try JSON first
            return json.dumps(output, default=str)
        except:
            # Fall back to pickle for complex objects
            return base64.b64encode(pickle.dumps(output)).decode('utf-8')

    def _deserialize_output(self, output_str: str, var_type: str = None) -> Any:
        """Deserialize output from storage."""
        if not output_str:
            return None

        try:
            # Try JSON first
            return json.loads(output_str)
        except:
            try:
                # Try pickle
                return pickle.loads(base64.b64decode(output_str))
            except:
                # Return as string
                return output_str

    def cleanup_old_workflows(self, days: int = 30):
        """Clean up old completed workflows."""
        cursor = self.conn.cursor()

        cursor.execute('''
            DELETE FROM workflows
            WHERE state = ? AND completed_at < datetime('now', '-' || ? || ' days')
        ''', (WorkflowState.COMPLETED.value, days))

        self.conn.commit()

    def close(self):
        """Close database connection."""
        self.conn.close()

if __name__ == '__main__':
    # Test the state manager
    manager = StateManager()

    # Create a workflow
    workflow_id = manager.create_workflow("test_workflow", {"type": "standard"})
    print(f"Created workflow: {workflow_id}")

    # Start a phase
    manager.start_phase(workflow_id, "scan_prioritize", 1)

    # Set some state variables
    manager.set_state_variable(workflow_id, "bug_count", 5)
    manager.set_state_variable(workflow_id, "priority_queue", ["BUG-001", "BUG-002"])

    # Complete the phase
    manager.complete_phase(workflow_id, "scan_prioritize", {"items": 5})

    # Get status
    status = manager.get_workflow_status(workflow_id)
    print(json.dumps(status, indent=2, default=str))

    manager.close()
