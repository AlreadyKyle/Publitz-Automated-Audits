# Debug Network Issues on Mac

Your Mac is blocking connections to gaming APIs. Here's how to fix it:

---

## Quick Test - Check if APIs are reachable

Open Terminal and run these commands:

```bash
# Test Steam API
curl -I https://store.steampowered.com/app/1091500/

# Test SteamSpy API
curl -I https://steamspy.com/api.php

# Test RAWG API
curl -I https://api.rawg.io/api/games
```

**If these fail**, your Mac is blocking the connections.

---

## Common Causes & Fixes

### 1. VPN/Proxy Software

**Check if you're running:**
- Company VPN
- Personal VPN (NordVPN, ExpressVPN, etc.)
- Proxy software
- Antivirus with web filtering

**Fix:** Temporarily disable VPN/proxy and test again.

### 2. Firewall Settings

**Check:**
1. System Settings → Network → Firewall
2. If enabled, click "Firewall Options"
3. Make sure Python isn't blocked

**Fix:** Add Python to allowed applications or temporarily disable firewall.

### 3. Corporate Network

**If you're on a company network:**
- IT might be blocking gaming sites
- Try switching to personal WiFi or hotspot

### 4. Antivirus/Security Software

**Common culprits:**
- Norton
- McAfee
- Kaspersky
- Bitdefender

**Fix:** Add exception for Python or temporarily disable.

### 5. Mac Security Settings

**Check:**
1. System Settings → Privacy & Security
2. Look for network/firewall restrictions

---

## Test Without Network Restrictions

**Quick test:**
1. Disconnect from work VPN if applicable
2. Switch to phone hotspot if available
3. Run test again:
   ```bash
   cd ~/path/to/Publitz-Automated-Audits
   source venv/bin/activate
   python3 generate_audit.py --test
   ```

---

## If Nothing Works - Alternative Approach

We can modify the code to use a different network approach or add retry logic with exponential backoff.

Let me know what you find from the curl tests above.

---

*Created: December 9, 2025*
