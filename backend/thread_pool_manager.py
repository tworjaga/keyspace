"""
Advanced Thread Pool Manager for Keyspace
Provides efficient multi-threading with worker monitoring, load balancing,
automatic recovery, and adaptive scaling
"""


import threading
import time
import queue
import logging
import statistics
from typing import List, Dict, Any, Callable, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, Future
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import psutil
import os

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels for priority queuing"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class TaskMetrics:
    """Metrics for a single task execution"""
    task_id: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    worker_id: Optional[int] = None
    
    @property
    def duration(self) -> float:
        """Get task duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


@dataclass
class WorkerMetrics:
    """Comprehensive metrics for a worker thread"""
    worker_id: int
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_duration: float = 0.0
    avg_task_duration: float = 0.0
    last_heartbeat: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    is_healthy: bool = True
    performance_history: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def update_performance(self, duration: float, success: bool):
        """Update worker performance metrics"""
        self.performance_history.append({
            'duration': duration,
            'success': success,
            'timestamp': time.time()
        })
        
        if success:
            self.tasks_completed += 1
            self.total_duration += duration
            self.avg_task_duration = self.total_duration / self.tasks_completed
            self.consecutive_failures = 0
        else:
            self.tasks_failed += 1
            self.consecutive_failures += 1
            
        self.last_heartbeat = time.time()
        self.is_healthy = self.consecutive_failures < 5  # Circuit breaker


@dataclass
class PoolMetrics:
    """Real-time pool performance metrics"""
    start_time: float = field(default_factory=time.time)
    tasks_submitted: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_task_duration: float = 0.0
    avg_task_duration: float = 0.0
    tasks_per_minute: float = 0.0
    success_rate: float = 1.0
    performance_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def update(self, duration: float, success: bool):
        """Update pool metrics"""
        self.tasks_completed += 1
        self.total_task_duration += duration
        
        if not success:
            self.tasks_failed += 1
            
        self.avg_task_duration = self.total_task_duration / self.tasks_completed
        self.success_rate = (self.tasks_completed - self.tasks_failed) / self.tasks_completed
        
        # Calculate tasks per minute
        uptime = time.time() - self.start_time
        if uptime > 0:
            self.tasks_per_minute = (self.tasks_completed / uptime) * 60
            
        self.performance_history.append({
            'duration': duration,
            'success': success,
            'timestamp': time.time(),
            'tasks_per_minute': self.tasks_per_minute
        })



class WorkerThread:
    """Individual worker thread with enhanced monitoring and recovery capabilities"""

    def __init__(self, worker_id: int, task_queue: queue.Queue, result_queue: queue.Queue, 
                 metrics: Optional[WorkerMetrics] = None):
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.is_active = True
        self.tasks_processed = 0
        self.start_time = time.time()
        self.last_activity = time.time()
        self.current_task = None
        self.thread = None
        self.metrics = metrics or WorkerMetrics(worker_id=worker_id)
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3


    def start(self):
        """Start the worker thread"""
        self.thread = threading.Thread(target=self._run, name=f"Worker-{self.worker_id}")
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop the worker thread"""
        self.is_active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)

    def _run(self):
        """Main worker loop with enhanced error handling and recovery"""
        while self.is_active:
            try:
                # Get task from queue with timeout
                task = self.task_queue.get(timeout=1.0)
                if task is None:  # Poison pill
                    break

                self.current_task = task
                self.last_activity = time.time()
                task_start = time.time()

                try:
                    # Process the task
                    result = self._process_task(task)
                    self.tasks_processed += 1
                    
                    # Update metrics
                    duration = time.time() - task_start
                    self.metrics.update_performance(duration, success=True)

                    # Put result in result queue
                    self.result_queue.put({
                        'worker_id': self.worker_id,
                        'task': task,
                        'result': result,
                        'timestamp': time.time(),
                        'duration': duration,
                        'success': True
                    })

                except Exception as e:
                    # Task failed - update metrics
                    duration = time.time() - task_start
                    self.metrics.update_performance(duration, success=False)
                    
                    logger.error(f"Worker {self.worker_id} task error: {e}")
                    self.result_queue.put({
                        'worker_id': self.worker_id,
                        'task': task,
                        'error': str(e),
                        'timestamp': time.time(),
                        'duration': duration,
                        'success': False
                    })
                    
                    # Check if worker should be marked unhealthy
                    if not self.metrics.is_healthy:
                        logger.warning(f"Worker {self.worker_id} marked unhealthy after {self.metrics.consecutive_failures} consecutive failures")

                self.task_queue.task_done()
                self.current_task = None
                self.recovery_attempts = 0  # Reset recovery counter on success

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {self.worker_id} critical error: {e}")
                self.recovery_attempts += 1
                
                if self.recovery_attempts >= self.max_recovery_attempts:
                    logger.error(f"Worker {self.worker_id} exceeded max recovery attempts, stopping")
                    self.is_active = False
                    break


    def _process_task(self, task: Dict[str, Any]) -> Any:
        """Process a single task"""
        task_type = task.get('type', 'password_attempt')
        data = task.get('data', {})

        if task_type == 'password_attempt':
            password = data.get('password')
            # Import here to avoid circular imports
            from .brute_force_thread import BruteForceThread

            # Create a minimal thread instance for password testing
            temp_thread = BruteForceThread(
                target="temp_target",
                attack_type="temp",
                wordlist_path="",
                min_length=1,
                max_length=1
            )
            return temp_thread.attempt_password(password)

        elif task_type == 'batch_process':
            passwords = data.get('passwords', [])
            results = []
            for password in passwords:
                # Same as above
                from .brute_force_thread import BruteForceThread
                temp_thread = BruteForceThread(
                    target="temp_target",
                    attack_type="temp",
                    wordlist_path="",
                    min_length=1,
                    max_length=1
                )
                results.append(temp_thread.attempt_password(password))
            return results

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive worker statistics"""
        return {
            'worker_id': self.worker_id,
            'tasks_processed': self.tasks_processed,
            'uptime': time.time() - self.start_time,
            'last_activity': time.time() - self.last_activity,
            'is_active': self.is_active,
            'current_task': self.current_task is not None if self.current_task else None,
            'metrics': {
                'tasks_completed': self.metrics.tasks_completed,
                'tasks_failed': self.metrics.tasks_failed,
                'avg_task_duration': self.metrics.avg_task_duration,
                'consecutive_failures': self.metrics.consecutive_failures,
                'is_healthy': self.metrics.is_healthy,
                'success_rate': (self.metrics.tasks_completed / (self.metrics.tasks_completed + self.metrics.tasks_failed)) 
                               if (self.metrics.tasks_completed + self.metrics.tasks_failed) > 0 else 1.0
            },
            'recovery_attempts': self.recovery_attempts
        }
    
    def is_stuck(self, timeout: float = 30.0) -> bool:
        """Check if worker appears stuck on a task"""
        if not self.current_task:
            return False
        return (time.time() - self.last_activity) > timeout
    
    def needs_restart(self) -> bool:
        """Check if worker needs to be restarted"""
        return not self.metrics.is_healthy or self.recovery_attempts >= self.max_recovery_attempts



class ThreadPoolManager:
    """Advanced thread pool manager with load balancing, monitoring, and automatic recovery"""

    def __init__(self, max_workers: Optional[int] = None, queue_size: int = 10000,
                 enable_recovery: bool = True, enable_adaptive_scaling: bool = True):
        """
        Initialize the thread pool manager

        Args:
            max_workers: Maximum number of worker threads (auto-detected if None)
            queue_size: Maximum size of task queue
            enable_recovery: Enable automatic thread recovery
            enable_adaptive_scaling: Enable adaptive worker scaling
        """
        self.max_workers = max_workers or self._detect_optimal_worker_count()
        self.queue_size = queue_size
        self.enable_recovery = enable_recovery
        self.enable_adaptive_scaling = enable_adaptive_scaling

        # Thread management
        self.workers: List[WorkerThread] = []
        self.worker_metrics: Dict[int, WorkerMetrics] = {}
        self.task_queue = queue.Queue(maxsize=queue_size)
        self.result_queue = queue.Queue()

        # State management
        self.is_running = False
        self.start_time = None

        # Performance monitoring
        self.pool_metrics = PoolMetrics()
        self.total_tasks_submitted = 0
        self.total_tasks_completed = 0
        self.tasks_per_second = 0
        self.last_monitoring_update = time.time()

        # Load balancing
        self.worker_loads = {}
        self.task_distribution = {}
        
        # Recovery and scaling
        self.monitoring_thread = None
        self.monitoring_interval = 5.0  # seconds
        self.adaptive_scaling_interval = 30.0  # seconds
        self.last_scaling_check = 0
        
        # Performance thresholds for adaptive scaling
        self.scale_up_threshold = 0.8  # Scale up if utilization > 80%
        self.scale_down_threshold = 0.3  # Scale down if utilization < 30%
        self.min_workers = 2
        self.max_workers_limit = 32

        logger.info(f"Initialized ThreadPoolManager with {self.max_workers} workers "
                     f"(recovery={enable_recovery}, adaptive_scaling={enable_adaptive_scaling})")


    def _detect_optimal_worker_count(self) -> int:
        """Detect optimal number of worker threads based on system resources"""
        cpu_count = psutil.cpu_count(logical=True)
        memory_gb = psutil.virtual_memory().total / (1024**3)

        # Base calculation: CPU cores * 2, but cap based on memory
        optimal = min(cpu_count * 2, int(memory_gb * 2))

        # Ensure reasonable bounds
        optimal = max(2, min(optimal, 16))

        logger.info(f"Detected optimal worker count: {optimal} (CPU: {cpu_count}, Memory: {memory_gb:.1f}GB)")
        return optimal

    def start(self):
        """Start the thread pool with monitoring"""
        if self.is_running:
            return

        self.is_running = True
        self.start_time = time.time()
        self.pool_metrics.start_time = time.time()

        # Create and start worker threads
        for i in range(self.max_workers):
            metrics = WorkerMetrics(worker_id=i)
            self.worker_metrics[i] = metrics
            worker = WorkerThread(i, self.task_queue, self.result_queue, metrics)
            worker.start()
            self.workers.append(worker)
            self.worker_loads[i] = 0

        # Start monitoring thread if recovery or adaptive scaling is enabled
        if self.enable_recovery or self.enable_adaptive_scaling:
            self._start_monitoring()

        logger.info(f"Started thread pool with {len(self.workers)} workers")
    
    def _start_monitoring(self):
        """Start the monitoring thread for recovery and scaling"""
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, 
                                                   name="PoolMonitor", daemon=True)
        self.monitoring_thread.start()
        logger.info("Started pool monitoring thread")
    
    def _monitoring_loop(self):
        """Main monitoring loop for recovery and adaptive scaling"""
        while self.is_running:
            try:
                if self.enable_recovery:
                    self._check_worker_health()
                
                if self.enable_adaptive_scaling:
                    current_time = time.time()
                    if current_time - self.last_scaling_check >= self.adaptive_scaling_interval:
                        self._adaptive_scale()
                        self.last_scaling_check = current_time
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _check_worker_health(self):
        """Check worker health and restart unhealthy workers"""
        for i, worker in enumerate(self.workers):
            if worker.needs_restart() or worker.is_stuck():
                logger.warning(f"Worker {worker.worker_id} needs restart, restarting...")
                self._restart_worker(i)
    
    def _restart_worker(self, index: int):
        """Restart a specific worker"""
        if index >= len(self.workers):
            return
            
        old_worker = self.workers[index]
        worker_id = old_worker.worker_id
        
        # Stop old worker
        old_worker.stop()
        
        # Create new worker with fresh metrics
        new_metrics = WorkerMetrics(worker_id=worker_id)
        self.worker_metrics[worker_id] = new_metrics
        new_worker = WorkerThread(worker_id, self.task_queue, self.result_queue, new_metrics)
        new_worker.start()
        
        # Replace in list
        self.workers[index] = new_worker
        
        logger.info(f"Restarted worker {worker_id}")
    
    def _adaptive_scale(self):
        """Adaptively scale worker count based on performance metrics"""
        if not self.workers:
            return
            
        # Calculate current utilization
        active_tasks = sum(1 for w in self.workers if w.current_task is not None)
        utilization = active_tasks / len(self.workers)
        
        # Calculate performance trend
        recent_tasks_per_minute = self.pool_metrics.tasks_per_minute
        
        logger.debug(f"Adaptive scaling check: utilization={utilization:.2f}, "
                    f"tasks_per_minute={recent_tasks_per_minute:.1f}, "
                    f"workers={len(self.workers)}")
        
        # Scale up if high utilization and good performance
        if utilization > self.scale_up_threshold and recent_tasks_per_minute > 100:
            target_workers = min(len(self.workers) + 2, self.max_workers_limit)
            if target_workers > len(self.workers):
                logger.info(f"Scaling up from {len(self.workers)} to {target_workers} workers")
                self.scale_workers(target_workers)
        
        # Scale down if low utilization
        elif utilization < self.scale_down_threshold and len(self.workers) > self.min_workers:
            target_workers = max(len(self.workers) - 1, self.min_workers)
            if target_workers < len(self.workers):
                logger.info(f"Scaling down from {len(self.workers)} to {target_workers} workers")
                self.scale_workers(target_workers)


    def stop(self, timeout: float = 10.0):
        """Stop the thread pool"""
        if not self.is_running:
            return

        self.is_running = False

        # Stop monitoring thread
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)

        # Send poison pills to workers
        for _ in self.workers:
            try:
                self.task_queue.put(None, timeout=1.0)
            except queue.Full:
                break

        # Stop all workers
        for worker in self.workers:
            worker.stop()

        self.workers.clear()
        self.worker_metrics.clear()
        logger.info("Stopped thread pool")


    def submit_task(self, task: Dict[str, Any], priority: TaskPriority = TaskPriority.NORMAL) -> bool:
        """Submit a task to the pool with priority"""
        if not self.is_running:
            return False

        try:
            # Add priority and timestamp to task
            task['_priority'] = priority.value
            task['_submitted_at'] = time.time()
            task['_task_id'] = f"task_{self.total_tasks_submitted}_{time.time()}"
            
            self.task_queue.put(task, timeout=5.0)
            self.total_tasks_submitted += 1
            self.pool_metrics.tasks_submitted += 1

            # Update load balancing
            worker_id = self._select_worker()
            self.worker_loads[worker_id] += 1

            return True
        except queue.Full:
            logger.warning("Task queue is full, task rejected")
            return False


    def submit_batch(self, tasks: List[Dict[str, Any]]) -> int:
        """Submit multiple tasks to the pool"""
        submitted = 0
        for task in tasks:
            if self.submit_task(task):
                submitted += 1
            else:
                break
        return submitted

    def _select_worker(self) -> int:
        """Select the least loaded worker for load balancing"""
        return min(self.worker_loads.items(), key=lambda x: x[1])[0]

    def get_results(self, timeout: float = 1.0) -> List[Dict[str, Any]]:
        """Get completed task results with metrics update"""
        results = []
        while True:
            try:
                result = self.result_queue.get(timeout=timeout)
                results.append(result)
                self.result_queue.task_done()
                self.total_tasks_completed += 1

                # Update pool metrics
                duration = result.get('duration', 0)
                success = result.get('success', False)
                self.pool_metrics.update(duration, success)

                # Update worker load
                worker_id = result.get('worker_id')
                if worker_id in self.worker_loads:
                    self.worker_loads[worker_id] = max(0, self.worker_loads[worker_id] - 1)

            except queue.Empty:
                break

        return results


    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for all tasks to complete"""
        start_time = time.time()

        while self.total_tasks_completed < self.total_tasks_submitted:
            if timeout and (time.time() - start_time) > timeout:
                return False

            time.sleep(0.1)

            # Check if all workers are still active
            active_workers = sum(1 for w in self.workers if w.is_active)
            if active_workers == 0:
                logger.error("All workers have stopped unexpectedly")
                return False

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics with enhanced metrics"""
        current_time = time.time()

        # Update performance metrics
        if self.start_time:
            uptime = current_time - self.start_time
            if uptime > 0:
                self.tasks_per_second = self.total_tasks_completed / uptime

        # Worker statistics
        worker_stats = []
        for worker in self.workers:
            worker_stats.append(worker.get_stats())

        # Queue statistics
        queue_stats = {
            'task_queue_size': self.task_queue.qsize(),
            'result_queue_size': self.result_queue.qsize(),
            'queue_capacity': self.queue_size,
            'queue_utilization': self.task_queue.qsize() / self.queue_size if self.queue_size > 0 else 0
        }

        # System resource usage
        process = psutil.Process(os.getpid())
        system_stats = {
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / (1024 * 1024),
            'threads_active': len(self.workers),
            'system_cpu_percent': psutil.cpu_percent(interval=0.1),
            'system_memory_percent': psutil.virtual_memory().percent
        }

        # Calculate performance trends
        recent_history = list(self.pool_metrics.performance_history)[-100:]
        if recent_history:
            avg_recent_duration = statistics.mean([h['duration'] for h in recent_history])
            recent_success_rate = sum([h['success'] for h in recent_history]) / len(recent_history)
        else:
            avg_recent_duration = 0
            recent_success_rate = 1.0

        return {
            'pool_stats': {
                'is_running': self.is_running,
                'max_workers': self.max_workers,
                'uptime': uptime if self.start_time else 0,
                'tasks_submitted': self.total_tasks_submitted,
                'tasks_completed': self.total_tasks_completed,
                'tasks_failed': self.pool_metrics.tasks_failed,
                'tasks_pending': self.total_tasks_submitted - self.total_tasks_completed,
                'tasks_per_second': self.tasks_per_second,
                'tasks_per_minute': self.pool_metrics.tasks_per_minute,
                'avg_task_duration': self.pool_metrics.avg_task_duration,
                'success_rate': self.pool_metrics.success_rate,
                'recent_avg_duration': avg_recent_duration,
                'recent_success_rate': recent_success_rate
            },
            'worker_stats': worker_stats,
            'queue_stats': queue_stats,
            'system_stats': system_stats,
            'load_balance': self.worker_loads.copy(),
            'features': {
                'recovery_enabled': self.enable_recovery,
                'adaptive_scaling_enabled': self.enable_adaptive_scaling
            }
        }


    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check on the thread pool"""
        issues = []
        warnings = []
        recommendations = []

        # Check worker health
        active_workers = 0
        healthy_workers = 0
        stuck_workers = 0
        
        for worker in self.workers:
            if not worker.is_active:
                issues.append(f"Worker {worker.worker_id} is not active")
            elif worker.thread and not worker.thread.is_alive():
                issues.append(f"Worker {worker.worker_id} thread is dead")
            elif not worker.metrics.is_healthy:
                warnings.append(f"Worker {worker.worker_id} is unhealthy ({worker.metrics.consecutive_failures} consecutive failures)")
            else:
                healthy_workers += 1
            
            if worker.is_stuck():
                stuck_workers += 1
                warnings.append(f"Worker {worker.worker_id} appears stuck on task")
            
            active_workers += 1

        # Worker count recommendations
        if active_workers < self.max_workers * 0.8:
            warnings.append(f"Only {active_workers}/{self.max_workers} workers are active")
            recommendations.append("Consider restarting the pool to recover workers")

        # Check queue health
        queue_utilization = self.task_queue.qsize() / self.queue_size if self.queue_size > 0 else 0
        if queue_utilization > 0.9:
            issues.append("Task queue is nearly full (90%+ utilization)")
            recommendations.append("Increase queue size or add more workers")
        elif queue_utilization > 0.7:
            warnings.append(f"Task queue is at {queue_utilization*100:.1f}% capacity")

        # Performance recommendations
        if self.pool_metrics.success_rate < 0.95:
            warnings.append(f"Success rate is low ({self.pool_metrics.success_rate*100:.1f}%)")
            recommendations.append("Check task configuration and worker health")

        if self.pool_metrics.tasks_per_minute < 100 and self.total_tasks_completed > 100:
            warnings.append(f"Performance is low ({self.pool_metrics.tasks_per_minute:.1f} tasks/minute)")
            recommendations.append("Consider scaling up workers or optimizing task processing")

        # System resource warnings
        system_memory = psutil.virtual_memory()
        if system_memory.percent > 90:
            warnings.append(f"System memory is at {system_memory.percent}%")
            recommendations.append("Consider reducing worker count or optimizing memory usage")

        return {
            'healthy': len(issues) == 0 and healthy_workers >= active_workers * 0.8,
            'status': 'healthy' if len(issues) == 0 else 'degraded' if len(warnings) > 0 else 'critical',
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'active_workers': active_workers,
            'healthy_workers': healthy_workers,
            'stuck_workers': stuck_workers,
            'queue_utilization': queue_utilization
        }


    def scale_workers(self, target_count: int):
        """Dynamically scale the number of workers"""
        target_count = max(1, min(target_count, 32))  # Reasonable bounds

        if target_count > self.max_workers:
            # Add workers
            for i in range(self.max_workers, target_count):
                worker = WorkerThread(i, self.task_queue, self.result_queue)
                worker.start()
                self.workers.append(worker)
                self.worker_loads[i] = 0

        elif target_count < self.max_workers:
            # Remove workers (stop excess workers)
            excess_count = self.max_workers - target_count
            for i in range(excess_count):
                if self.workers:
                    worker = self.workers.pop()
                    worker.stop()
                    self.worker_loads.pop(worker.worker_id, None)

        self.max_workers = target_count
        logger.info(f"Scaled worker count to {self.max_workers}")


