"""
PTY Runner - Run commands in a pseudo-terminal.

This module provides functionality to run CLI commands in a PTY,
capturing all output including ANSI escape codes.
"""

import os
import pty
import select
import subprocess
import signal
import time
from typing import Union


class PTYRunner:
    """Run commands in a pseudo-terminal and capture output."""
    
    def __init__(self, rows: int = 24, cols: int = 80):
        """
        Initialize the PTY runner.
        
        Args:
            rows: Number of terminal rows
            cols: Number of terminal columns
        """
        self.rows = rows
        self.cols = cols
        self.output = b""
    
    def run(
        self,
        command: Union[str, list[str]],
        timeout: float | None = None,
        env: dict[str, str] | None = None,
    ) -> bytes:
        """
        Run a command in a PTY and capture output.
        
        Args:
            command: Command to run (string or list of arguments)
            timeout: Maximum time to run (seconds). If None, wait for completion.
            env: Additional environment variables
        
        Returns:
            Raw bytes output from the command
        """
        # Prepare command
        if isinstance(command, str):
            shell_command = command
            use_shell = True
        else:
            shell_command = " ".join(command)
            use_shell = True
        
        # Set up environment
        cmd_env = os.environ.copy()
        cmd_env["TERM"] = "xterm-256color"
        cmd_env["COLUMNS"] = str(self.cols)
        cmd_env["LINES"] = str(self.rows)
        # Force color output for common tools
        cmd_env["CLICOLOR_FORCE"] = "1"
        cmd_env["FORCE_COLOR"] = "1"
        if env:
            cmd_env.update(env)
        
        # Create PTY
        master_fd, slave_fd = pty.openpty()
        
        # Set terminal size and disable echo
        import fcntl
        import struct
        import termios
        
        winsize = struct.pack("HHHH", self.rows, self.cols, 0, 0)
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)
        
        # Disable echo so the command isn't echoed back
        attrs = termios.tcgetattr(slave_fd)
        attrs[3] = attrs[3] & ~termios.ECHO  # Disable ECHO flag
        termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)
        
        self.output = b""
        
        try:
            # Start process
            process = subprocess.Popen(
                shell_command,
                shell=use_shell,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                env=cmd_env,
                preexec_fn=os.setsid,
            )
            
            # Close slave in parent
            os.close(slave_fd)
            
            # Read output
            start_time = time.time()
            
            while True:
                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        # Kill the process group
                        try:
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        break
                
                # Check if process has ended
                poll_result = process.poll()
                
                # Use select to check for available data
                remaining = None
                if timeout is not None:
                    remaining = max(0, timeout - (time.time() - start_time))
                
                try:
                    ready, _, _ = select.select([master_fd], [], [], 0.1 if remaining is None else min(0.1, remaining))
                except ValueError:
                    # File descriptor closed
                    break
                
                if ready:
                    try:
                        data = os.read(master_fd, 4096)
                        if data:
                            self.output += data
                        else:
                            # EOF
                            if poll_result is not None:
                                break
                    except OSError:
                        break
                elif poll_result is not None:
                    # Process ended and no more data
                    # Do one final read attempt
                    try:
                        ready, _, _ = select.select([master_fd], [], [], 0.05)
                        if ready:
                            data = os.read(master_fd, 4096)
                            if data:
                                self.output += data
                    except (OSError, ValueError):
                        pass
                    break
        
        finally:
            # Clean up
            try:
                os.close(master_fd)
            except OSError:
                pass
        
        return self.output
    
    def get_output(self) -> bytes:
        """Get the captured output."""
        return self.output


def run_command(
    command: Union[str, list[str]],
    timeout: float | None = None,
    rows: int = 24,
    cols: int = 80,
    env: dict[str, str] | None = None,
) -> bytes:
    """
    Convenience function to run a command and capture PTY output.
    
    Args:
        command: Command to run
        timeout: Maximum execution time (seconds)
        rows: Terminal rows
        cols: Terminal columns
        env: Additional environment variables
    
    Returns:
        Raw bytes output from the command
    """
    runner = PTYRunner(rows=rows, cols=cols)
    return runner.run(command, timeout=timeout, env=env)
