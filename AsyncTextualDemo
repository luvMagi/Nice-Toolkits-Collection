"""
Asynchronous Business Process Textual UI Demo

This application demonstrates how to handle long-running business logic in Textual UI:
- Using TextArea to display real-time logs
- Updating UI via callbacks
- Support for starting/stopping business processing  
- Simulating IO intensive operations
"""

import asyncio
import time
from datetime import datetime
from typing import Callable, Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, TextArea, Static, ProgressBar
from textual.worker import Worker, get_current_worker
from textual import log
import random


class BusinessProcessor:
    """
    Business Processor Class

    Simulates a long running business processor that includes:
    - IO intensive operations (simulated with sleep)
    - Callback mechanism to update UI
    - Interruptible processing flow
    """

    def __init__(self):
        self.is_running = False
        self.log_callback: Optional[Callable[[str], None]] = None
        self.progress_callback: Optional[Callable[[int], None]] = None
        self.total_tasks = 10
        self.current_task = 0

    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set the log callback function

        Args:
            callback: Callback function that receives log messages
        """
        self.log_callback = callback

    def set_progress_callback(self, callback: Callable[[int], None]) -> None:
        """
        Set the progress callback function

        Args:
            callback: Callback function that receives progress percentage
        """
        self.progress_callback = callback

    def _log(self, message: str) -> None:
        """
        Internal logging method that sends logs to UI via callback

        Args:
            message: Log message
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_message = f"[{timestamp}] {message}"

        if self.log_callback:
            self.log_callback(full_message)

    def _update_progress(self, current: int) -> None:
        """
        Update processing progress

        Args:
            current: Number of tasks completed
        """
        progress = int((current / self.total_tasks) * 100)
        if self.progress_callback:
            self.progress_callback(progress)

    async def start_processing(self) -> None:
        """
        Start business processing flow

        This is the main business function that simulates time consuming operations:
        1. Data preprocessing
        2. Batch task processing  
        3. Result summarization

        Uses asyncio.sleep to simulate IO operations while keeping UI responsive
        """
        if self.is_running:
            self._log("❌ Processing already running, please stop current task first")
            return

        try:
            self.is_running = True
            self.current_task = 0

            self._log("🚀 Starting business processing flow")

            # Stage 1: Initialize and preprocess
            self._log("📋 Stage 1: Data preprocessing...")
            await asyncio.sleep(1.5)  # Simulate data loading time

            if not self.is_running:
                self._log("⏸️  Processing interrupted by user")
                return

            self._log("✅ Data preprocessing completed")

            # Stage 2: Batch task processing
            self._log(f"⚙️  Stage 2: Processing {self.total_tasks} tasks...")

            for i in range(self.total_tasks):
                if not self.is_running:
                    self._log("⏸️  Processing interrupted by user")
                    return

                # Simulate processing time for each task (random 0.5-2 seconds)
                task_duration = random.uniform(0.5, 2.0)
                task_name = f"Task-{i + 1:02d}"

                self._log(f"🔄 Processing {task_name} (estimated time: {task_duration:.1f}s)")

                # Simulate IO intensive operation
                await asyncio.sleep(task_duration)

                # Simulate occasional errors
                if random.random() < 0.1:  # 10% chance of warning
                    self._log(f"⚠️  Warning while processing {task_name}, but continuing")
                else:
                    self._log(f"✅ {task_name} completed")

                self.current_task = i + 1
                self._update_progress(self.current_task)

                # Give UI a chance to update
                await asyncio.sleep(0.1)

            if not self.is_running:
                self._log("⏸️  Processing interrupted by user")
                return

            # Stage 3: Result summarization  
            self._log("📊 Stage 3: Summarizing results...")
            await asyncio.sleep(1.0)  # Simulate summary time

            if not self.is_running:
                self._log("⏸️  Processing interrupted by user")
                return

            # Generate processing report
            success_rate = random.uniform(85, 98)
            total_time = sum(random.uniform(0.5, 2.0) for _ in range(self.total_tasks)) + 3.5

            self._log("=" * 50)
            self._log("📋 Processing Complete Report:")
            self._log(f"   • Total tasks: {self.total_tasks}")
            self._log(f"   • Success rate: {success_rate:.1f}%")
            self._log(f"   • Total time: {total_time:.1f} seconds")
            self._log(f"   • Average time per task: {total_time / self.total_tasks:.2f} seconds")
            self._log("=" * 50)
            self._log("🎉 All processing completed successfully!")

        except asyncio.CancelledError:
            self._log("❌ Processing forcefully cancelled")
        except Exception as e:
            self._log(f"💥 Processing exception occurred: {str(e)}")
        finally:
            self.is_running = False
            self._update_progress(0)  # Reset progress bar

    def stop_processing(self) -> None:
        """
        Stop business processing

        Sets stop flag that business loop checks to gracefully exit
        """
        if self.is_running:
            self._log("🛑 Received stop signal, gracefully exiting...")
            self.is_running = False
        else:
            self._log("ℹ️  No processing currently running")


