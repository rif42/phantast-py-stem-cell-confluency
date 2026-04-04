# Draft: Killswitch Module

## Requirements (confirmed)
- **Trigger**: On app startup, before MainWindow shows
- **Check flow**: Internet available? → Contact server → Server responds "kill" / "ok" / "unkill"
- **Offline behavior**: If no internet, app opens normally (no kill check)
- **Kill permanence**: Server-controlled reversal (server can send "unkill" to re-enable)
- **Threat model**: Semi-technical users (registry editing, file deletion, basic reverse engineering)
- **Server**: Need to include server-side component (user doesn't have one yet)
- **Obfuscation**: Heavy — protect URLs, keys, logic from casual reverse engineering

## Technical Decisions
- Entry point: Hook into `src/main.py` `main()` function, BEFORE `MainWindow()` creation
- HTTP client: Use `urllib.request` (stdlib) to avoid adding `requests` dependency
- PyInstaller: Single-file EXE already configured, killswitch code bundled in

## Architecture Decisions (confirmed)
- **Server technology**: Cloudflare Worker (lightweight edge API)
- **Machine identification**: Per-machine — hardware ID (MAC + disk serial + hostname → SHA256 hash)
- **Local persistence**: 3 locations — (1) Windows Registry via QSettings, (2) hidden file in AppData, (3) environment variable
- **Server deployment**: Include `wrangler deploy` steps in plan
- **Handshake protocol**: GET /check?id=<machine_id> → "ok" | "kill" | "unkill"
- **"unkill" behavior**: Clears all local kill flags, re-enables app
- **HTTP client**: `urllib.request` (stdlib, no new dependency)

## Research Findings
- No existing HTTP/network code in project
- QSettings already used for persistence (Windows Registry backend)
- PyInstaller spec: `PhantastLab.spec` — single-file, no console, UPX enabled
- Dependencies are minimal: no `requests` lib available

## Policy Decisions (confirmed with user)
- **Offline + local kill flag → FAIL-CLOSED**: If server unreachable AND local kill flag exists → app BLOCKED. Fresh kill flags persist through offline periods.
- **Offline + no local flag → FAIL-OPEN**: If server unreachable AND no local kill flag → app opens normally.
- **HMAC-signed server responses**: Server signs responses with secret key, client verifies to prevent spoofing.
- **Startup latency budget**: 2 seconds max for network check, then fallback.
- **Phased approach**: Wave 1 = core killswitch + tests + server. Wave 2 = obfuscation + anti-tamper + PyInstaller hardening.

## Startup Decision Matrix
| Local Flag | Server Reachable | Server Response | Result |
|-----------|-----------------|-----------------|--------|
| No | Yes | "ok" | ✅ Open |
| No | Yes | "kill" | ❌ Block + set flags |
| No | Yes | "unkill" | ✅ Open |
| Yes | Yes | "ok" | ✅ Open + clear flags |
| Yes | Yes | "kill" | ❌ Block |
| Yes | Yes | "unkill" | ✅ Open + clear flags |
| No | No | N/A | ✅ Open (fail-open) |
| Yes | No | N/A | ❌ Block (fail-closed) |

## Obfuscation Strategy (semi-technical threat model)
- String obfuscation: XOR + base64 for URL, keys, flag names
- Code obfuscation: meaningless variable names, dead code injection, control flow flattening
- Anti-tampering: hash self-verification of killswitch module
- Anti-debugging: detect debugging tools, timing checks
- PyInstaller `--key` flag for bytecode encryption
- No PyArmor needed (semi-technical threat model doesn't justify the cost/complexity)

## Scope Boundaries
- INCLUDE: Client-side killswitch module, server-side endpoint, obfuscation, PyInstaller integration
- EXCLUDE: UI changes (killswitch is invisible), modifying existing business logic
