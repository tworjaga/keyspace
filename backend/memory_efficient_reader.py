"""
Memory-efficient wordlist reader for large files
Provides streaming processing to minimize memory usage
"""

import os
import mmap
import logging
from typing import Iterator, Optional, TextIO
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryEfficientWordlistReader:
    """Memory-efficient wordlist reader that streams large files without loading everything into memory"""

    def __init__(self, file_path: str, encoding: str = 'utf-8', errors: str = 'ignore'):
        """
        Initialize the memory-efficient reader

        Args:
            file_path: Path to the wordlist file
            encoding: Text encoding to use
            errors: How to handle encoding errors
        """
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.errors = errors
        self.file_size = 0
        self.line_count = 0

        if not self.file_path.exists():
            raise FileNotFoundError(f"Wordlist file not found: {file_path}")

        # Get file statistics
        self.file_size = self.file_path.stat().st_size

    def get_file_info(self) -> dict:
        """Get basic file information"""
        return {
            'file_path': str(self.file_path),
            'file_size': self.file_size,
            'file_size_formatted': self._format_file_size(self.file_size)
        }

    def count_lines(self) -> int:
        """Count total lines in file efficiently"""
        if self.line_count > 0:
            return self.line_count

        try:
            with open(self.file_path, 'rb') as f:
                # Use memory mapping for large files
                if self.file_size > 100 * 1024 * 1024:  # > 100MB
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        self.line_count = mm.read().count(b'\n')
                else:
                    # For smaller files, use regular counting
                    self.line_count = sum(1 for _ in f)
        except Exception as e:
            logger.warning(f"Could not count lines efficiently: {e}")
            # Fallback: estimate based on file size (rough approximation)
            self.line_count = max(1, self.file_size // 50)  # Assume ~50 bytes per line

        return self.line_count

    def stream_lines(self, start_line: int = 0, max_lines: Optional[int] = None,
                    skip_empty: bool = True, skip_comments: bool = True) -> Iterator[tuple[int, str]]:
        """
        Stream lines from the file with memory efficiency

        Args:
            start_line: Line number to start from (0-based)
            max_lines: Maximum number of lines to read (None for all)
            skip_empty: Skip empty lines
            skip_comments: Skip lines starting with #

        Yields:
            Tuple of (line_number, line_content)
        """
        current_line = 0
        lines_read = 0

        try:
            # Use memory mapping for very large files
            if self.file_size > 50 * 1024 * 1024:  # > 50MB
                with open(self.file_path, 'rb') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        # Skip to start_line
                        pos = 0
                        for _ in range(start_line):
                            newline_pos = mm.find(b'\n', pos)
                            if newline_pos == -1:
                                return
                            pos = newline_pos + 1
                            current_line += 1

                        # Read lines from start position
                        while pos < len(mm):
                            if max_lines and lines_read >= max_lines:
                                break

                            newline_pos = mm.find(b'\n', pos)
                            if newline_pos == -1:
                                # Last line without newline
                                line_bytes = mm[pos:]
                            else:
                                line_bytes = mm[pos:newline_pos]

                            try:
                                line = line_bytes.decode(self.encoding, errors=self.errors).rstrip('\r\n')
                            except UnicodeDecodeError:
                                line = line_bytes.decode('latin-1', errors='ignore').rstrip('\r\n')

                            current_line += 1
                            pos = newline_pos + 1 if newline_pos != -1 else len(mm)

                            # Filter lines
                            if skip_empty and not line.strip():
                                continue
                            if skip_comments and line.strip().startswith('#'):
                                continue

                            lines_read += 1
                            yield current_line, line

            else:
                # For smaller files, use regular file reading
                with open(self.file_path, 'r', encoding=self.encoding, errors=self.errors) as f:
                    for line_num, line in enumerate(f, 1):
                        if line_num <= start_line:
                            continue

                        if max_lines and lines_read >= max_lines:
                            break

                        line = line.rstrip('\r\n')

                        # Filter lines
                        if skip_empty and not line.strip():
                            continue
                        if skip_comments and line.strip().startswith('#'):
                            continue

                        lines_read += 1
                        yield line_num, line

        except Exception as e:
            logger.error(f"Error streaming lines from {self.file_path}: {e}")
            raise

    def get_sample_lines(self, count: int = 10, skip_empty: bool = True,
                        skip_comments: bool = True) -> list[str]:
        """Get a sample of lines from the file for preview"""
        sample = []
        for _, line in self.stream_lines(max_lines=count,
                                       skip_empty=skip_empty,
                                       skip_comments=skip_comments):
            sample.append(line)
        return sample

    def validate_file(self) -> dict:
        """Validate that the file is readable and contains valid content"""
        result = {
            'valid': False,
            'error': None,
            'line_count': 0,
            'sample_lines': [],
            'encoding': self.encoding
        }

        try:
            # Try to read first few lines
            sample_lines = self.get_sample_lines(5)
            result['sample_lines'] = sample_lines

            if sample_lines:
                result['valid'] = True
                # Estimate total lines
                result['line_count'] = self.count_lines()
            else:
                result['error'] = "File appears to be empty or contains no valid lines"

        except UnicodeDecodeError:
            result['error'] = f"File encoding issue. Tried {self.encoding}"
        except PermissionError:
            result['error'] = "Permission denied reading file"
        except Exception as e:
            result['error'] = f"Error reading file: {str(e)}"

        return result

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return ".1f"
            size_bytes /= 1024.0
        return ".1f"


class StreamingPasswordProcessor:
    """Processes passwords in streaming fashion to minimize memory usage"""

    def __init__(self, wordlist_reader: MemoryEfficientWordlistReader,
                 batch_size: int = 1000, max_memory_mb: int = 100):
        """
        Initialize streaming processor

        Args:
            wordlist_reader: MemoryEfficientWordlistReader instance
            batch_size: Number of passwords to process in each batch
            max_memory_mb: Maximum memory to use in MB
        """
        self.reader = wordlist_reader
        self.batch_size = batch_size
        self.max_memory_mb = max_memory_mb
        self.current_position = 0

    def process_stream(self, processor_func, start_line: int = 0,
                      max_lines: Optional[int] = None) -> Iterator[dict]:
        """
        Process passwords in streaming batches

        Args:
            processor_func: Function to process each batch of passwords
            start_line: Line to start processing from
            max_lines: Maximum lines to process

        Yields:
            Processing results for each batch
        """
        batch = []
        batch_start_line = start_line

        for line_num, password in self.reader.stream_lines(start_line=start_line,
                                                         max_lines=max_lines):
            batch.append(password)

            if len(batch) >= self.batch_size:
                # Process batch
                result = processor_func(batch, batch_start_line, line_num)
                yield result

                # Reset for next batch
                batch = []
                batch_start_line = line_num + 1

        # Process remaining batch
        if batch:
            result = processor_func(batch, batch_start_line, line_num)
            yield result

    def get_progress_info(self, current_line: int) -> dict:
        """Get progress information"""
        total_lines = self.reader.count_lines()
        progress_percent = (current_line / total_lines * 100) if total_lines > 0 else 0

        return {
            'current_line': current_line,
            'total_lines': total_lines,
            'progress_percent': progress_percent,
            'file_size': self.reader.file_size,
            'file_size_formatted': self.reader._format_file_size(self.reader.file_size)
        }
