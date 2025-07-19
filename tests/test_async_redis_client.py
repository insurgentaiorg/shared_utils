import asyncio
import time
import threading
from pydantic import BaseModel
import pytest
import uuid
from shared_utils.clients.redis_client import redis_client

class TestMessage(BaseModel):
    id: str
    value: str

# Test 1: Concurrent callback execution
# This test will verify that multiple callbacks are executed concurrently
# by measuring execution time of slow callbacks

def test_concurrent_callbacks():
    # Setup
    stream_name = f"test-stream-{uuid.uuid4()}"
    group_id = "test-group"
    execution_times = []
    execution_order = []
    lock = threading.Lock()
    event = threading.Event()
    callback_count = 5

    # Create callback that simulates slow processing (1 second)
    def slow_callback(msg_id, data):
        with lock:
            start_time = time.time()
            execution_order.append(f"start-{data['value']}")

        # Simulate work
        time.sleep(1)

        with lock:
            execution_times.append(time.time() - start_time)
            execution_order.append(f"end-{data['value']}")
            if len(execution_times) == callback_count:
                event.set()

    # Register callback
    redis_client.register_callback(stream_name, group_id, slow_callback)

    # Send multiple messages quickly
    for i in range(callback_count):
        message = TestMessage(id=str(i), value=f"test-{i}")
        redis_client.send(stream_name, message)

    # Wait for all callbacks to complete (with timeout)
    assert event.wait(timeout=3), "Callbacks did not complete in time"

    # Verify execution was concurrent
    # If execution is concurrent, total time should be much less than (callback_count * 1 second)
    # We expect it to be close to 1 second (slightly more due to overhead)
    max_time = max(execution_times)
    assert max_time < 3, f"Execution took too long ({max_time}s), suggests non-concurrent execution"

    # Cleanup
    redis_client.stop_consumer(stream_name)

# Test 2: Max concurrency limit
# This test verifies the max_concurrent_tasks parameter works correctly

def test_max_concurrency_limit():
    # Setup
    stream_name = f"test-stream-{uuid.uuid4()}"
    group_id = "test-group"
    max_concurrent = 2
    execution_starts = []
    running_count = [0]  # Use list for mutable reference
    max_running = [0]
    lock = threading.Lock()
    all_done_event = threading.Event()
    messages_sent = 5

    # Create callback that tracks concurrency
    def tracking_callback(msg_id, data):
        with lock:
            running_count[0] += 1
            max_running[0] = max(max_running[0], running_count[0])
            execution_starts.append(time.time())

        # Hold execution to ensure concurrency
        time.sleep(1)

        with lock:
            running_count[0] -= 1
            if len(execution_starts) == messages_sent:
                all_done_event.set()

    # Create consumer with max_concurrent_tasks=2
    redis_client.create_consumer(stream_name, group_id, max_concurrent_tasks=max_concurrent)
    redis_client.register_callback(stream_name, group_id, tracking_callback)

    # Send messages
    for i in range(messages_sent):
        message = TestMessage(id=str(i), value=f"test-{i}")
        redis_client.send(stream_name, message)

    # Wait for all callbacks to complete
    assert all_done_event.wait(timeout=5), "Callbacks did not complete in time"

    # Verify max concurrent tasks was respected
    assert max_running[0] <= max_concurrent, f"Max concurrency exceeded: {max_running[0]} > {max_concurrent}"

    # Cleanup
    redis_client.stop_consumer(stream_name)

# Test 3: Mixed async and sync callbacks
# This test verifies both async and sync callbacks work
# (requires async test support)
@pytest.mark.asyncio
async def test_mixed_callbacks():
    # Setup
    stream_name = f"test-stream-{uuid.uuid4()}"
    group_id = "test-group"
    sync_called = [0]
    async_called = [0]
    all_done_event = asyncio.Event()

    # Create sync callback
    def sync_callback(msg_id, data):
        time.sleep(0.5)  # Simulate work
        sync_called[0] += 1
        check_done()

    # Create async callback
    async def async_callback(msg_id, data):
        await asyncio.sleep(0.5)  # Simulate async work
        async_called[0] += 1
        check_done()

    def check_done():
        if sync_called[0] + async_called[0] == 4:  # 2 messages * 2 callbacks
            all_done_event.set()

    # Register both types of callbacks
    redis_client.register_callback(stream_name, group_id, sync_callback)
    redis_client.register_callback(stream_name, group_id, async_callback)

    # Send messages
    for i in range(2):
        message = TestMessage(id=str(i), value=f"test-{i}")
        redis_client.send(stream_name, message)

    # Wait for completion with timeout
    try:
        await asyncio.wait_for(all_done_event.wait(), timeout=3)
    except asyncio.TimeoutError:
        pytest.fail("Callbacks did not complete in time")

    # Verify both types of callbacks were called
    assert sync_called[0] == 2, f"Sync callback called {sync_called[0]} times instead of 2"
    assert async_called[0] == 2, f"Async callback called {async_called[0]} times instead of 2"

    # Cleanup
    redis_client.stop_consumer(stream_name)

# Test 4: Error handling in callbacks
# This test verifies that errors in callbacks don't break processing

def test_callback_error_handling():
    # Setup
    stream_name = f"test-stream-{uuid.uuid4()}"
    group_id = "test-group"
    successful_calls = [0]
    event = threading.Event()

    # Create callbacks - one that fails, one that succeeds
    def failing_callback(msg_id, data):
        raise Exception("Intentional test failure")

    def successful_callback(msg_id, data):
        successful_calls[0] += 1
        if successful_calls[0] == 2:  # We expect 2 messages
            event.set()

    # Register callbacks
    redis_client.register_callback(stream_name, group_id, failing_callback)
    redis_client.register_callback(stream_name, group_id, successful_callback)

    # Send messages
    for i in range(2):
        message = TestMessage(id=str(i), value=f"test-{i}")
        redis_client.send(stream_name, message)

    # Wait for successful callback completions
    assert event.wait(timeout=3), "Callbacks did not complete in time"

    # Verify the successful callback was called for both messages
    # despite errors in the failing callback
    assert successful_calls[0] == 2, "Successful callback was not called correctly"

    # Cleanup
    redis_client.stop_consumer(stream_name)