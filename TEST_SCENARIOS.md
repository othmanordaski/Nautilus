# Test Scenarios - Error Handling & Retry Logic

## Overview
This document outlines test scenarios for validating the error handling and retry logic implementation in Nautilus.

---

## 1. Network Timeout Tests

### Test 1.1: Single Timeout with Successful Retry
**Objective**: Verify retry logic works after a timeout

**Steps**:
1. Start Nautilus: `python app.py`
2. Simulate slow network (if possible, throttle connection to 1KB/s)
3. Search for a movie: "Inception"
4. Observe retry messages

**Expected Result**:
- First attempt times out
- System shows: `[yellow]Request timeout. Retrying in 1.0s... (1/3)[/yellow]`
- Second attempt succeeds
- Search results display normally

**Pass Criteria**: ✓ Retry happens automatically, ✓ User sees retry message, ✓ Eventually succeeds

---

### Test 1.2: Multiple Timeouts Leading to Failure
**Objective**: Verify system fails gracefully after max retries

**Steps**:
1. Completely disconnect from internet
2. Run: `python app.py`
3. Try to search: "Avatar"

**Expected Result**:
- Three timeout attempts with exponential backoff (1s, 2s, 4s)
- Final message: `[red]Request timed out after 3 attempts[/red]`
- Returns to prompt without crashing

**Pass Criteria**: ✓ Exponential backoff visible, ✓ Fails gracefully, ✓ No crash

---

## 2. Server Error Tests

### Test 2.1: 500 Server Error with Recovery
**Objective**: Verify retry on server errors

**Setup**: (Requires mock server or catching real 500 errors)

**Steps**:
1. Run Nautilus
2. Search for content when server returns 500
3. Observe retry behavior

**Expected Result**:
- Shows: `[yellow]Server error (500). Retrying in 1.0s... (1/3)[/yellow]`
- Retries up to 3 times
- If server recovers, continues normally

**Pass Criteria**: ✓ Retries on 5xx errors, ✓ Shows status code, ✓ Recovers if server fixes

---

### Test 2.2: 404 Not Found (No Retry)
**Objective**: Verify client errors don't trigger retries

**Steps**:
1. Run Nautilus
2. Search for: "xyznonexistentmovie12345"
3. Observe behavior

**Expected Result**:
- No retry attempts (404 is client error, not server error)
- Returns empty results or error message
- No unnecessary retry delays

**Pass Criteria**: ✓ No retries on 4xx, ✓ Fast failure, ✓ Clear error message

---

## 3. Network Error Tests

### Test 3.1: Connection Refused
**Objective**: Test behavior when server is unreachable

**Steps**:
1. Modify `~/.config/nautilus/config.yaml`:
   ```yaml
   base_url: "http://localhost:9999"  # Non-existent server
   ```
2. Run: `python app.py`
3. Try to search: "Test"

**Expected Result**:
- Shows: `[yellow]Network error. Retrying in 1.0s... (1/3)[/yellow]`
- Retries 3 times with exponential backoff
- Final: `[red]Network error: Unable to connect after 3 attempts[/red]`

**Pass Criteria**: ✓ Handles connection refused, ✓ Retries appropriately, ✓ Clear error

---

### Test 3.2: DNS Resolution Failure
**Objective**: Test invalid hostname handling

**Steps**:
1. Modify config to use invalid domain:
   ```yaml
   base_url: "https://this-domain-does-not-exist-12345.com"
   ```
2. Run Nautilus
3. Search for anything

**Expected Result**:
- Network error detected
- Retries with backoff
- Eventually fails with clear message

**Pass Criteria**: ✓ Handles DNS errors, ✓ No crash, ✓ User-friendly message

---

## 4. Decrypt API Tests

### Test 4.1: Decrypt API Timeout
**Objective**: Test stream extraction failures

**Steps**:
1. Search and select a movie
2. Wait for stream extraction
3. If decrypt API is slow, observe retry

**Expected Result**:
- Retries decrypt API calls
- Shows appropriate error if all retries fail
- Falls back gracefully

**Pass Criteria**: ✓ Retries decrypt calls, ✓ Error message shown, ✓ Can try another movie

---

### Test 4.2: Invalid Decrypt Response
**Objective**: Test malformed decrypt API response

**Steps**:
1. Select content that has broken decrypt response
2. Observe error handling

**Expected Result**:
- Shows: `[red]Failed to decrypt stream: [error details][/red]`
- Returns to menu
- Doesn't crash

**Pass Criteria**: ✓ Handles bad JSON, ✓ Clear error, ✓ Recoverable

---

## 5. Multi-Step Failure Tests

### Test 5.1: Search → Seasons → Episodes Flow
**Objective**: Test error handling across multiple API calls

**Steps**:
1. Search: "Breaking Bad"
2. Select the show
3. Disconnect network before seasons load
4. Observe behavior
5. Reconnect network
6. Try again

**Expected Result**:
- Each API call retries independently
- Clear error at failure point
- Can retry from menu

**Pass Criteria**: ✓ Each step handles errors, ✓ State preserved, ✓ Can recover

---

## 6. Exponential Backoff Verification

### Test 6.1: Timing Verification
**Objective**: Verify retry delays are correct

**Steps**:
1. Disconnect internet
2. Run search
3. Time the retry attempts

**Expected Timing**:
- Attempt 1: Immediate
- Retry 1: After ~1 second
- Retry 2: After ~2 seconds  
- Retry 3: After ~4 seconds
- Total: ~7-8 seconds before final failure

