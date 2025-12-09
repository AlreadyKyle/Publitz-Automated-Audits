# Debug Network Issues on Mac

If you're getting API errors, connection timeouts, or proxy errors, use this guide.

---

## Quick Network Test

**Run this first to see what's working:**

```bash
cd ~/Documents/GitHub/Publitz-Automated-Audits
source venv/bin/activate
python test_network.py
```

**What to expect:**
- The script tests Steam, SteamSpy, RAWG, and Claude APIs
- Should take 30-60 seconds
- Shows ✅ or ❌ for each API
- Gives specific error messages

---

## Understanding Test Results

### ✅ All Tests Pass

```
🎉 ALL TESTS PASSED - Your system can reach all required APIs!
```

**Action:** No network issues. Your system should work fine.

---

### ❌ Some Tests Fail

```
⚠️  SOME TESTS FAILED

❌ BLOCKED   - Steam Store
✅ WORKING   - SteamSpy
❌ BLOCKED   - RAWG
✅ WORKING   - Claude AI
```

**Action:** See "Common Causes" section below.

---

## Manual curl Tests

If you want to test each API individually:

### Test Steam Store API

```bash
curl -I https://store.steampowered.com/app/1091500/
```

**Success:** You'll see `HTTP/2 200` or `HTTP/1.1 200`
**Failure:** Timeout, connection refused, or proxy error

---

### Test SteamSpy API

```bash
curl -I https://steamspy.com/api.php
```

**Success:** `HTTP/1.1 200 OK`
**Failure:** Connection error

---

### Test RAWG API

```bash
curl -I https://api.rawg.io/api/games
```

**Success:** `HTTP/1.1 200 OK` or `HTTP/2 200`
**Failure:** Connection refused or timeout

---

### Test Claude AI API

```bash
curl -I https://api.anthropic.com/
```

**Success:** Any 2xx or 4xx response (404 is fine - endpoint exists)
**Failure:** Connection refused or timeout

---

## Common Causes & Fixes

### 1. VPN/Proxy Blocking Requests

**Symptoms:**
- ProxyError messages
- "Unable to connect to proxy"
- "Tunnel connection failed: 403 Forbidden"

**Check if you're running:**
- Company VPN (Cisco, Pulse Secure, etc.)
- Personal VPN (NordVPN, ExpressVPN, Surfshark, etc.)
- Proxy software
- Antivirus with web filtering

**Fix:**
1. Disconnect from VPN
2. Disable proxy in System Settings
3. Run test again:
   ```bash
   python test_network.py
   ```

---

### 2. Corporate Network Restrictions

**Symptoms:**
- Specific gaming sites blocked
- Works on home WiFi but not work WiFi
- Some APIs work, others don't

**Check:**
- Are you on company WiFi?
- Does your company block gaming sites?
- Is IT monitoring/filtering web traffic?

**Fix:**
1. Switch to personal WiFi network
2. Use phone hotspot temporarily
3. Run test again

---

### 3. Firewall Blocking Python

**Symptoms:**
- All curl tests pass
- But Python script fails
- "Connection refused" in Python only

**Check macOS Firewall:**
1. System Settings → Network → Firewall
2. Click "Firewall Options"
3. Look for Python in blocked applications

**Fix:**
1. Add Python to allowed applications
2. Or temporarily disable firewall:
   - Turn off Firewall
   - Run test
   - Turn Firewall back on after confirming it's the issue

---

### 4. Antivirus/Security Software Blocking

**Symptoms:**
- Intermittent connection failures
- "SSL certificate" errors
- "Connection reset by peer"

**Common culprits:**
- Norton
- McAfee
- Kaspersky
- Bitdefender
- Malwarebytes
- Little Snitch

**Fix:**
1. Temporarily disable antivirus
2. Run test:
   ```bash
   python test_network.py
   ```
3. If test passes, add Python exception in antivirus
4. Re-enable antivirus with exception

---

### 5. DNS Issues

**Symptoms:**
- "Name or service not known"
- "Could not resolve host"
- Intermittent connection failures

**Fix:**
1. Try changing DNS servers:
   - System Settings → Network → Advanced → DNS
   - Add Google DNS: `8.8.8.8` and `8.8.4.4`
   - Or Cloudflare DNS: `1.1.1.1` and `1.0.0.1`
2. Run test again

---

### 6. ISP Blocking/Throttling

**Symptoms:**
- Slow connections
- Timeouts after long wait
- Works on different network

**Check:**
- Does it work on phone hotspot?
- Does it work on different WiFi network?

**Fix:**
- Use different network temporarily
- Contact ISP if systematic blocking

---

## Advanced Diagnostics

### Check for Proxy Environment Variables

```bash
echo $HTTP_PROXY
echo $HTTPS_PROXY
echo $NO_PROXY
```

**If these show values**, you have system-wide proxy configured.

**Fix:**
```bash
unset HTTP_PROXY
unset HTTPS_PROXY
unset NO_PROXY
```

Then run test again.

---

### Check Python's Proxy Settings

```bash
python -c "import os; print('HTTP_PROXY:', os.environ.get('HTTP_PROXY')); print('HTTPS_PROXY:', os.environ.get('HTTPS_PROXY'))"
```

**If these show values**, Python is using proxy.

**Fix:** Unset as shown above.

---

### Verify SSL Certificates

```bash
python -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

**Should show:** OpenSSL version info
**If error:** SSL libraries not properly installed

---

## System Settings to Check

### Network Settings

```
System Settings → Network
→ Check active connection (WiFi/Ethernet)
→ Advanced → Proxies
→ Make sure all proxy settings are OFF
```

---

### Firewall Settings

```
System Settings → Network → Firewall
→ If ON, check options
→ Make sure Python is not blocked
→ Consider turning OFF temporarily to test
```

---

### Privacy & Security

```
System Settings → Privacy & Security
→ Check for network restrictions
→ Check for app restrictions
```

---

## Test Without Restrictions

### Quick Isolation Test

1. **Disconnect from work VPN** (if applicable)
2. **Switch to phone hotspot**:
   - iPhone: Settings → Personal Hotspot → Turn On
   - Android: Settings → Network → Hotspot
   - Connect Mac to your phone's hotspot
3. **Run test**:
   ```bash
   cd ~/Documents/GitHub/Publitz-Automated-Audits
   source venv/bin/activate
   python test_network.py
   ```

**If this works:** Your regular network/VPN is blocking the APIs
**If this fails:** System-level blocking (firewall, antivirus, etc.)

---

## When All Else Fails

### Nuclear Option: Network Reset

```bash
# Flush DNS cache
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Reset network preferences (WARNING: Will forget WiFi passwords)
sudo rm /Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist
sudo rm /Library/Preferences/SystemConfiguration/NetworkInterfaces.plist
sudo rm /Library/Preferences/SystemConfiguration/preferences.plist
```

**After reset:**
1. Restart Mac
2. Reconnect to WiFi
3. Run test

---

## Reporting Network Issues

**If you've tried everything and still failing, send me:**

1. **Output of network test:**
   ```bash
   python test_network.py 2>&1 | tee network_test_output.txt
   ```

2. **Output of curl tests:**
   ```bash
   curl -v https://store.steampowered.com/app/1091500/ 2>&1 | tee curl_test_output.txt
   ```

3. **Your network setup:**
   - VPN? (Yes/No, which one?)
   - Corporate network? (Yes/No)
   - Antivirus? (Which one?)
   - Firewall on? (Yes/No)
   - Mac model & macOS version

---

*Last Updated: December 9, 2025*
