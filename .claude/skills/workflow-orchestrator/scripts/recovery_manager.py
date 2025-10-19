#!/usr/bin/env python3
"""
Recovery management for failed workflows.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecoveryManager:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.recovery_strategies = {
            'retry': self._retry_strategy,
            'rollback': self._rollback_strategy,
            'skip': self._skip_strategy,
            'manual': self._manual_strategy
        }

    def analyze_failure(self, workflow_id: str, phase_name: str) -> Dict:
        """Analyze failure and recommend recovery strategy."""
        status = self.state_manager.get_workflow_status(workflow_id)

        if not status:
            return {'strategy': 'manual', 'reason': 'Workflow not found'}

        # Find the failed phase
        failed_phase = None
        for phase in status['phases']:
            if phase['name'] == phase_name and phase['state'] == 'failed':
                failed_phase = phase
                break

        if not failed_phase:
            return {'strategy': 'manual', 'reason': 'Failed phase not found'}

        # Analyze error type
        error = failed_phase.get('error', '')

        # Determine strategy based on error patterns
        if 'timeout' in error.lower():
            return {
                'strategy': 'retry',
                'reason': 'Timeout error - may be transient',
                'params': {'increase_timeout': True}
            }
        elif 'permission denied' in error.lower():
            return {
                'strategy': 'manual',
                'reason': 'Permission error - requires manual intervention'
            }
        elif 'network' in error.lower() or 'connection' in error.lower():
            return {
                'strategy': 'retry',
                'reason': 'Network error - likely transient',
                'params': {'wait_time': 60}
            }
        elif 'conflict' in error.lower():
            return {
                'strategy': 'rollback',
                'reason': 'Conflict detected - rollback recommended'
            }
        else:
            # Check if this phase has failed multiple times
            failure_count = self._count_phase_failures(workflow_id, phase_name)

            if failure_count > 3:
                return {
                    'strategy': 'skip',
                    'reason': f'Phase has failed {failure_count} times',
                    'params': {'create_issue': True}
                }
            else:
                return {
                    'strategy': 'retry',
                    'reason': 'Generic failure - retry recommended'
                }

    def _count_phase_failures(self, workflow_id: str, phase_name: str) -> int:
        """Count how many times a phase has failed."""
        # This would query the database for historical failures
        # For now, return a placeholder
        return 1

    def recover_workflow(self, workflow_id: str, phase_name: str,
                        strategy: Optional[str] = None) -> Dict:
        """Execute recovery strategy for failed workflow."""
        if not strategy:
            # Auto-detect strategy
            analysis = self.analyze_failure(workflow_id, phase_name)
            strategy = analysis['strategy']
            logger.info(f"Auto-detected recovery strategy: {strategy}")

        if strategy not in self.recovery_strategies:
            return {
                'success': False,
                'error': f'Unknown recovery strategy: {strategy}'
            }

        # Execute recovery strategy
        recovery_func = self.recovery_strategies[strategy]
        return recovery_func(workflow_id, phase_name)

    def _retry_strategy(self, workflow_id: str, phase_name: str) -> Dict:
        """Retry the failed phase."""
        logger.info(f"Retrying phase {phase_name} in workflow {workflow_id}")

        # Reset phase state to pending
        # This would trigger re-execution in the orchestrator

        return {
            'success': True,
            'action': 'retry',
            'message': f'Phase {phase_name} queued for retry'
        }

    def _rollback_strategy(self, workflow_id: str, phase_name: str) -> Dict:
        """Rollback to previous checkpoint."""
        logger.info(f"Rolling back workflow {workflow_id}")

        # Find latest checkpoint before failed phase
        checkpoints = self._get_checkpoints_before_phase(workflow_id, phase_name)

        if not checkpoints:
            return {
                'success': False,
                'error': 'No checkpoint found for rollback'
            }

        # Restore from checkpoint
        latest_checkpoint = checkpoints[0]
        state = self.state_manager.restore_checkpoint(
            workflow_id, latest_checkpoint['name']
        )

        # Update workflow state
        from state_manager import WorkflowState
        self.state_manager.update_workflow_state(
            workflow_id, WorkflowState.ROLLED_BACK
        )

        return {
            'success': True,
            'action': 'rollback',
            'checkpoint': latest_checkpoint['name'],
            'message': f'Rolled back to checkpoint {latest_checkpoint["name"]}'
        }

    def _skip_strategy(self, workflow_id: str, phase_name: str) -> Dict:
        """Skip the failed phase."""
        logger.info(f"Skipping phase {phase_name} in workflow {workflow_id}")

        # Mark phase as skipped
        # This would allow the workflow to continue

        return {
            'success': True,
            'action': 'skip',
            'message': f'Phase {phase_name} skipped',
            'warning': 'Manual verification may be required'
        }

    def _manual_strategy(self, workflow_id: str, phase_name: str) -> Dict:
        """Request manual intervention."""
        logger.info(f"Manual intervention required for {phase_name} in workflow {workflow_id}")

        # Create manual intervention request
        self._create_intervention_request(workflow_id, phase_name)

        return {
            'success': True,
            'action': 'manual',
            'message': 'Manual intervention requested',
            'next_steps': [
                'Review the error in the workflow logs',
                'Resolve the issue manually',
                'Resume the workflow using the resume command'
            ]
        }

    def _get_checkpoints_before_phase(self, workflow_id: str, phase_name: str) -> List[Dict]:
        """Get all checkpoints created before a specific phase."""
        # This would query the database
        # For now, return a placeholder
        return [{'name': 'phase_1_checkpoint'}]

    def _create_intervention_request(self, workflow_id: str, phase_name: str):
        """Create a request for manual intervention."""
        request = {
            'workflow_id': workflow_id,
            'phase_name': phase_name,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }

        # Save to human-actions directory
        request_file = Path(f"./human-actions/intervention_{workflow_id}_{phase_name}.json")
        request_file.parent.mkdir(parents=True, exist_ok=True)

        with open(request_file, 'w') as f:
            json.dump(request, f, indent=2)

        logger.info(f"Intervention request created: {request_file}")
