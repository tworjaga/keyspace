#!/usr/bin/env python3
"""
Performance Benchmarking Script for Keyspace
Tests various attack types and measures performance metrics
"""

import sys
import time
import psutil
import os
import json
from pathlib import Path
from datetime import datetime
import threading
import gc
from typing import Dict, List, Any, Optional
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.brute_force_thread import BruteForceThread


class PerformanceBenchmark:
    """Comprehensive performance benchmarking for Keyspace"""

    def __init__(self, output_dir: str = "benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Benchmark configuration
        self.test_configs = {
            "dictionary_attack": {
                "attack_type": "Dictionary Attack (WPA2)",
                "wordlist_path": self._create_test_wordlist(1000),
                "min_length": 6,
                "max_length": 12,
                "charset": "abcdefghijklmnopqrstuvwxyz",
                "duration_limit": 30  # seconds
            },
            "brute_force_small": {
                "attack_type": "Brute Force Attack",
                "wordlist_path": "",
                "min_length": 4,
                "max_length": 6,
                "charset": "abcdefghijklmnopqrstuvwxyz",
                "duration_limit": 30
            },
            "brute_force_medium": {
                "attack_type": "Brute Force Attack",
                "wordlist_path": "",
                "min_length": 6,
                "max_length": 8,
                "charset": "abcdefghijklmnopqrstuvwxyz0123456789",
                "duration_limit": 60
            },
            "rule_based_attack": {
                "attack_type": "Rule-based Attack",
                "wordlist_path": self._create_test_wordlist(500),
                "min_length": 6,
                "max_length": 12,
                "charset": "abcdefghijklmnopqrstuvwxyz0123456789!@#$",
                "duration_limit": 45
            },
            "hybrid_attack": {
                "attack_type": "Hybrid Attack",
                "wordlist_path": self._create_test_wordlist(300),
                "min_length": 8,
                "max_length": 12,
                "charset": "abcdefghijklmnopqrstuvwxyz0123456789",
                "duration_limit": 45
            },
            "mask_attack": {
                "attack_type": "Mask Attack",
                "wordlist_path": "",
                "min_length": 8,
                "max_length": 12,
                "charset": "abcdefghijklmnopqrstuvwxyz0123456789!@#$",
                "duration_limit": 30
            },
            "combinator_attack": {
                "attack_type": "Combinator Attack",
                "wordlist_path": self._create_test_wordlist(200),
                "min_length": 6,
                "max_length": 10,
                "charset": "abcdefghijklmnopqrstuvwxyz",
                "duration_limit": 30
            },
            "pin_attack": {
                "attack_type": "Pin Code Attack",
                "wordlist_path": "",
                "min_length": 4,
                "max_length": 6,
                "charset": "0123456789",
                "duration_limit": 20
            }
        }

        self.results = {}
        self.system_info = self._get_system_info()

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmark context"""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "platform": sys.platform,
            "python_version": sys.version,
            "timestamp": datetime.now().isoformat()
        }

    def _create_test_wordlist(self, size: int) -> str:
        """Create a test wordlist file with specified number of entries"""
        wordlist_path = self.output_dir / f"test_wordlist_{size}.txt"

        if wordlist_path.exists():
            return str(wordlist_path)

        # Generate test words
        words = []
        import string
        import random

        charset = string.ascii_lowercase
        for i in range(size):
            length = random.randint(4, 10)
            word = ''.join(random.choices(charset, k=length))
            words.append(word)

        # Write to file
        with open(wordlist_path, 'w') as f:
            f.write('\n'.join(words))

        return str(wordlist_path)

    def _monitor_performance(self, process: psutil.Process, duration: float) -> Dict[str, Any]:
        """Monitor performance metrics during benchmark"""
        start_time = time.time()
        cpu_percentages = []
        memory_usages = []
        disk_ios = []

        while time.time() - start_time < duration:
            try:
                cpu_percentages.append(process.cpu_percent(interval=0.1))
                memory_usages.append(process.memory_info().rss)
                disk_ios.append(process.io_counters())
                time.sleep(0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

        return {
            "cpu_avg": sum(cpu_percentages) / len(cpu_percentages) if cpu_percentages else 0,
            "cpu_max": max(cpu_percentages) if cpu_percentages else 0,
            "memory_avg": sum(memory_usages) / len(memory_usages) if memory_usages else 0,
            "memory_max": max(memory_usages) if memory_usages else 0,
            "memory_peak_mb": (max(memory_usages) / 1024 / 1024) if memory_usages else 0,
            "monitoring_duration": duration
        }

    def run_single_benchmark(self, config_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single benchmark test"""
        print(f"\n[*] Running benchmark: {config_name}")
        print(f"   Attack Type: {config['attack_type']}")
        print(f"   Duration Limit: {config['duration_limit']}s")

        # Create attack thread
        attack_thread = BruteForceThread(
            target="benchmark_target",  # Non-existent target for testing
            attack_type=config["attack_type"],
            wordlist_path=config["wordlist_path"],
            min_length=config["min_length"],
            max_length=config["max_length"],
            charset=config["charset"]
        )

        # Start performance monitoring
        current_process = psutil.Process()
        monitor_thread = threading.Thread(
            target=self._monitor_performance,
            args=(current_process, config["duration_limit"])
        )
        monitor_thread.daemon = True

        # Track start time and memory
        start_time = time.time()
        start_memory = psutil.virtual_memory().available

        # Start monitoring and attack
        monitor_thread.start()
        attack_thread.start()

        # Wait for completion or timeout
        attack_thread.wait(config["duration_limit"] * 1000)  # Convert to milliseconds

        # Stop attack if still running
        if attack_thread.isRunning():
            attack_thread.stop()
            attack_thread.wait(5000)  # Wait up to 5 seconds for clean shutdown

        end_time = time.time()
        end_memory = psutil.virtual_memory().available

        # Get final statistics
        stats = attack_thread.stats
        actual_duration = end_time - start_time

        # Calculate performance metrics
        passwords_tested = stats.get('total_passwords_tested', 0)
        passwords_per_second = passwords_tested / actual_duration if actual_duration > 0 else 0

        result = {
            "config_name": config_name,
            "attack_type": config["attack_type"],
            "config": config,
            "duration_actual": actual_duration,
            "duration_limit": config["duration_limit"],
            "passwords_tested": passwords_tested,
            "passwords_per_second": passwords_per_second,
            "memory_used_mb": (start_memory - end_memory) / 1024 / 1024,
            "status": stats.get('status', 'unknown'),
            "errors": stats.get('errors', 0),
            "start_time": stats.get('start_time').isoformat() if stats.get('start_time') else None,
            "end_time": stats.get('end_time').isoformat() if stats.get('end_time') else None,
            "efficiency_score": self._calculate_efficiency_score(passwords_per_second, config)
        }

        print(f"   Duration: {actual_duration:.1f}s")
        print(f"   Passwords Tested: {passwords_tested:,}")
        print(f"   Speed: {passwords_per_second:.1f} p/s")
        return result

    def _calculate_efficiency_score(self, passwords_per_second: float, config: Dict[str, Any]) -> float:
        """Calculate efficiency score based on attack type and performance"""
        base_scores = {
            "Dictionary Attack (WPA2)": 1000,
            "Brute Force Attack": 100,
            "Rule-based Attack": 500,
            "Hybrid Attack": 300,
            "Mask Attack": 200,
            "Combinator Attack": 150,
            "Pin Code Attack": 10000
        }

        base_score = base_scores.get(config["attack_type"], 100)
        return (passwords_per_second / base_score) * 100

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmark tests"""
        print(">>> Starting Keyspace Performance Benchmark Suite")
        print("=" * 60)

        all_results = {
            "system_info": self.system_info,
            "benchmark_timestamp": datetime.now().isoformat(),
            "results": {}
        }

        for config_name, config in self.test_configs.items():
            try:
                result = self.run_single_benchmark(config_name, config)
                all_results["results"][config_name] = result

                # Force garbage collection between tests
                gc.collect()
                time.sleep(2)  # Brief pause between tests

            except Exception as e:
                print(f"[ERROR] Error in benchmark {config_name}: {str(e)}")
                all_results["results"][config_name] = {
                    "config_name": config_name,
                    "error": str(e),
                    "status": "failed"
                }

        # Generate summary
        all_results["summary"] = self._generate_summary(all_results["results"])

        return all_results

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from all benchmark results"""
        successful_tests = [r for r in results.values() if r.get("status") != "failed"]
        failed_tests = [r for r in results.values() if r.get("status") == "failed"]

        if not successful_tests:
            return {"error": "No successful tests"}

        total_passwords = sum(r.get("passwords_tested", 0) for r in successful_tests)
        avg_speed = sum(r.get("passwords_per_second", 0) for r in successful_tests) / len(successful_tests)
        max_speed = max((r.get("passwords_per_second", 0) for r in successful_tests), default=0)
        min_speed = min((r.get("passwords_per_second", 0) for r in successful_tests), default=0)

        # Group by attack type
        attack_type_stats = {}
        for result in successful_tests:
            attack_type = result.get("attack_type", "Unknown")
            if attack_type not in attack_type_stats:
                attack_type_stats[attack_type] = []
            attack_type_stats[attack_type].append(result.get("passwords_per_second", 0))

        attack_type_avg = {}
        for attack_type, speeds in attack_type_stats.items():
            attack_type_avg[attack_type] = sum(speeds) / len(speeds)

        return {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "total_passwords_tested": total_passwords,
            "average_speed_pps": avg_speed,
            "max_speed_pps": max_speed,
            "min_speed_pps": min_speed,
            "attack_type_averages": attack_type_avg,
            "system_efficiency_rating": self._calculate_system_rating(avg_speed)
        }

    def _calculate_system_rating(self, avg_speed: float) -> str:
        """Calculate system performance rating"""
        if avg_speed > 10000:
            return "Excellent"
        elif avg_speed > 5000:
            return "Very Good"
        elif avg_speed > 2000:
            return "Good"
        elif avg_speed > 500:
            return "Fair"
        else:
            return "Needs Optimization"

    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save benchmark results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n[SAVE] Results saved to: {output_path}")
        return str(output_path)

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable performance report"""
        report_lines = []
        report_lines.append("Keyspace Performance Benchmark Report")
        report_lines.append("=" * 50)
        report_lines.append("")

        # System Info
        report_lines.append("System Information:")
        report_lines.append(f"  CPU Cores: {results['system_info']['cpu_count']}")
        report_lines.append(f"  Logical CPUs: {results['system_info']['cpu_count_logical']}")
        report_lines.append(f"  Memory: {results['system_info']['memory_total'] / (1024**3):.1f} GB")
        report_lines.append(f"  Platform: {results['system_info']['platform']}")
        report_lines.append("")

        # Summary
        summary = results.get("summary", {})
        report_lines.append("Benchmark Summary:")
        report_lines.append(f"  Total Tests: {summary.get('total_tests', 0)}")
        report_lines.append(f"  Successful: {summary.get('successful_tests', 0)}")
        report_lines.append(f"  Failed: {summary.get('failed_tests', 0)}")
        report_lines.append(f"  Total Passwords Tested: {summary.get('total_passwords_tested', 0):,}")
        report_lines.append(f"  Average Speed: {summary.get('average_speed_pps', 0):.1f} p/s")
        report_lines.append(f"  System Rating: {summary.get('system_efficiency_rating', 'Unknown')}")
        report_lines.append("")

        # Attack Type Performance
        report_lines.append("Attack Type Performance:")
        attack_averages = summary.get("attack_type_averages", {})
        for attack_type, avg_speed in sorted(attack_averages.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"  {attack_type}: {avg_speed:.1f} p/s")
        report_lines.append("")

        # Detailed Results
        report_lines.append("Detailed Results:")
        report_lines.append("-" * 30)

        for test_name, result in results["results"].items():
            if result.get("status") == "failed":
                report_lines.append(f"[FAILED] {test_name}: {result.get('error', 'Unknown error')}")
                continue

            report_lines.append(f"[SUCCESS] {test_name}:")
            report_lines.append(f"   Attack Type: {result.get('attack_type', 'N/A')}")
            report_lines.append(f"   Duration: {result.get('duration_actual', 0):.1f}s")
            report_lines.append(f"   Passwords Tested: {result.get('passwords_tested', 0):,}")
            report_lines.append(f"   Speed: {result.get('passwords_per_second', 0):.1f} p/s")
            report_lines.append(f"   Memory Used: {result.get('memory_used_mb', 0):.1f} MB")
            report_lines.append("")

        # Recommendations
        report_lines.append("Performance Recommendations:")
        report_lines.append("-" * 30)

        avg_speed = summary.get("average_speed_pps", 0)
        if avg_speed < 1000:
            report_lines.append("• Consider using GPU acceleration for better performance")
            report_lines.append("• Optimize memory usage in attack threads")
        elif avg_speed < 5000:
            report_lines.append("• Good performance, but could benefit from multi-threading optimizations")
        else:
            report_lines.append("• Excellent performance! System is well-optimized")

        report_lines.append("• Regular benchmarking helps track performance improvements")
        report_lines.append("• Consider attack type selection based on target characteristics")

        return "\n".join(report_lines)

    def save_report(self, report: str, filename: Optional[str] = None) -> str:
        """Save human-readable report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_report_{timestamp}.txt"

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            f.write(report)

        print(f"[REPORT] Report saved to: {output_path}")
        return str(output_path)


def main():
    """Main entry point for benchmarking"""
    parser = argparse.ArgumentParser(description="Keyspace Performance Benchmark")
    parser.add_argument("--output-dir", default="benchmark_results",
                       help="Output directory for results (default: benchmark_results)")
    parser.add_argument("--single-test", help="Run only a specific test")
    parser.add_argument("--duration-multiplier", type=float, default=1.0,
                       help="Multiply duration limits by this factor")

    args = parser.parse_args()

    # Create benchmark instance
    benchmark = PerformanceBenchmark(args.output_dir)

    # Adjust duration limits if specified
    if args.duration_multiplier != 1.0:
        for config in benchmark.test_configs.values():
            config["duration_limit"] = int(config["duration_limit"] * args.duration_multiplier)

    try:
        if args.single_test:
            # Run single test
            if args.single_test in benchmark.test_configs:
                result = benchmark.run_single_benchmark(args.single_test, benchmark.test_configs[args.single_test])
                results = {
                    "system_info": benchmark.system_info,
                    "benchmark_timestamp": datetime.now().isoformat(),
                    "results": {args.single_test: result},
                    "summary": benchmark._generate_summary({args.single_test: result})
                }
            else:
                print(f"[ERROR] Test '{args.single_test}' not found. Available tests:")
                for test_name in benchmark.test_configs.keys():
                    print(f"  - {test_name}")
                return
        else:
            # Run all benchmarks
            results = benchmark.run_all_benchmarks()

        # Save results
        json_file = benchmark.save_results(results)

        # Generate and save report
        report = benchmark.generate_report(results)
        txt_file = benchmark.save_report(report)

        print("\n[SUCCESS] Benchmarking complete!")
        print(f"[JSON] Results: {json_file}")
        print(f"[REPORT] Text Report: {txt_file}")

        # Print summary to console
        summary = results.get("summary", {})
        print("\n[SUMMARY]:")
        print(f"  Average Speed: {summary.get('average_speed_pps', 0):.1f} p/s")
        print(f"[RATING] System Rating: {summary.get('system_efficiency_rating', 'Unknown')}")

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Benchmark interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Benchmark failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

