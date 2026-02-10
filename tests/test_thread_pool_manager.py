"""
Comprehensive tests for ThreadPoolManager with enhanced monitoring and recovery
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock
from backend.thread_pool_manager import (
    ThreadPoolManager, WorkerThread, BatchProcessor,
    TaskPriority, WorkerMetrics, PoolMetrics
)


class TestWorkerMetrics:
    """Test WorkerMetrics dataclass"""

    def test_initialization(self):
        """Test WorkerMetrics initialization"""
        metrics = WorkerMetrics(worker_id=1)
        assert metrics.worker_id == 1
        assert metrics.tasks_completed == 0
        assert metrics.tasks_failed == 0
        assert metrics.is_healthy is True
        assert metrics.consecutive_failures == 0

    def test_update_performance_success(self):
        """Test updating metrics with successful task"""
        metrics = WorkerMetrics(worker_id=1)
        metrics.update_performance(duration=0.5, success=True)
        
        assert metrics.tasks_completed == 1
        assert metrics.tasks_failed == 0
        assert metrics.avg_task_duration == 0.5
        assert metrics.consecutive_failures == 0
        assert metrics.is_healthy is True

    def test_update_performance_failure(self):
        """Test updating metrics with failed task"""
        metrics = WorkerMetrics(worker_id=1)
        
        # Add 4 failures
        for i in range(4):
            metrics.update_performance(duration=0.1, success=False)
        
        assert metrics.tasks_completed == 0
        assert metrics.tasks_failed == 4
        assert metrics.consecutive_failures == 4
        assert metrics.is_healthy is True  # Still healthy (under 5)
        
        # Add 5th failure - should become unhealthy
        metrics.update_performance(duration=0.1, success=False)
        assert metrics.consecutive_failures == 5
        assert metrics.is_healthy is False  # Circuit breaker triggered

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        metrics = WorkerMetrics(worker_id=1)
        
        # 8 successes, 2 failures
        for _ in range(8):
            metrics.update_performance(duration=0.1, success=True)
        for _ in range(2):
            metrics.update_performance(duration=0.1, success=False)
        
        expected_rate = 8 / 10
        actual_rate = metrics.tasks_completed / (metrics.tasks_completed + metrics.tasks_failed)
        assert actual_rate == expected_rate


class TestPoolMetrics:
    """Test PoolMetrics dataclass"""

    def test_initialization(self):
        """Test PoolMetrics initialization"""
        metrics = PoolMetrics()
        assert metrics.tasks_completed == 0
        assert metrics.tasks_failed == 0
        assert metrics.success_rate == 1.0
        assert metrics.tasks_per_minute == 0.0

    def test_update_success(self):
        """Test updating with successful task"""
        metrics = PoolMetrics()
        metrics.update(duration=0.5, success=True)
        
        assert metrics.tasks_completed == 1
        assert metrics.tasks_failed == 0
        assert metrics.avg_task_duration == 0.5
        assert metrics.success_rate == 1.0

    def test_update_failure(self):
        """Test updating with failed task"""
        metrics = PoolMetrics()
        
        # 3 successes, 1 failure
        for _ in range(3):
            metrics.update(duration=0.5, success=True)
        metrics.update(duration=0.5, success=False)
        
        assert metrics.tasks_completed == 4
        assert metrics.tasks_failed == 1
        assert metrics.success_rate == 0.75

    def test_tasks_per_minute_calculation(self):
        """Test tasks per minute calculation"""
        metrics = PoolMetrics()
        metrics.start_time = time.time() - 60  # 1 minute ago
        
        for _ in range(100):
            metrics.update(duration=0.1, success=True)
        
        # Should be approximately 100 tasks per minute
        assert metrics.tasks_per_minute > 90  # Allow some tolerance


class TestWorkerThread:
    """Test WorkerThread class"""

    def test_initialization(self):
        """Test WorkerThread initialization"""
        task_queue = MagicMock()
        result_queue = MagicMock()
        worker = WorkerThread(1, task_queue, result_queue)
        
        assert worker.worker_id == 1
        assert worker.is_active is True
        assert worker.tasks_processed == 0
        assert worker.current_task is None
        assert worker.recovery_attempts == 0

    def test_get_stats(self):
        """Test get_stats method"""
        task_queue = MagicMock()
        result_queue = MagicMock()
        worker = WorkerThread(1, task_queue, result_queue)
        
        stats = worker.get_stats()
        assert stats['worker_id'] == 1
        assert stats['is_active'] is True
        assert 'metrics' in stats
        assert 'recovery_attempts' in stats

    def test_is_stuck_no_task(self):
        """Test is_stuck when no current task"""
        task_queue = MagicMock()
        result_queue = MagicMock()
        worker = WorkerThread(1, task_queue, result_queue)
        
        assert worker.is_stuck() is False

    def test_needs_restart_healthy(self):
        """Test needs_restart when healthy"""
        task_queue = MagicMock()
        result_queue = MagicMock()
        worker = WorkerThread(1, task_queue, result_queue)
        
        assert worker.needs_restart() is False

    def test_needs_restart_unhealthy(self):
        """Test needs_restart when unhealthy"""
        task_queue = MagicMock()
        result_queue = MagicMock()
        worker = WorkerThread(1, task_queue, result_queue)
        
        # Make worker unhealthy
        for _ in range(5):
            worker.metrics.update_performance(0.1, success=False)
        
        assert worker.needs_restart() is True


class TestThreadPoolManager:
    """Test ThreadPoolManager class"""

    def test_initialization(self):
        """Test ThreadPoolManager initialization"""
        pool = ThreadPoolManager(max_workers=4, queue_size=1000)
        
        assert pool.max_workers == 4
        assert pool.queue_size == 1000
        assert pool.enable_recovery is True
        assert pool.enable_adaptive_scaling is True
        assert pool.is_running is False

    def test_initialization_default_workers(self):
        """Test auto-detection of worker count"""
        pool = ThreadPoolManager()
        
        # Should auto-detect between 2 and 16 workers
        assert 2 <= pool.max_workers <= 16

    def test_start_stop(self):
        """Test starting and stopping the pool"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        
        # Start pool
        pool.start()
        assert pool.is_running is True
        assert len(pool.workers) == 2
        
        # Stop pool
        pool.stop()
        assert pool.is_running is False
        assert len(pool.workers) == 0

    def test_submit_task(self):
        """Test task submission"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        pool.start()
        
        task = {'type': 'test', 'data': {'value': 1}}
        result = pool.submit_task(task)
        
        assert result is True
        assert pool.total_tasks_submitted == 1
        
        pool.stop()

    def test_submit_task_not_running(self):
        """Test task submission when not running"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        # Don't start the pool
        
        task = {'type': 'test', 'data': {'value': 1}}
        result = pool.submit_task(task)
        
        assert result is False

    def test_submit_task_with_priority(self):
        """Test task submission with priority"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        pool.start()
        
        task = {'type': 'test', 'data': {'value': 1}}
        result = pool.submit_task(task, priority=TaskPriority.HIGH)
        
        assert result is True
        assert '_priority' in task
        assert task['_priority'] == TaskPriority.HIGH.value
        
        pool.stop()

    def test_submit_batch(self):
        """Test batch task submission"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        pool.start()
        
        tasks = [
            {'type': 'test', 'data': {'value': i}}
            for i in range(5)
        ]
        submitted = pool.submit_batch(tasks)
        
        assert submitted == 5
        assert pool.total_tasks_submitted == 5
        
        pool.stop()

    def test_get_stats(self):
        """Test getting pool statistics"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        pool.start()
        
        stats = pool.get_stats()
        
        assert 'pool_stats' in stats
        assert 'worker_stats' in stats
        assert 'queue_stats' in stats
        assert 'system_stats' in stats
        assert 'features' in stats
        
        pool.stop()

    def test_health_check_healthy(self):
        """Test health check on healthy pool"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        pool.start()
        
        health = pool.health_check()
        
        assert health['healthy'] is True
        assert health['status'] == 'healthy'
        assert health['active_workers'] == 2
        
        pool.stop()

    def test_scale_workers_up(self):
        """Test scaling workers up"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        pool.start()
        
        initial_count = len(pool.workers)
        pool.scale_workers(4)
        
        assert len(pool.workers) == 4
        assert pool.max_workers == 4
        
        pool.stop()

    def test_scale_workers_down(self):
        """Test scaling workers down"""
        pool = ThreadPoolManager(max_workers=4, queue_size=100)
        pool.start()
        
        pool.scale_workers(2)
        
        # Allow for some tolerance in worker count due to timing
        assert len(pool.workers) <= 2
        assert pool.max_workers == 2
        
        pool.stop()

    def test_adaptive_scaling_disabled(self):
        """Test pool without adaptive scaling"""
        pool = ThreadPoolManager(
            max_workers=2,
            queue_size=100,
            enable_recovery=False,
            enable_adaptive_scaling=False
        )
        pool.start()
        
        assert pool.monitoring_thread is None
        
        pool.stop()


class TestBatchProcessor:
    """Test BatchProcessor class"""

    def test_initialization(self):
        """Test BatchProcessor initialization"""
        pool = MagicMock()
        processor = BatchProcessor(pool, batch_size=500)
        
        assert processor.batch_size == 500
        assert processor.adaptive_sizing is True
        assert processor.min_batch_size == 100
        assert processor.max_batch_size == 5000

    def test_calculate_optimal_batch_size_no_history(self):
        """Test batch size calculation without history"""
        pool = MagicMock()
        processor = BatchProcessor(pool, batch_size=500)
        
        size = processor._calculate_optimal_batch_size()
        assert size == 500  # Returns default when no history

    def test_submit_password_batch(self):
        """Test submitting password batch"""
        pool = MagicMock()
        pool.submit_task.return_value = True
        processor = BatchProcessor(pool, batch_size=10)
        
        passwords = [f"pass{i}" for i in range(25)]
        batch_id = processor.submit_password_batch(passwords)
        
        assert batch_id is not None
        assert len(processor.pending_batches) == 1
        assert processor.pending_batches[0]['total_passwords'] == 25

    def test_get_batch_results_pending(self):
        """Test getting results for pending batch"""
        pool = MagicMock()
        pool.get_results.return_value = []
        processor = BatchProcessor(pool, batch_size=10)
        
        # Add a pending batch
        processor.pending_batches.append({
            'batch_id': 'test_batch',
            'total_passwords': 10,
            'chunks': 1,
            'submitted_tasks': 1,
            'completed_tasks': 0,
            'start_time': time.time()
        })
        
        result = processor.get_batch_results('test_batch')
        
        assert result is not None
        assert result['status'] == 'pending'
        assert 'progress' in result

    def test_cleanup_completed_batches(self):
        """Test cleaning up old completed batches"""
        pool = MagicMock()
        processor = BatchProcessor(pool, batch_size=10)
        
        # Add old completed batch
        processor.completed_batches.append({
            'batch_id': 'old_batch',
            'completion_time': time.time() - 7200  # 2 hours ago
        })
        
        # Add recent completed batch
        processor.completed_batches.append({
            'batch_id': 'recent_batch',
            'completion_time': time.time() - 1800  # 30 minutes ago
        })
        
        processor.cleanup_completed_batches(max_age=3600)  # 1 hour max age
        
        assert len(processor.completed_batches) == 1
        assert processor.completed_batches[0]['batch_id'] == 'recent_batch'


class TestTaskPriority:
    """Test TaskPriority enum"""

    def test_priority_values(self):
        """Test priority value ordering"""
        assert TaskPriority.CRITICAL.value == 0
        assert TaskPriority.HIGH.value == 1
        assert TaskPriority.NORMAL.value == 2
        assert TaskPriority.LOW.value == 3
        assert TaskPriority.BACKGROUND.value == 4

    def test_priority_comparison(self):
        """Test priority comparison"""
        assert TaskPriority.CRITICAL.value < TaskPriority.HIGH.value
        assert TaskPriority.HIGH.value < TaskPriority.NORMAL.value


class TestIntegration:
    """Integration tests for the complete system"""

    def test_full_workflow(self):
        """Test complete workflow from start to finish"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        pool.start()
        
        # Submit some tasks
        for i in range(10):
            task = {
                'type': 'password_attempt',
                'data': {'password': f'test{i}'}
            }
            pool.submit_task(task, priority=TaskPriority.NORMAL)
        
        # Wait a bit for processing
        time.sleep(0.5)
        
        # Get results
        results = pool.get_results(timeout=0.5)
        
        # Check stats
        stats = pool.get_stats()
        assert stats['pool_stats']['tasks_submitted'] == 10
        
        # Health check
        health = pool.health_check()
        assert 'healthy' in health
        
        pool.stop()

    def test_batch_processing_workflow(self):
        """Test batch processing workflow"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        pool.start()
        
        processor = BatchProcessor(pool, batch_size=5)
        
        # Submit batch
        passwords = [f"password{i}" for i in range(20)]
        batch_id = processor.submit_password_batch(passwords, priority=TaskPriority.HIGH)
        
        # Check batch was created
        assert len(processor.pending_batches) == 1
        
        # Get results (will be pending initially)
        result = processor.get_batch_results(batch_id)
        assert result is not None
        
        pool.stop()

    def test_recovery_mechanism(self):
        """Test automatic recovery mechanism"""
        pool = ThreadPoolManager(
            max_workers=2,
            queue_size=100,
            enable_recovery=True,
            enable_adaptive_scaling=False
        )
        pool.start()
        
        # Verify monitoring thread started
        assert pool.monitoring_thread is not None
        assert pool.monitoring_thread.is_alive()
        
        pool.stop()

    def test_performance_metrics_tracking(self):
        """Test that performance metrics are tracked correctly"""
        pool = ThreadPoolManager(max_workers=2, queue_size=100)
        pool.start()
        
        # Submit and process tasks
        for i in range(5):
            task = {'type': 'test', 'data': {'value': i}}
            pool.submit_task(task)
        
        # Wait for processing
        time.sleep(0.3)
        
        # Get results to trigger metrics update
        pool.get_results(timeout=0.5)
        
        # Check metrics were updated
        assert pool.pool_metrics.tasks_completed > 0
        
        pool.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