class BatchProcessor:
    """Advanced batch processor with adaptive sizing and progress tracking"""

    def __init__(self, thread_pool: ThreadPoolManager, batch_size: int = 1000,
                 adaptive_sizing: bool = True, min_batch_size: int = 100, max_batch_size: int = 5000):
        self.thread_pool = thread_pool
        self.batch_size = batch_size
        self.adaptive_sizing = adaptive_sizing
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.pending_batches = []
        self.completed_batches = []
        self.batch_performance_history = deque(maxlen=50)
        
        # Adaptive sizing parameters
        self.target_batch_duration = 1.0  # Target 1 second per batch
        self.sizing_adjustment_factor = 0.2  # 20% adjustment per iteration
        
    def _calculate_optimal_batch_size(self) -> int:
        """Calculate optimal batch size based on performance history"""
        if not self.adaptive_sizing or len(self.batch_performance_history) < 5:
            return self.batch_size
        
        # Calculate average batch duration
        recent_durations = [b['duration'] for b in list(self.batch_performance_history)[-10:]]
        avg_duration = statistics.mean(recent_durations)
        
        # Adjust batch size based on target duration
        if avg_duration > 0:
            adjustment = (self.target_batch_duration / avg_duration - 1) * self.sizing_adjustment_factor
            new_size = int(self.batch_size * (1 + adjustment))
            
            # Clamp to bounds
            return max(self.min_batch_size, min(new_size, self.max_batch_size))
        
        return self.batch_size


    def submit_password_batch(self, passwords: List[str], priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Submit a batch of passwords for processing with adaptive sizing"""
        batch_id = f"batch_{int(time.time())}_{len(self.pending_batches)}"
        
        # Use adaptive batch size if enabled
        current_batch_size = self._calculate_optimal_batch_size()
        
        # Split into smaller chunks for workers
        chunks = [passwords[i:i + current_batch_size] for i in range(0, len(passwords), current_batch_size)]

        tasks = []
        for i, chunk in enumerate(chunks):
            task = {
                'type': 'batch_process',
                'data': {'passwords': chunk},
                'batch_id': batch_id,
                'chunk_id': i,
                'chunk_size': len(chunk),
                'total_chunks': len(chunks)
            }
            tasks.append(task)

        # Submit all tasks with priority
        submitted = 0
        for task in tasks:
            if self.thread_pool.submit_task(task, priority):
                submitted += 1

        if submitted > 0:
            self.pending_batches.append({
                'batch_id': batch_id,
                'total_passwords': len(passwords),
                'chunks': len(chunks),
                'submitted_tasks': submitted,
                'completed_tasks': 0,
                'start_time': time.time(),
                'priority': priority.name
            })

        return batch_id


    def get_batch_results(self, batch_id: str, timeout: float = 0) -> Optional[Dict[str, Any]]:
        """Get results for a specific batch with progress tracking"""
        # Get new results from thread pool
        new_results = self.thread_pool.get_results(timeout=timeout)
        
        # Update batch progress
        for result in new_results:
            result_batch_id = result.get('task', {}).get('batch_id')
            if result_batch_id:
                # Update pending batch progress
                for batch in self.pending_batches:
                    if batch['batch_id'] == result_batch_id:
                        batch['completed_tasks'] += 1
                        
                        # Track performance for adaptive sizing
                        if self.adaptive_sizing and 'duration' in result:
                            self.batch_performance_history.append({
                                'batch_id': result_batch_id,
                                'chunk_id': result.get('task', {}).get('chunk_id'),
                                'duration': result.get('duration', 0),
                                'timestamp': time.time()
                            })
        
        # Check if batch is still pending
        for batch in self.pending_batches[:]:
            if batch['batch_id'] == batch_id:
                # Check if all tasks for this batch are complete
                all_results = []
                # Get all results from thread pool that belong to this batch
                temp_results = self.thread_pool.get_results(timeout=0.1)
                for r in temp_results:
                    if r.get('task', {}).get('batch_id') == batch_id:
                        all_results.append(r)
                
                # Also check previously stored results
                for completed in self.completed_batches:
                    if completed['batch_id'] == batch_id:
                        return completed

                # If batch is complete, move to completed
                if batch['completed_tasks'] >= batch['submitted_tasks']:
                    self.pending_batches.remove(batch)
                    completion_data = {
                        'batch_id': batch_id,
                        'results': all_results,
                        'completion_time': time.time(),
                        'duration': time.time() - batch['start_time'],
                        'total_passwords': batch['total_passwords'],
                        'chunks': batch['chunks']
                    }
                    self.completed_batches.append(completion_data)
                    return completion_data
                
                # Return current progress for pending batch
                return {
                    'batch_id': batch_id,
                    'status': 'pending',
                    'progress': batch['completed_tasks'] / batch['submitted_tasks'] if batch['submitted_tasks'] > 0 else 0,
                    'completed_tasks': batch['completed_tasks'],
                    'total_tasks': batch['submitted_tasks'],
                    'elapsed_time': time.time() - batch['start_time']
                }

        # Check completed batches
        for batch in self.completed_batches:
            if batch['batch_id'] == batch_id:
                return batch

        return None


    def get_pending_batches(self) -> List[Dict[str, Any]]:
        """Get list of pending batches"""
        return self.pending_batches.copy()

    def cleanup_completed_batches(self, max_age: float = 3600):
        """Clean up old completed batches"""
        current_time = time.time()
        self.completed_batches = [
            batch for batch in self.completed_batches
            if (current_time - batch['completion_time']) < max_age
        ]