**Pass Criteria**: ✓ Delays match exponential pattern, ✓ Not too fast, ✓ Not too slow

---

## 7. Provider Fallback Tests

### Test 7.1: Primary Provider Failure
**Objective**: Test behavior when configured provider fails

**Steps**:
1. Config: `provider: "NonExistentProvider"`
2. Search and select content
3. Try to play

**Expected Result**:
- Shows: `[red]Could not find server for provider: NonExistentProvider[/red]`
- Clear error message
- Suggest user to check config

**Pass Criteria**: ✓ Detects missing provider, ✓ Helpful error, ✓ Doesn't crash

---

## 8. Edge Cases

### Test 8.1: Empty Search Results
**Objective**: Handle no results gracefully

**Steps**:
1. Search: "asdfjkl12345notreal"
2. Observe behavior

**Expected Result**:
- No errors (empty is valid)
- Shows: "No results found."
- Returns to search prompt

**Pass Criteria**: ✓ Handles empty elegantly, ✓ No exceptions, ✓ Clear message

---

### Test 8.2: Intermittent Connection
**Objective**: Test recovery from flaky network

**Steps**:
1. Start search
2. Toggle WiFi on/off rapidly during requests
3. Let it stabilize
4. Complete operation

**Expected Result**:
- Multiple retries visible
- Eventually succeeds when connection stable
- No data corruption

**Pass Criteria**: ✓ Resilient to flakiness, ✓ Recovers gracefully, ✓ Data integrity

---

## 9. User Experience Tests

### Test 9.1: Retry Message Clarity
**Objective**: Verify error messages are helpful

**Expected Messages**:
- ✓ `Request timeout. Retrying in 2.0s... (2/3)` - Shows attempt number
- ✓ `Server error (503). Retrying...` - Shows status code
- ✓ `Network error: Unable to connect after 3 attempts` - Clear final message

**Pass Criteria**: ✓ Messages are clear, ✓ User knows what's happening, ✓ Shows progress

---

### Test 9.2: Performance Under Normal Conditions
**Objective**: Ensure retry logic doesn't slow normal operations

**Steps**:
1. With good internet connection
2. Complete full flow: Search → Select → Play
3. Time the operation

**Expected Result**:
- No retry messages shown
- Normal speed (no artificial delays)
- Timeout set to 30s is reasonable

**Pass Criteria**: ✓ Fast on success, ✓ No unnecessary waits, ✓ Smooth UX

---

## 10. Stress Tests

### Test 10.1: Rapid Sequential Requests
**Objective**: Test retry logic under load

**Steps**:
1. Search multiple times rapidly
2. Select different content quickly
3. Observe resource usage

**Expected Result**:
- Each request handled independently
- No memory leaks
- Retries don't stack indefinitely

**Pass Criteria**: ✓ Handles concurrent failures, ✓ Memory stable, ✓ No deadlocks

---

### Test 10.2: Long Session
**Objective**: Test stability over extended use

**Steps**:
1. Use Nautilus for 30+ minutes
2. Search, play, resume multiple items
3. Include some network disruptions

**Expected Result**:
- httpx client stays healthy
- Retries continue working
- No degradation over time

**Pass Criteria**: ✓ Stable long-term, ✓ No connection leaks, ✓ Consistent behavior

---

## Test Execution Checklist

### Manual Testing
- [ ] Test 1.1 - Single timeout retry
- [ ] Test 1.2 - Max retries exceeded
- [ ] Test 2.2 - 404 no retry
- [ ] Test 3.1 - Connection refused
- [ ] Test 3.2 - DNS failure
- [ ] Test 4.2 - Invalid decrypt response
- [ ] Test 5.1 - Multi-step flow
- [ ] Test 6.1 - Timing verification
- [ ] Test 7.1 - Provider fallback
- [ ] Test 8.1 - Empty results
- [ ] Test 8.2 - Intermittent connection
- [ ] Test 9.1 - Message clarity
- [ ] Test 9.2 - Normal performance
- [ ] Test 10.1 - Rapid requests
- [ ] Test 10.2 - Long session

### Success Criteria
- ✓ All tests pass
- ✓ No crashes or exceptions
- ✓ Clear error messages
- ✓ Appropriate retry behavior
- ✓ Good user experience

---

## Quick Test Commands

```bash
# Test with good connection
python app.py
# Search: "Inception", verify normal flow

# Test with no connection
# Disconnect WiFi, then:
python app.py
# Verify retry messages and graceful failure

# Test with slow connection
# Throttle to 100KB/s, then:
python app.py
# Search: "Avatar", watch for timeouts

# Test invalid config
# Edit config with bad URL:
nano ~/.config/nautilus/config.yaml
# Change base_url to "http://invalid-domain.local"
python app.py
# Verify error handling
```

---

## Notes for Testers

1. **Network Simulation**: Use tools like `tc` (Linux) or NetLimiter (Windows) to simulate network conditions
2. **Log Monitoring**: Watch terminal output for colored error/retry messages
3. **Config Backup**: Keep backup of `config.yaml` before testing with invalid settings
4. **Reset Between Tests**: Clear state between tests for consistent results
5. **Document Issues**: Note any unexpected behavior or unclear error messages

---

## Automated Test Ideas (Future)

- Mock httpx responses with `respx` library
- Simulate timeouts with `pytest-timeout`
- Test exponential backoff timing with `freezegun`
- Parameterized tests for different error codes
- Integration tests with mock FlixHQ server
