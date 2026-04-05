# Killswitch Module — Remote App Gating

## TL;DR
> **Summary**: Add a remote-kill capability that gates PhantastLab startup via a Cloudflare Worker endpoint. On launch, the app checks local kill flags and contacts the server with a hardware fingerprint. Server responses are HMAC-signed. If killed, the app silently exits. Phased delivery: core logic first, obfuscation second.
> **Deliverables**: Killswitch service module, HMAC-verified server check, local persistence (3 backends), Cloudflare Worker endpoint, hardware fingerprinting, obfuscation layer, comprehensive tests, PyInstaller integration
> **Effort**: Medium
> **Parallel**: YES - 3 waves (Wave 1: server + fingerprint + persistence + core logic; Wave 2: main.py integration + obfuscation; Wave 3: PyInstaller + final verification)
> **Critical Path**: Task 1 (server) → Task 3 (persistence) → Task 5 (core evaluator) → Task 7 (main.py hook) → Task 10 (obfuscation) → Task 12 (PyInstaller) → Final Verification

## Context
### Original Request
Add a killswitch module to PhantastLab that allows remotely blocking app startup. Semi-technical threat model (registry editing, file deletion, basic reverse engineering). No UI changes.

### Interview Summary
- Fail-closed policy: offline + local kill flag = blocked; offline + no flag = allowed
- HMAC-signed server responses to prevent spoofing
- 2-second network timeout budget
- Phased: core logic + tests first, obfuscation second
- Server: Cloudflare Worker with GET /check?id=<machine_id>
- Machine ID: MAC + disk serial + hostname → SHA-256 (persisted once generated)
- Local persistence: 3 backends (QSettings/Registry, AppData hidden file, environment variable)
- No new dependencies (stdlib only)

### Metis Review (gaps addressed)
- **Policy contradiction resolved**: Defined explicit decision matrix for all state combinations (local flag × server reachable × server response)
- **Fingerprint instability**: Persist machine_id once generated; use multi-source hash
- **Response spoofing**: HMAC-signed responses mandated
- **Over-scoped hardening**: Phased into Wave 2, after core logic is tested
- **Persistence fragility**: Best-effort multi-write with explicit error handling
- **Startup UX**: Strict 2s timeout, single attempt, no retry storm
- **Partial failure handling**: Defined precedence for read (any flag present = killed) and best-effort for writes

## Work Objectives
### Core Objective
Implement a killswitch that gates PhantastLab startup by checking local flags and a remote Cloudflare Worker endpoint. The killswitch must be invisible (no UI), tamper-resistant (obfuscated), and reliable (tested decision matrix covering all edge cases).

### Deliverables
1. `src/services/killswitch.py` — Core killswitch service module
2. `src/services/hw_fingerprint.py` — Hardware fingerprint generator
3. `src/services/killswitch_persistence.py` — Multi-backend persistence (QSettings, file, env)
4. `server/worker.js` — Cloudflare Worker endpoint (HMAC-signed responses)
5. `server/wrangler.toml` — Worker configuration
6. `src/services/killswitch_obfuscation.py` — String/code obfuscation utilities
7. `tests/services/test_killswitch.py` — Comprehensive unit tests
8. `tests/services/test_hw_fingerprint.py` — Fingerprint tests
9. `tests/services/test_killswitch_persistence.py` — Persistence tests
10. `tests/mock_server.py` — Local HTTP mock server for QA scenarios
11. Updated `PhantastLab.spec` — PyInstaller hardening (strip + optimize)
11. Updated `src/main.py` — Startup hook

### Definition of Done (verifiable conditions with commands)
```bash
# All tests pass
pytest tests/services/test_killswitch.py tests/services/test_hw_fingerprint.py tests/services/test_killswitch_persistence.py -v

# Lint clean
ruff check src/services/killswitch.py src/services/hw_fingerprint.py src/services/killswitch_persistence.py src/services/killswitch_obfuscation.py

# App launches when killswitch allows
python src/main.py  # (with mock server returning "ok")

# App exits when killswitch blocks
python src/main.py  # (with mock server returning "kill")

# PyInstaller build succeeds
pyinstaller PhantastLab.spec
```