class AsyncBusinessApp(App):
    """
    Asynchronous Business Processing Textual Application

    Demonstrates handling long running async tasks in Textual:
    - Real-time log display
    - Progress bar updates
    - Start/Stop controls  
    - Non-blocking UI interaction
    """

    CSS = """
    .main-container {
        height: 100%;
        margin: 1;
    }
    
    .log-container {
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
        height: 50%;
        
    }
    
    .controls-container {
        border: solid $primary;
        padding: 1;
        height: 50%;
    }
    
    .progress-container {
        margin: 1 0;
    }
    
    .status-text {
        text-align: center;
        margin: 1 0;
    }
    
    .button-group {
        height: auto;
        align: center middle;
    }
    
    #log-area {
        height: 60%;
        min-height: 12;
        background: $surface;
    }
    
    #start-button {
        margin: 0 1;
        min-width: 12;
    }
    
    #stop-button {
        margin: 0 1;
        min-width: 12;
    }
    
    #progress-bar {
        margin: 1 0;
    }
    """

    def __init__(self):
        super().__init__()
        self.business_processor = BusinessProcessor()
        self.current_worker: Optional[Worker] = None

        # Set up business processor callbacks
        self.business_processor.set_log_callback(self.add_log)
        self.business_processor.set_progress_callback(self.update_progress)

    def compose(self) -> ComposeResult:
        """Build the user interface"""

        yield Header(show_clock=True)

        with Container(classes="main-container"):
            # Log display area - takes more space
            with Container(classes="log-container"):
                yield Static("📋 Processing Log", classes="status-text")
                yield TextArea(
                    "=== Business Processing System Ready ===\n"
                    "Click \"Start Processing\" button to begin\n"
                    "Logs will display here in real-time...\n"
                    "\n"
                    "💡 Tips:\n"
                    "- Processing simulates real IO operations\n"
                    "- Each task takes 0.5-2 seconds\n"
                    "- Total of 10 tasks to process\n"
                    "- Can stop running tasks at any time\n"
                    "- UI remains responsive\n"
                    "\n"
                    "Ready to begin...",
                    read_only=True,
                    show_line_numbers=True,
                    id="log-area"
                )

            # Control panel - takes less space
            with Container(classes="controls-container"):
                yield Static("🎮 Control Panel", classes="status-text")

                # Progress bar container
                with Container(classes="progress-container"):
                    yield Static("Progress:", id="progress-label")
                    yield ProgressBar(total=100, show_eta=False, id="progress-bar")

                # Button group
                with Horizontal(classes="button-group"):
                    yield Button(
                        "🚀 Start Processing",
                        variant="success",
                        id="start-button"
                    )
                    yield Button(
                        "🛑 Stop Processing",
                        variant="error",
                        id="stop-button"
                    )
                    yield Button(
                        "🗑️  Clear Log",
                        variant="warning",
                        id="clear-button"
                    )

        yield Footer()

    def on_mount(self) -> None:
        """Initialize on application startup"""
        self.add_log("🔧 System initialization complete")
        self.add_log("💡 Tip: Processing simulates IO operations and may take time")
        self.add_log("⚡ UI remains responsive during processing, can stop anytime")
        self.add_log("📊 TextArea sized larger to show more log lines")

        # Set initial button states
        self.update_button_states(False)

    def add_log(self, message: str) -> None:
        """
        Add log to TextArea

        Called by business processor callback to update logs in real-time

        Args:
            message: Log message to add
        """
        try:
            log_area = self.query_one("#log-area", TextArea)

            # Append new log at the end 
            current_text = log_area.text
            new_text = current_text + message + "\n"
            log_area.load_text(new_text)

            # Auto-scroll to bottom to show latest logs
            log_area.scroll_end()

        except Exception as e:
            # Log to app log if UI update fails
            log(f"Failed to update log UI: {e}")

    def update_progress(self, progress: int) -> None:
        """
        Update progress bar

        Args:
            progress: Progress percentage (0-100)
        """
        try:
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            progress_bar.progress = progress

            # Update progress label
            progress_label = self.query_one("#progress-label", Static)
            if progress > 0:
                progress_label.update(f"Progress: {progress}%")
            else:
                progress_label.update("Progress:")

        except Exception as e:
            log(f"Failed to update progress UI: {e}")

    def update_button_states(self, is_running: bool) -> None:
        """
        Update button states

        Args:
            is_running: Whether processing is running
        """
        try:
            start_button = self.query_one("#start-button", Button)
            stop_button = self.query_one("#stop-button", Button)

            # Disable start button and enable stop button while running
            start_button.disabled = is_running
            stop_button.disabled = not is_running

            # Update button text and style
            if is_running:
                start_button.label = "⏳ Processing..."
                stop_button.label = "🛑 Stop Processing"
            else:
                start_button.label = "🚀 Start Processing"
                stop_button.label = "⏸️  Stopped"

        except Exception as e:
            log(f"Failed to update button states: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click events"""

        button_id = event.button.id

        if button_id == "start-button":
            # Start processing
            if not self.business_processor.is_running:
                self.add_log("👤 User clicked start processing")
                self.update_button_states(True)

                # Use Textual Worker to run processing in background
                # Worker ensures long running tasks don't block UI
                self.current_worker = self.run_worker(
                    self.business_processor.start_processing(),
                    exclusive=True,  # Only run one processor at a time
                    description="Business Processing"
                )

        elif button_id == "stop-button":
            # Stop processing
            if self.business_processor.is_running:
                self.add_log("👤 User clicked stop processing")
                self.business_processor.stop_processing()

                # Try to cancel active worker if exists
                if self.current_worker and not self.current_worker.is_finished:
                    self.current_worker.cancel()

        elif button_id == "clear-button":
            # Clear log
            try:
                log_area = self.query_one("#log-area", TextArea)
                log_area.load_text("=== Log Cleared ===\nReady for new logs...\n")
                self.add_log("👤 User cleared log")
            except Exception as e:
                log(f"Failed to clear log: {e}")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when Worker state changes"""
        if event.worker.is_finished:
            self.add_log("🔧 Processing Worker completed")
            self.update_button_states(False)
            self.current_worker = None

    def on_unmount(self) -> None:
        """Cleanup when application closes"""
        if self.business_processor.is_running:
            self.business_processor.stop_processing()

        if self.current_worker and not self.current_worker.is_finished:
            self.current_worker.cancel()


if __name__ == "__main__":
    """
    Application entry point
    
    Running this script starts a full-screen TUI app showing:
    - Larger real-time log display area (10+ lines visible) 
    - Asynchronous business processing
    - Progress tracking
    - User interaction controls
    """
    app = AsyncBusinessApp()
    app.run()
