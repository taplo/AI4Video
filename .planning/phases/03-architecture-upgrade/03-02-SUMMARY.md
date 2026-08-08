# Plan 03-02: AnalysisManager Rewrite

## Objective
Rewrite AnalysisManager to use ThreadPoolExecutor instead of multiprocessing.

## What Was Built

### 1. ThreadPoolExecutor for Pipeline Management
- Replaced multiprocessing-based pipeline management with `concurrent.futures.ThreadPoolExecutor`
- Each camera pipeline runs as a Future in the thread pool
- Removed `_mp_ctx`, `_status_manager`, `_status_dict` and related multiprocessing code

### 2. Signal Handlers for Graceful Shutdown
- Added `_setup_signal_handlers()` method to register SIGTERM and SIGINT handlers
- Signal handlers call `shutdown(timeout=30)` for graceful shutdown
- Uses `threading.Event` for coordination (not direct cleanup in signal handler)

### 3. Graceful Shutdown Method
- Added `shutdown(timeout=30)` method
- Sets `_shutdown_event` to reject new tasks
- Calls `_executor.shutdown(wait=False, cancel_futures=True)`
- Waits for running futures with configurable timeout

### 4. Worker Health Checks
- Added `_health_check_loop()` method running in daemon thread
- Checks pipeline health every 30 seconds
- Logs exceptions from completed futures
- Starts automatically in `__init__`

### 5. Updated Pipeline Lifecycle
- `start()` now always uses thread-based approach (removed `_use_multiprocess()` check)
- `stop()` cancels Future and calls `pipeline.stop()`
- `_is_pipeline_alive()` checks `future.done()` instead of `process.is_alive()`
- All existing public methods preserved

## Files Modified
- `app/analysis/manager.py` (complete rewrite of pipeline management)

## Verification
- AnalysisManager uses concurrent.futures.ThreadPoolExecutor
- Signal handlers registered for SIGTERM/SIGINT
- shutdown() method exists and uses _shutdown_event.set()
- _health_check_loop method exists and runs in daemon thread
- start() checks _shutdown_event.is_set() and returns False if shutting down

## Self-Check: PASSED