### Must Have
- All 8 rows of the startup decision matrix implemented and tested
- HMAC signature verification on server responses
- Machine ID generated once and persisted
- 3-backend local persistence (Registry, file, env var)
- 2-second network timeout
- Silent exit on kill (no error dialogs, no traceback)
- Cloudflare Worker deployed and responding

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- NO UI elements, dialogs, toast notifications, or windows
- NO new third-party dependencies in the Python client (stdlib only). The `server/` directory is a separate Cloudflare Worker project and may have its own JS dev dependencies (wrangler) — these are NOT counted as client dependencies.
- NO business logic changes to existing modules
- NO PyQt imports in `hw_fingerprint.py` or `killswitch_obfuscation.py` (must be pure Python)
- NO retry loops or exponential backoff on network calls
- NO logging of killswitch decisions to visible log files (telemetry only in obfuscated storage)
- NO `QDialog`, `QMessageBox`, or popup widgets

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification is agent-executed.
- Test decision: TDD (RED-GREEN-REFACTOR) for core evaluator; tests-after for integration
- Framework: pytest + pytest-mock
- QA policy: Every task has agent-executed scenarios
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`

## Startup Decision Matrix (authoritative)
| # | Local Flag | Server Reachable | Server Response | Result |
|---|-----------|-----------------|-----------------|--------|
| 1 | No | Yes | "ok" | ✅ Open |
| 2 | No | Yes | "kill" | ❌ Block + set all flags |
| 3 | No | Yes | "unkill" | ✅ Open (no-op, no flags to clear) |
| 4 | Yes | Yes | "ok" | ✅ Open + clear all flags |
| 5 | Yes | Yes | "kill" | ❌ Block (flags already set) |
| 6 | Yes | Yes | "unkill" | ✅ Open + clear all flags |
| 7 | No | No | N/A | ✅ Open (fail-open, no flag) |
| 8 | Yes | No | N/A | ❌ Block (fail-closed, flag present) |
| 9 | Any | Yes | Invalid/timeout/error | ✅ Open (fail-open on error) |
| 10 | Any | Yes | HMAC invalid | ✅ Open (fail-open, treat as error) |

## Execution Strategy
### Parallel Execution Waves

**Wave 1 — Foundation (independent, fully parallel)**
- Task 1: Cloudflare Worker endpoint (server/)
- Task 2: Hardware fingerprint module
- Task 3: Killswitch persistence module
- Task 4: HMAC utility module

**Wave 2 — Core Logic (depends on Wave 1)**
- Task 5: Core killswitch evaluator (depends on Tasks 2, 3, 4)
- Task 6: Killswitch integration tests (depends on Task 5)

**Wave 3 — Integration (depends on Wave 2)**
- Task 7: main.py startup hook (depends on Task 5)
- Task 8: String obfuscation module
- Task 9: Apply obfuscation to killswitch module
- Task 10: PyInstaller hardening (depends on Task 7)

**Final Verification Wave**
- Task F1–F4: Plan compliance, code quality, manual QA, scope fidelity

### Dependency Matrix
| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 (Server) | None | 5, 7 |
| 2 (Fingerprint) | None | 5, 7 |
| 3 (Persistence) | None | 5, 7 |
| 4 (HMAC) | None | 5 |
| 5 (Evaluator) | 2, 3, 4 | 6, 7, 8, 9 |
| 6 (Integration tests) | 5 | F1–F4 |
| 7 (main.py hook) | 5 | 10 |
| 8 (Obfuscation) | None | 9 |
| 9 (Apply obfuscation) | 5, 8 | F1–F4 |
| 10 (PyInstaller) | 7 | F1–F4 |

### Agent Dispatch Summary
| Wave | Tasks | Categories |
|------|-------|-----------|
| 1 | 4 tasks | quick × 3, unspecified-low × 1 |
| 2 | 2 tasks | unspecified-high × 1, unspecified-low × 1 |
| 3 | 4 tasks | unspecified-high × 1, quick × 2, unspecified-low × 1 |
| Final | 4 tasks | oracle, unspecified-high × 2, deep |

## TODOs

- [ ] 1. Cloudflare Worker Endpoint

  **What to do**: Create a Cloudflare Worker in `server/` that handles GET /check?id=<machine_id> requests. The worker must:
  1. Create `server/` directory at project root
  2. Create `server/worker.js` with a `fetch(request, env)` handler
  3. Parse the `id` query parameter from the URL
  4. Look up the machine ID in a KV namespace (or hardcoded allowlist for MVP)
  5. Return JSON: `{"status": "ok"|"kill"|"unkill", "ts": <unix_timestamp>, "sig": "<hmac_hex>"}`
  6. Sign the response: HMAC-SHA256 of `f"{status}:{timestamp}"` using `env.HMAC_SECRET`
  7. Include CORS headers for development testing
  8. Create `server/wrangler.toml` with worker config (name, compatibility_date, KV binding)
  9. Create `server/package.json` with wrangler dev dependency
  10. Create `server/README.md` with deployment instructions (`wrangler deploy`, secret setup)

  **Must NOT do**: Do not add authentication beyond HMAC signing. Do not use D1 database (KV is sufficient). Do not implement rate limiting.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: Well-defined server boilerplate, minimal logic
  - Skills: [] — No special skills needed for a simple JS worker
  - Omitted: [`computer-vision-opencv`] — Not relevant to server code

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: [5, 7] | Blocked By: []

  **References**:
  - Cloudflare Worker pattern: `export default { async fetch(request, env) { ... } }` — standard Worker entry
  - KV namespace: `env.KILL_FLAGS.get(machineId)` — simple key-value lookup
  - HMAC in Worker: `const key = await crypto.subtle.importKey('raw', encoder.encode(env.HMAC_SECRET), {name:'HMAC', hash:'SHA-256'}, false, ['sign'])`
  - Existing project structure: Project root is `D:\work\phantast-py-stem-cell-confluency\`

  **Acceptance Criteria** (agent-executable only):
  - [ ] `server/worker.js` exists and exports a `fetch` handler
  - [ ] `server/wrangler.toml` exists with valid Cloudflare Worker config
  - [ ] `wrangler dev` starts without errors (local dev server)
  - [ ] `curl "http://localhost:8787/check?id=test123"` returns JSON with `status`, `ts`, and `sig` fields
  - [ ] Response signature is valid HMAC-SHA256 of `f"{status}:{ts}"` string

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Valid machine ID returns signed response
    Tool: Bash (curl)
    Steps: Start `wrangler dev` in server/ directory, then `curl "http://localhost:8787/check?id=test123"`
    Expected: JSON response with {"status":"ok","ts":<number>,"sig":"<64-char-hex>"}, HTTP 200
    Evidence: .sisyphus/evidence/task-1-server-valid.txt

  Scenario: Missing ID parameter returns error
    Tool: Bash (curl)
    Steps: `curl "http://localhost:8787/check"`
    Expected: HTTP 400 with error message about missing ID
    Evidence: .sisyphus/evidence/task-1-server-missing-id.txt

  Scenario: HMAC signature verification
    Tool: Bash (node)
    Steps: Extract sig and body from response, recompute HMAC-SHA256 with same secret, compare
    Expected: Signatures match exactly
    Evidence: .sisyphus/evidence/task-1-hmac-verify.txt
  ```

  **Commit**: YES | Message: `feat(killswitch): add Cloudflare Worker endpoint with HMAC signing` | Files: [server/*]

---

- [ ] 2. Hardware Fingerprint Module

  **What to do**: Create `src/services/hw_fingerprint.py` — a pure Python module (NO PyQt imports) that generates a stable per-machine hardware ID. Implementation:
  1. Create `src/services/hw_fingerprint.py`
  2. Implement `get_machine_id() -> str` that:
     - Tries `uuid.getnode()` for MAC address (returns 48-bit int)
     - Falls back to `platform.node()` for hostname if MAC is unreliable (uuid.getnode() returns a random value starting with specific bit patterns — check if the returned value's multicast bit is set, which indicates random)
     - Gets disk serial via `subprocess.run(["wmic", "diskdrive", "get", "serialnumber"])` on Windows, with error handling for non-Windows
     - Concatenates: `f"{mac}:{disk_serial}:{hostname}"` and returns SHA-256 hex digest
  3. Implement `persist_machine_id(machine_id: str) -> None` that writes the ID to a hidden file in AppData:
     - Path: `os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".phantastlab_mid")`
     - Write the machine ID as plain text to this file
     - Wrap in try/except — persistence failure should not crash the app
  4. Implement `get_persisted_machine_id() -> str | None` that reads the ID from the AppData file:
     - If file exists and content is a valid 64-char hex string, return it
     - Otherwise return None
  5. Implement `get_or_create_machine_id() -> str` — returns persisted ID if exists, else generates + persists + returns new one
  6. Handle edge cases: `uuid.getnode()` returning random, `wmic` not available, subprocess errors, file permission errors

  **Why file-based persistence (not QSettings)**: The existing `SettingsService` (`src/services/settings_service.py`) only exposes node-parameter methods (`get_node_parameters`, `save_node_parameter`, etc.) — there is no generic key/value API. Adding one would require modifying both `SettingsInterface` and `SettingsService`, violating the "no existing business logic changes" scope boundary. A simple AppData file avoids this entirely.

  **Must NOT do**: No PyQt imports in this file. No network calls. Must not use QSettings or settings_service. Must be CLI-testable.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: Small utility module, well-defined interface
  - Skills: [] — No special skills needed
  - Omitted: [`pyqt6-ui-development-rules`] — No PyQt used here

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: [5, 7] | Blocked By: []

  **References**:
  - AppData path pattern: `os.environ.get("APPDATA", os.path.expanduser("~"))` — same pattern used in Task 3 for kill flags
  - MAC address via uuid: `uuid.getnode()` returns 48-bit int, check multicast bit for reliability
  - Disk serial on Windows: `wmic diskdrive get serialnumber` — parse stdout, handle encoding issues
  - SHA-256: `hashlib.sha256(f"{mac}:{disk}:{host}".encode()).hexdigest()`

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/services/test_hw_fingerprint.py -v` — all tests pass
  - [ ] `ruff check src/services/hw_fingerprint.py` — no errors
  - [ ] No PyQt6 imports found in the file: `Select-String -Path "src/services/hw_fingerprint.py" -Pattern "PyQt6"` returns no matches
  - [ ] `get_or_create_machine_id()` returns a 64-char lowercase hex string

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Machine ID is deterministic
    Tool: Bash (pytest)
    Steps: Mock uuid.getnode() to return 0x AABBCCDDEEFF, mock hostname "test-pc", mock wmic output "WD-12345". Call get_machine_id() twice.
    Expected: Both calls return identical SHA-256 hex string
    Evidence: .sisyphus/evidence/task-2-deterministic.txt

  Scenario: Fallback when MAC is unreliable
    Tool: Bash (pytest)
    Steps: Mock uuid.getnode() to return value with multicast bit set (random indicator). Verify hostname is used as fallback component.
    Expected: Still returns valid 64-char hex string, hostname is part of input to hash
    Evidence: .sisyphus/evidence/task-2-mac-fallback.txt

  Scenario: wmic subprocess failure
    Tool: Bash (pytest)
    Steps: Mock subprocess.run to raise FileNotFoundError. Call get_machine_id().
    Expected: Returns valid hash using MAC + hostname only (no crash)
    Evidence: .sisyphus/evidence/task-2-wmic-fail.txt

  Scenario: Persisted ID is reused
    Tool: Bash (pytest)
    Steps: Call get_or_create_machine_id() once, then call again with get_machine_id() mocked to raise.
    Expected: Second call returns the persisted ID without regenerating
    Evidence: .sisyphus/evidence/task-2-persist.txt
  ```

  **Commit**: YES | Message: `feat(killswitch): add hardware fingerprint module` | Files: [src/services/hw_fingerprint.py, tests/services/test_hw_fingerprint.py]

---

- [ ] 3. Killswitch Persistence Module

  **What to do**: Create `src/services/killswitch_persistence.py` — multi-backend persistence for kill flags. Implementation:
  1. Create `src/services/killswitch_persistence.py`
  2. Define a `KillswitchPersistence` class with methods:
     - `set_kill_flag() -> None` — write kill flag to all 3 backends
     - `clear_kill_flag() -> None` — remove kill flag from all 3 backends
     - `is_kill_flag_set() -> bool` — check if flag exists in ANY backend
  3. Backend 1 — QSettings (Windows Registry):
     - Use existing `QSettings("PhantastLab", "PhantastLab")` instance
     - Key: `"killswitch/killed"` → value: ISO timestamp of when flag was set
     - Read: `settings.value("killswitch/killed", None)`
     - Write: `settings.setValue("killswitch/killed", timestamp)`
     - Clear: `settings.remove("killswitch/killed")`
  4. Backend 2 — Hidden file in AppData:
     - Path: `os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".phantastlab_kill")`
     - Write: create file with timestamp content
     - Read: check file existence
     - Clear: delete file
  5. Backend 3 — Environment variable (current process only, persists in parent if launched from shell):
     - Key: `PHANTASTLAB_KILLED`
     - Write: `os.environ["PHANTASTLAB_KILLED"] = timestamp`
     - Read: `"PHANTASTLAB_KILLED" in os.environ`
     - Clear: `os.environ.pop("PHANTASTLAB_KILLED", None)`
  6. Error handling: Each backend write must be wrapped in try/except. Log failures silently. A single backend failure must not prevent other backends from being written.
  7. Read precedence: If ANY backend has the flag, return True (conservative — fail-closed).

  **Must NOT do**: No network calls. No UI. Must not crash if QSettings is not yet initialized (handle gracefully). Must not create directories that don't exist.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: Straightforward CRUD operations across 3 backends
  - Skills: [`pyqt6-ui-development-rules`] — Needed for QSettings pattern reference
  - Omitted: [`computer-vision-opencv`] — Not relevant

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: [5, 7] | Blocked By: []

  **References**:
  - QSettings singleton: `src/services/settings_service.py:35` — `QSettings("PhantastLab", "PhantastLab")`
  - QSettings value/set/remove: `src/services/settings_service.py:48,71,92` — `.value()`, `.setValue()`, `.remove()`, `.sync()`
  - APPDATA path: `os.environ.get("APPDATA", os.path.expanduser("~"))` — Windows AppData or home fallback
  - Pattern for multi-backend writes: Try each, collect errors, never abort early

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/services/test_killswitch_persistence.py -v` — all tests pass
  - [ ] `ruff check src/services/killswitch_persistence.py` — no errors
  - [ ] `is_kill_flag_set()` returns False when all backends are clean
  - [ ] `set_kill_flag()` writes to all 3 backends and `is_kill_flag_set()` returns True
  - [ ] `clear_kill_flag()` removes from all 3 and `is_kill_flag_set()` returns False

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Set flag writes to all backends
    Tool: Bash (pytest)
    Steps: Call set_kill_flag() with mocked QSettings, temp AppData dir, and clean env. Verify QSettings value set, file created, env var set.
    Expected: All 3 backends contain the kill flag
    Evidence: .sisyphus/evidence/task-3-set-all.txt

  Scenario: Any single backend triggers is_kill_flag_set
    Tool: Bash (pytest)
    Steps: Clear all backends, then set ONLY the AppData file flag. Call is_kill_flag_set().
    Expected: Returns True
    Evidence: .sisyphus/evidence/task-3-any-flag.txt

  Scenario: Clear removes from all backends
    Tool: Bash (pytest)
    Steps: Set all 3 backends, then call clear_kill_flag(). Verify all 3 are empty.
    Expected: QSettings key removed, file deleted, env var unset
    Evidence: .sisyphus/evidence/task-3-clear.txt

  Scenario: Partial backend failure during write
    Tool: Bash (pytest)
    Steps: Mock QSettings.setValue to raise OSError. Call set_kill_flag(). Verify file and env var still written.
    Expected: No exception raised, 2 of 3 backends written successfully
    Evidence: .sisyphus/evidence/task-3-partial-fail.txt
  ```

  **Commit**: YES | Message: `feat(killswitch): add multi-backend persistence for kill flags` | Files: [src/services/killswitch_persistence.py, tests/services/test_killswitch_persistence.py]

---

- [ ] 4. HMAC Utility Module

  **What to do**: Create `src/services/killswitch_hmac.py` — a pure Python module for HMAC signing and verification. Implementation:
  1. Create `src/services/killswitch_hmac.py`
  2. Implement `sign_response(status: str, timestamp: int, secret: str) -> str`:
     - Create message: `f"{status}:{timestamp}"`
     - Return `hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()`
  3. Implement `verify_response(status: str, timestamp: int, signature: str, secret: str) -> bool`:
     - Compute expected signature using same algorithm
     - Use `hmac.compare_digest()` (constant-time comparison) to prevent timing attacks
     - Return True if match, False otherwise
  4. The HMAC secret will be hardcoded (obfuscated) in the client and stored as a Cloudflare Worker secret

  **Must NOT do**: No third-party crypto libraries. No timing-vulnerable string comparison. No network calls.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: ~20 lines, well-defined crypto primitive wrappers
  - Skills: [] — stdlib hmac module is straightforward
  - Omitted: [`pyqt6-ui-development-rules`] — No Qt involved

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: [5] | Blocked By: []

  **References**:
  - Python hmac module: `import hmac, hashlib` — stdlib
  - Constant-time comparison: `hmac.compare_digest(a, b)` — prevents timing attacks
  - Message format: `f"{status}:{timestamp}"` — simple concatenation with separator

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/services/test_killswitch_hmac.py -v` — all tests pass
  - [ ] `ruff check src/services/killswitch_hmac.py` — no errors
  - [ ] `verify_response()` returns True for valid signatures
  - [ ] `verify_response()` returns False for tampered signatures (single char changed)
  - [ ] `verify_response()` returns False for wrong secret

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Valid signature verifies correctly
    Tool: Bash (pytest)
    Steps: sign_response("kill", 1700000000, "secret123"), then verify_response("kill", 1700000000, sig, "secret123")
    Expected: verify returns True
    Evidence: .sisyphus/evidence/task-4-valid-sig.txt

  Scenario: Tampered status fails verification
    Tool: Bash (pytest)
    Steps: Sign with status="kill", verify with status="ok" (same timestamp and secret)
    Expected: verify returns False
    Evidence: .sisyphus/evidence/task-4-tampered.txt

  Scenario: Wrong secret fails verification
    Tool: Bash (pytest)
    Steps: Sign with "secret123", verify with "wrong_secret"
    Expected: verify returns False
    Evidence: .sisyphus/evidence/task-4-wrong-secret.txt

  Scenario: Signature is deterministic
    Tool: Bash (pytest)
    Steps: Sign same inputs twice
    Expected: Identical hex strings returned
    Evidence: .sisyphus/evidence/task-4-deterministic.txt
  ```

  **Commit**: YES | Message: `feat(killswitch): add HMAC signing and verification utility` | Files: [src/services/killswitch_hmac.py, tests/services/test_killswitch_hmac.py]

---

- [ ] 5. Core Killswitch Evaluator

  **What to do**: Create `src/services/killswitch.py` — the main orchestrator that ties fingerprint, persistence, HMAC, and network check together. Implementation:
  1. Create `src/services/killswitch.py`
  2. Implement `is_startup_allowed() -> bool` that executes the full decision matrix:
     ```
     Step 1: Read local kill flags via KillswitchPersistence.is_kill_flag_set()
     Step 2: If local flag set AND server unreachable → return False (row 8)
     Step 3: If no local flag AND server unreachable → return True (row 7)
     Step 4: Server reachable → build URL with machine_id, make GET request
     Step 5: Parse JSON response, verify HMAC signature
     Step 6: If HMAC invalid → return True (row 10, fail-open on error)
     Step 7: Based on status field:
       - "ok": clear flags if set, return True (rows 1, 4)
       - "kill": set flags, return False (rows 2, 5)
       - "unkill": clear flags, return True (rows 3, 6)
       - anything else: return True (row 9)
     ```
  3. Implement `_check_server(machine_id: str) -> dict | None`:
     - Build URL: `f"{base_url}/check?id={machine_id}"`
     - `base_url` is determined by: `os.environ.get("KILLSWITCH_URL_OVERRIDE") or deobfuscate_string(OBFUSCATED_URL, key)` — this allows tests and QA to override the endpoint without modifying source code
     - Use `urllib.request.urlopen()` with 2-second timeout
     - Parse JSON response body
     - Return parsed dict or None on any error (timeout, DNS failure, HTTP error, JSON parse error)
  4. Implement `_verify_server_response(response: dict) -> bool`:
     - Extract `status`, `ts`, `sig` from response
     - Call `killswitch_hmac.verify_response(status, ts, sig, HMAC_SECRET)`
     - Check timestamp is within ±5 minutes of current time (replay protection)
     - Return True/False
  5. All HTTP errors, timeouts, JSON parse errors → treat as "server unreachable"
  6. The server URL and HMAC secret are placeholder strings that will be replaced with obfuscated values in Task 9

  **Must NOT do**: No UI. No retry logic. No logging to console/files. No more than 2-second timeout. Must not import PyQt6 (use settings_service for QSettings access via the persistence module).

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: Core logic with complex decision matrix, needs careful TDD implementation
  - Skills: [`numpy-best-practices`] — No, not needed
  - Omitted: [`pyqt6-ui-development-rules`] — No direct Qt usage

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: [6, 7, 8, 9] | Blocked By: [2, 3, 4]

  **References**:
  - Fingerprint module: `src/services/hw_fingerprint.py` — `get_or_create_machine_id()`
  - Persistence module: `src/services/killswitch_persistence.py` — `set_kill_flag()`, `clear_kill_flag()`, `is_kill_flag_set()`
  - HMAC module: `src/services/killswitch_hmac.py` — `verify_response()`
  - HTTP client: `urllib.request.urlopen(url, timeout=2)` — stdlib, no new dependency
  - JSON parsing: `json.loads(response.read().decode())`
  - Decision matrix: See "Startup Decision Matrix" section above in this plan

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/services/test_killswitch.py -v` — all tests pass
  - [ ] All 10 decision matrix rows have dedicated test cases
  - [ ] `ruff check src/services/killswitch.py` — no errors
  - [ ] Network timeout is exactly 2 seconds (configurable via constant)

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Row 1 - No flag, server ok → allow
    Tool: Bash (pytest)
    Steps: Mock is_kill_flag_set()=False, mock server response={"status":"ok","ts":now,"sig":valid_hmac}
    Expected: is_startup_allowed() returns True, no flags set
    Evidence: .sisyphus/evidence/task-5-row1.txt

  Scenario: Row 2 - No flag, server kill → block + set flags
    Tool: Bash (pytest)
    Steps: Mock is_kill_flag_set()=False, mock server response={"status":"kill","ts":now,"sig":valid_hmac}
    Expected: is_startup_allowed() returns False, set_kill_flag() called
    Evidence: .sisyphus/evidence/task-5-row2.txt

  Scenario: Row 6 - Flag set, server unkill → clear + allow
    Tool: Bash (pytest)
    Steps: Mock is_kill_flag_set()=True, mock server response={"status":"unkill","ts":now,"sig":valid_hmac}
    Expected: is_startup_allowed() returns True, clear_kill_flag() called
    Evidence: .sisyphus/evidence/task-5-row6.txt

  Scenario: Row 8 - Flag set, offline → block (fail-closed)
    Tool: Bash (pytest)
    Steps: Mock is_kill_flag_set()=True, mock urlopen to raise URLError
    Expected: is_startup_allowed() returns False
    Evidence: .sisyphus/evidence/task-5-row8.txt

  Scenario: Row 7 - No flag, offline → allow (fail-open)
    Tool: Bash (pytest)
    Steps: Mock is_kill_flag_set()=False, mock urlopen to raise URLError
    Expected: is_startup_allowed() returns True
    Evidence: .sisyphus/evidence/task-5-row7.txt

  Scenario: Row 10 - Invalid HMAC → allow (fail-open)
    Tool: Bash (pytest)
    Steps: Mock server response with invalid HMAC signature
    Expected: is_startup_allowed() returns True
    Evidence: .sisyphus/evidence/task-5-row10.txt

  Scenario: Row 9 - Malformed response → allow (fail-open)
    Tool: Bash (pytest)
    Steps: Mock server response with status="unexpected_value"
    Expected: is_startup_allowed() returns True
    Evidence: .sisyphus/evidence/task-5-row9.txt

  Scenario: Network timeout respects 2s limit
    Tool: Bash (pytest)
    Steps: Mock urlopen to sleep for 3s. Call is_startup_allowed().
    Expected: Returns True (timeout → unreachable → no flag → allow) within ~2s, not 3s
    Evidence: .sisyphus/evidence/task-5-timeout.txt
  ```

  **Commit**: YES | Message: `feat(killswitch): add core evaluator with decision matrix` | Files: [src/services/killswitch.py, tests/services/test_killswitch.py]

---

- [ ] 6. Killswitch Integration Tests

  **What to do**: Create comprehensive integration tests in `tests/services/test_killswitch_integration.py` that test the full flow end-to-end with a mock HTTP server. Implementation:
  1. Create `tests/services/test_killswitch_integration.py`
  2. Create `tests/conftest.py` (if not exists) — add sys.path bootstrapping at the top:
     ```python
     import sys
     import os
     sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
     ```
     This fixes the existing baseline failure where `tests/test_folder_explorer.py` cannot import `src` module. This is a minimal fix that does not alter any test logic.
     - Use `pytest-mock` + `unittest.mock` to mock `urllib.request.urlopen`
     - For real HTTP testing: create a `tests/mock_server.py` — a tiny `http.server.HTTPServer` that returns canned HMAC-signed responses
     - The mock server reads the desired response from an env var or class variable (e.g., `MOCK_RESPONSE="ok"`)
  3. Use `KILLSWITCH_URL_OVERRIDE` env var (added in Task 5) to point the evaluator at the mock server:
     - Set `KILLSWITCH_URL_OVERRIDE=http://localhost:18765` before importing killswitch
  4. Test full startup flow: `is_startup_allowed()` → correct result for each decision matrix row
  5. Test machine ID integration: verify `get_or_create_machine_id()` is called exactly once
  6. Test persistence integration: verify flags are set/cleared in all backends after evaluator runs
  7. Test HMAC integration: verify correct signature verification with real (test) secret
  8. Test network error scenarios: DNS failure, connection refused, SSL error, empty response, invalid JSON
  9. Test replay protection: verify old timestamps (>5 min) are rejected
  10. Use `pytest-mock` fixtures for all external dependencies

  **Must NOT do**: No real external network calls. No PyQt app initialization needed (mock QSettings). Do not hardcode the real server URL in tests — always use `KILLSWITCH_URL_OVERRIDE`.

  **Recommended Agent Profile**:
  - Category: `unspecified-low` — Reason: Test writing, follows established patterns
  - Skills: [] — pytest-mock is standard
  - Omitted: [`pyqt6-ui-development-rules`] — Tests mock Qt away

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: [F1-F4] | Blocked By: [5]

  **References**:
  - Test patterns: `tests/` directory — look at existing test files for fixture patterns
  - pytest-mock: `mocker.patch("module.function", return_value=...)`
  - QSettings mock: `mocker.patch("src.services.killswitch_persistence.QSettings")`
  - urlopen mock: `mocker.patch("urllib.request.urlopen")`
  - Mock HTTP server: `http.server.HTTPServer` + `BaseHTTPRequestHandler` — stdlib, no dependency
  - Test seam: `KILLSWITCH_URL_OVERRIDE` env var — set in Task 5, used here to redirect to mock server
  - HMAC test secret: Use a known test secret like `"test-secret-for-qa"` — never the real production secret

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/services/test_killswitch_integration.py -v` — all tests pass
  - [ ] Coverage of all 10 decision matrix rows
  - [ ] Network error scenarios covered (DNS, timeout, SSL, empty, invalid JSON)
  - [ ] Replay protection test exists
  - [ ] `KILLSWITCH_URL_OVERRIDE` is used in all tests (no hardcoded real URLs)

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Full kill→unkill cycle
    Tool: Bash (pytest)
    Steps: (1) Set mock server to return "kill" → verify blocked, flags set. (2) Set mock server to return "unkill" → verify allowed, flags cleared. Use KILLSWITCH_URL_OVERRIDE env var.
    Expected: First call returns False, second returns True, persistence backends match state
    Evidence: .sisyphus/evidence/task-6-kill-unkill-cycle.txt

  Scenario: Network transient failure during kill
    Tool: Bash (pytest)
    Steps: Set local flag. Mock urlopen to raise ConnectionResetError.
    Expected: is_startup_allowed() returns False (fail-closed with flag)
    Evidence: .sisyphus/evidence/task-6-network-failure.txt

  Scenario: Replay attack with old timestamp
    Tool: Bash (pytest)
    Steps: Mock server response with timestamp 10 minutes in the past, valid HMAC
    Expected: is_startup_allowed() returns True (HMAC check fails due to stale timestamp → treated as error → fail-open)
    Evidence: .sisyphus/evidence/task-6-replay.txt
  ```

  **Commit**: YES | Message: `test(killswitch): add integration tests for decision matrix` | Files: [tests/services/test_killswitch_integration.py, tests/conftest.py]

---

- [ ] 7. main.py Startup Hook

  **What to do**: Integrate the killswitch into the app startup sequence in `src/main.py`. Implementation:
  1. Open `src/main.py`
  2. Add import: `from src.services.killswitch import is_startup_allowed`
  3. Insert killswitch check AFTER `initialize_settings_interface()` and BEFORE `app = QApplication(sys.argv)`:
     ```python
     def main():
         initialize_settings_interface()

         if not is_startup_allowed():
             sys.exit(0)

         app = QApplication(sys.argv)
         # ... rest unchanged
     ```
  4. The `sys.exit(0)` must be silent — no error output, no traceback, no dialog
  5. Killswitch runs BEFORE QApplication is created, so no Qt-dependent code can execute in the kill path
  6. This means `killswitch_persistence.py` must handle the case where QSettings exists (it was initialized by `initialize_settings_interface()`) but QApplication does not yet exist — QSettings works without QApplication on Windows via Registry backend

  **Must NOT do**: No print statements. No error dialogs. No sys.exit(1) (use exit code 0 to avoid suspicion). No changes to existing function signatures.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: Critical insertion point, must verify QSettings works pre-QApplication
  - Skills: [`pyqt6-ui-development-rules`] — Needed for QSettings/QApplication lifecycle understanding
  - Omitted: [`computer-vision-opencv`] — Not relevant

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: [10] | Blocked By: [5]

  **References**:
  - Current main.py: `src/main.py:14-29` — startup sequence
  - Settings init: `src/main.py:16` — `initialize_settings_interface()` runs before everything
  - QSettings without QApplication: On Windows, QSettings uses Registry backend and does NOT require QApplication instance. Verify this with a test.
  - Import pattern: `from src.services.killswitch import is_startup_allowed` — follows existing import style

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/test_main_startup_killswitch.py -v` — tests pass
  - [ ] `ruff check src/main.py` — no errors
  - [ ] When killswitch blocks: process exits with code 0, no output to stdout/stderr
  - [ ] When killswitch allows: app starts normally (existing behavior unchanged)
  - [ ] Killswitch check happens before `QApplication()` creation

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Blocked startup exits silently
    Tool: Bash (pytest)
    Steps: Mock is_startup_allowed() to return False. Call main() (mock QApplication to prevent real launch).
    Expected: sys.exit(0) called, no output to stdout/stderr, no QApplication created
    Evidence: .sisyphus/evidence/task-7-blocked.txt

  Scenario: Allowed startup proceeds normally
    Tool: Bash (pytest)
    Steps: Mock is_startup_allowed() to return True. Mock QApplication and MainWindow.
    Expected: QApplication created, MainWindow instantiated, show() called — existing flow unchanged
    Evidence: .sisyphus/evidence/task-7-allowed.txt

  Scenario: Killswitch runs before QApplication
    Tool: Bash (pytest)
    Steps: Track call order via mock side_effects. Verify is_startup_allowed() called before QApplication().
    Expected: is_startup_allowed call index < QApplication() call index
    Evidence: .sisyphus/evidence/task-7-order.txt
  ```

  **Commit**: YES | Message: `feat(killswitch): integrate startup gate into main.py` | Files: [src/main.py, tests/test_main_startup_killswitch.py]

---

- [ ] 8. String Obfuscation Module

  **What to do**: Create `src/services/killswitch_obfuscation.py` — pure Python obfuscation utilities. Implementation:
  1. Create `src/services/killswitch_obfuscation.py`
  2. Implement `xor_encode(data: bytes, key: bytes) -> bytes`:
     - XOR each byte of data with corresponding byte of key (cycling)
  3. Implement `xor_decode(data: bytes, key: bytes) -> bytes`:
     - Same as encode (XOR is symmetric)
  4. Implement `obfuscate_string(plaintext: str, key: bytes) -> str`:
     - XOR encode → base64 encode → return string
  5. Implement `deobfuscate_string(encoded: str, key: bytes) -> str`:
     - base64 decode → XOR decode → return string
  6. Implement `generate_key() -> bytes`:
     - Return a deterministic 16-byte key derived from a hardcoded seed (so the encoded strings in the source are reproducible)
  7. Include a helper `encode_for_source(plaintext: str) -> str` that returns the obfuscated string ready to paste into source code
  8. Include a pre-computed lookup table of obfuscated strings needed by the killswitch:
     - Server URL
     - HMAC secret
     - QSettings kill flag key
     - AppData filename
     - Environment variable name

  **Must NOT do**: No PyQt imports. No external crypto libraries. Must be CLI-testable. No code obfuscation yet (that's Task 9).

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: Simple XOR + base64 utilities, ~60 lines
  - Skills: [] — Pure Python, no special skills needed
  - Omitted: [`pyqt6-ui-development-rules`] — No Qt involved

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: [9] | Blocked By: []

  **References**:
  - XOR cipher: `bytes(a ^ b for a, b in zip(data, itertools.cycle(key)))`
  - Base64: `base64.b64encode()` / `base64.b64decode()`
  - Deterministic key: `hashlib.sha256(b"phantast-killswitch-key-seed").digest()[:16]`

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/services/test_killswitch_obfuscation.py -v` — all tests pass
  - [ ] `ruff check src/services/killswitch_obfuscation.py` — no errors
  - [ ] `deobfuscate_string(obfuscate_string("hello", key), key) == "hello"`
  - [ ] No PyQt6 imports: `Select-String -Path "src/services/killswitch_obfuscation.py" -Pattern "PyQt6"` returns no matches

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Round-trip encode/decode
    Tool: Bash (pytest)
    Steps: obfuscate_string("https://example.com/check", key) → encoded. deobfuscate_string(encoded, key) → original.
    Expected: Original string recovered exactly
    Evidence: .sisyphus/evidence/task-8-roundtrip.txt

  Scenario: Obfuscated string is not plaintext-readable
    Tool: Bash (pytest)
    Steps: obfuscate_string("https://example.com/check", key). Check if "https" or "example" appear in result.
    Expected: Neither substring appears in the obfuscated output
    Evidence: .sisyphus/evidence/task-8-not-readable.txt

  Scenario: Different keys produce different output
    Tool: Bash (pytest)
    Steps: obfuscate_string("test", key1) vs obfuscate_string("test", key2)
    Expected: Different encoded strings
    Evidence: .sisyphus/evidence/task-8-different-keys.txt
  ```

  **Commit**: YES | Message: `feat(killswitch): add string obfuscation utilities` | Files: [src/services/killswitch_obfuscation.py, tests/services/test_killswitch_obfuscation.py]

---

- [ ] 9. Apply Obfuscation to Killswitch Module

  **What to do**: Replace all plaintext sensitive strings in the killswitch modules with obfuscated versions. Implementation:
  1. Open `src/services/killswitch.py`
  2. Import `deobfuscate_string` and `generate_key` from `killswitch_obfuscation`
  3. Replace the server URL constant with: `deobfuscate_string("<pre-computed-encoded-url>", generate_key())`
  4. Replace the HMAC secret constant with: `deobfuscate_string("<pre-computed-encoded-secret>", generate_key())`
  5. Open `src/services/killswitch_persistence.py`
  6. Replace QSettings key `"killswitch/killed"` with obfuscated version
  7. Replace AppData filename `".phantastlab_kill"` with obfuscated version
  8. Replace env var name `"PHANTASTLAB_KILLED"` with obfuscated version
  9. Verify all tests still pass after obfuscation (the logic doesn't change, only string representations)
  10. Apply additional code-level obfuscation to `killswitch.py`:
     - Use meaningless variable names in critical sections (e.g., `_a`, `_b`, `_c` for the decision flow)
     - Add dead code branches that are never taken
     - Flatten the control flow where practical

  **Must NOT do**: Do not obfuscate import statements. Do not break existing tests. Do not apply obfuscation to non-killswitch files.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: Careful string replacement across multiple files without breaking logic
  - Skills: [] — No special skills needed
  - Omitted: [`pyqt6-ui-development-rules`] — No new UI

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: [F1-F4] | Blocked By: [5, 8]

  **References**:
  - Obfuscation module: `src/services/killswitch_obfuscation.py` — `deobfuscate_string()`, `generate_key()`
  - Strings to obfuscate in `killswitch.py`: server URL, HMAC secret
  - Strings to obfuscate in `killswitch_persistence.py`: QSettings key, AppData filename, env var name

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/ -v` — all tests still pass
  - [ ] `Select-String -Path src/services/killswitch.py -Pattern "https://"` returns no matches (URL is obfuscated)
  - [ ] `Select-String -Path src/services/killswitch_persistence.py -Pattern "PHANTASTLAB_KILLED"` returns no matches
  - [ ] `Select-String -Path src/services/killswitch_persistence.py -Pattern "killswitch/killed"` returns no matches
  - [ ] No sensitive strings visible via `Select-String` on .pyc files
  - [ ] `deobfuscate_string()` is called at module import time, not at call time (runtime deobfuscation)

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Obfuscated killswitch still blocks correctly
    Tool: Bash (pytest)
    Steps: Run the full test_killswitch.py suite after obfuscation applied
    Expected: All 10 decision matrix tests pass (same as pre-obfuscation)
    Evidence: .sisyphus/evidence/task-9-obfuscated-still-works.txt

  Scenario: Sensitive strings not in plaintext
    Tool: Bash (grep)
    Steps: grep for "https://", server domain, "PHANTASTLAB_KILLED", ".phantastlab_kill" in src/services/killswitch*.py
    Expected: No matches found for any sensitive string
    Evidence: .sisyphus/evidence/task-9-no-plaintext.txt

  Scenario: Runtime deobfuscation works after obfuscation applied
    Tool: Bash (pytest)
    Steps: After obfuscation applied, call `deobfuscate_string()` with the encoded values and key. Verify the server URL and HMAC secret are recovered correctly.
    Expected: Deobfuscated strings match original plaintext values exactly
    Evidence: .sisyphus/evidence/task-9-deobfuscation.txt
  ```

  **Commit**: YES | Message: `feat(killswitch): apply string and code obfuscation` | Files: [src/services/killswitch.py, src/services/killswitch_persistence.py]

---

- [ ] 10. PyInstaller Hardening

  **What to do**: Update the PyInstaller spec with hardening measures compatible with current PyInstaller versions. The `--key` / `PyiBlockCipher` cipher feature has been removed from modern PyInstaller and raises `RemovedCipherFeatureError`. Instead, use these alternative hardening approaches:
  1. Open `PhantastLab.spec`
  2. Enable `strip=True` in the EXE section (currently `strip=False`) — removes debug symbols from the binary
  3. Set `optimize=2` in the Analysis section (currently `optimize=0`) — applies Python bytecode optimization (removes docstrings, asserts)
  4. Add killswitch modules to `hiddenimports` explicitly to ensure they're bundled: `hiddenimports=['src.services.killswitch', 'src.services.hw_fingerprint', 'src.services.killswitch_persistence', 'src.services.killswitch_hmac', 'src.services.killswitch_obfuscation']`
  5. Verify `src/services/killswitch*.py` files are included in the analysis
  6. Build the EXE: `pyinstaller PhantastLab.spec`
  7. Verify the built EXE runs correctly:
     - With mock server returning "ok" → app launches
     - With mock server returning "kill" → app exits silently
   8. Verify sensitive strings are not in the EXE binary: use `Select-String -Path dist/PhantastLab.exe -Pattern "https://" -Encoding byte` or a binary search approach

  **Why not PyiBlockCipher**: The `--key` / `cipher=block_cipher` mechanism (`pyimod02_crypto.PyiBlockCipher`) was removed from PyInstaller and raises `RemovedCipherFeatureError` at import time. The current hardening relies on: (1) string obfuscation in Task 8-9, (2) bytecode optimization (`optimize=2`), (3) symbol stripping (`strip=True`), and (4) the single-file EXE packaging itself.

  **Must NOT do**: Do not use `PyiBlockCipher` or `--key` (removed feature). Do not modify the app icon or metadata. Do not enable `console=True`.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: Small spec file change + verification build
  - Skills: [] — Standard PyInstaller configuration
  - Omitted: [`pyqt6-ui-development-rules`] — No UI changes

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: [F1-F4] | Blocked By: [7]

  **References**:
  - Current spec: `PhantastLab.spec` — Analysis on line 4-16, PYZ on line 17, EXE on line 19-38
  - `optimize` parameter: `PhantastLab.spec:15` — currently `optimize=0`, change to `optimize=2`
  - `strip` parameter: `PhantastLab.spec:28` — currently `strip=False`, change to `strip=True`
  - `hiddenimports`: `PhantastLab.spec:9` — currently `[]`, add killswitch module names
  - Build command: `pyinstaller PhantastLab.spec` — from project root
  - Removed cipher: `pyimod02_crypto.PyiBlockCipher` raises `RemovedCipherFeatureError` — do NOT use

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pyinstaller PhantastLab.spec` completes without errors
  - [ ] Built EXE exists in `dist/PhantastLab.exe`
  - [ ] EXE launches normally with mock server returning "ok"
  - [ ] EXE exits silently with mock server returning "kill"
  - [ ] `Select-String -Path dist/PhantastLab.exe -Pattern "kill" -Encoding byte` does not reveal killswitch URL in plaintext

  **QA Scenarios** (MANDATORY):
  ```
  Scenario: Build succeeds with hardening options
    Tool: Bash
    Steps: Run `pyinstaller PhantastLab.spec`. Check exit code.
    Expected: Exit code 0, dist/PhantastLab.exe exists
    Evidence: .sisyphus/evidence/task-10-build.txt

  Scenario: EXE respects killswitch
    Tool: Bash
    Steps: (1) Start mock server: `Start-Process python -ArgumentList "tests/mock_server.py --response kill --port 18765" -WindowStyle Hidden` (2) Set `$env:KILLSWITCH_URL_OVERRIDE="http://localhost:18765"` (3) Run `dist/PhantastLab.exe` and capture exit code
    Expected: Process exits with code 0 within 3s
    Evidence: .sisyphus/evidence/task-10-exe-kill.txt

  Scenario: Sensitive strings not extractable
    Tool: Bash (PowerShell)
    Steps: Run `[System.Text.Encoding]::ASCII.GetString([System.IO.File]::ReadAllBytes("dist/PhantastLab.exe"))` and search for server domain, HMAC secret plaintext
    Expected: Neither string found in the binary
    Evidence: .sisyphus/evidence/task-10-strings-check.txt
  ```

  **Commit**: YES | Message: `build(killswitch): harden PyInstaller spec with strip and optimize` | Files: [PhantastLab.spec]

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)
> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.
- [ ] F1. Plan Compliance Audit — oracle

  **What to do**: Verify every task in the plan has been implemented as specified. Check each acceptance criterion against actual code.
  **QA Scenarios**:
  ```
  Scenario: All acceptance criteria met
    Tool: Bash (pytest)
    Steps: Run killswitch tests `pytest tests/services/test_killswitch*.py tests/services/test_hw_fingerprint.py tests/services/test_killswitch_persistence.py tests/services/test_killswitch_hmac.py tests/services/test_killswitch_obfuscation.py -v`. Verify all pass.
    Expected: All killswitch tests pass, zero failures
    Evidence: .sisyphus/evidence/F1-test-results.txt

  Scenario: All plan files exist
    Tool: Bash
    Steps: Check each deliverable file exists: src/services/killswitch.py, src/services/hw_fingerprint.py, src/services/killswitch_persistence.py, src/services/killswitch_hmac.py, src/services/killswitch_obfuscation.py, server/worker.js, tests/services/test_killswitch.py
    Expected: All files exist and are non-empty
    Evidence: .sisyphus/evidence/F1-files-exist.txt

  Scenario: Decision matrix fully covered
    Tool: Bash (pytest)
    Steps: Run `pytest tests/services/test_killswitch.py -v -k "row"`. Count distinct row tests.
    Expected: At least 10 test functions covering all decision matrix rows
    Evidence: .sisyphus/evidence/F1-decision-matrix.txt
  ```

- [ ] F2. Code Quality Review — unspecified-high

  **What to do**: Lint and code quality review of all killswitch modules.
  **QA Scenarios**:
  ```
  Scenario: Ruff lint passes on all new files
    Tool: Bash
    Steps: Run `ruff check src/services/killswitch.py src/services/hw_fingerprint.py src/services/killswitch_persistence.py src/services/killswitch_hmac.py src/services/killswitch_obfuscation.py`
    Expected: Zero errors, zero warnings
    Evidence: .sisyphus/evidence/F2-ruff.txt

  Scenario: No PyQt in pure-Python modules
    Tool: Bash (PowerShell Select-String)
    Steps: Run `Select-String -Path src/services/hw_fingerprint.py,src/services/killswitch_obfuscation.py -Pattern "PyQt6"`
    Expected: No matches found
    Evidence: .sisyphus/evidence/F2-no-pyqt.txt

  Scenario: No hardcoded sensitive strings
    Tool: Bash (PowerShell Select-String)
    Steps: Run `Select-String -Path src/services/killswitch*.py -Pattern "https://","PHANTASTLAB_KILLED","killswitch/killed"`
    Expected: No plaintext matches
    Evidence: .sisyphus/evidence/F2-no-plaintext.txt
  ```

- [ ] F3. Real Manual QA — unspecified-high

  **What to do**: Run the actual application with mock server to verify killswitch behavior end-to-end.
  **Test Seam**: Use `KILLSWITCH_URL_OVERRIDE=http://localhost:18765` environment variable (added in Task 5) to redirect the killswitch to a local mock server. Start `tests/mock_server.py` before running the app.
  **QA Scenarios**:
  ```
  Scenario: App launches when server says ok
    Tool: Bash
    Steps: (1) Start mock server: `Start-Process python -ArgumentList "tests/mock_server.py --response ok --port 18765" -WindowStyle Hidden` (2) Set env: `$env:KILLSWITCH_URL_OVERRIDE="http://localhost:18765"` (3) Run `python src/main.py`. Wait 5s and check if process is still running via `Get-Process -Name python -ErrorAction SilentlyContinue`.
    Expected: python process is still running after 5s (killswitch allowed startup)
    Evidence: .sisyphus/evidence/F3-app-ok.txt

  Scenario: App exits when server says kill
    Tool: Bash
    Steps: (1) Start mock server: `Start-Process python -ArgumentList "tests/mock_server.py --response kill --port 18765" -WindowStyle Hidden` (2) Set env: `$env:KILLSWITCH_URL_OVERRIDE="http://localhost:18765"` (3) Run `python src/main.py` and capture exit code via `$LASTEXITCODE`.
    Expected: $LASTEXITCODE is 0, process exits within 3s, stdout and stderr are empty
    Evidence: .sisyphus/evidence/F3-app-kill.txt

  Scenario: App exits when killed and offline
    Tool: Bash
    Steps: (1) First run with kill response to set local flag (use Start-Process as above). (2) Stop mock server: `Stop-Process -Name python` (3) Remove KILLSWITCH_URL_OVERRIDE. (4) Run `python src/main.py` and check exit code.
    Expected: $LASTEXITCODE is 0 (fail-closed with flag, no server needed)
    Evidence: .sisyphus/evidence/F3-app-offline-killed.txt
  ```

- [ ] F4. Scope Fidelity Check — deep

  **What to do**: Verify no scope creep — no UI changes, no existing business logic modifications, no new dependencies.
  **QA Scenarios**:
  ```
  Scenario: No UI files modified
    Tool: Bash (git diff)
    Steps: Run `git diff --name-only` and check if any files in src/ui/ are modified
    Expected: Zero files in src/ui/ modified
    Evidence: .sisyphus/evidence/F4-no-ui.txt

  Scenario: No new dependencies added
    Tool: Bash
    Steps: Compare requirements_build.txt against git HEAD. Check no new lines added.
    Expected: requirements_build.txt unchanged
    Evidence: .sisyphus/evidence/F4-no-deps.txt

  Scenario: Existing tests still pass
    Tool: Bash (pytest)
    Steps: Run pre-existing test suite (excluding new killswitch tests)
    Expected: All pre-existing tests pass unchanged
    Evidence: .sisyphus/evidence/F4-existing-tests.txt
  ```

## Commit Strategy
- Atomic commits per task (see each task's commit message)
- Each commit must leave the codebase in a passing-test state
- Final verification commits are separate from implementation commits

## Success Criteria
1. All 10 rows of the startup decision matrix pass as automated tests
2. App silently exits (sys.exit(0)) when killed — no dialog, no traceback
3. App launches normally when allowed
4. Cloudflare Worker responds to `/check` with HMAC-signed responses
5. Hardware fingerprint is stable across restarts on the same machine
6. Kill flag persists across app restarts (all 3 backends)
7. Obfuscated strings are not readable via binary inspection of the EXE
8. PyInstaller build succeeds with strip + optimize hardening
9. Zero new third-party dependencies in Python client (JS server tooling excluded)
10. No PyQt imports in fingerprint or obfuscation modules
