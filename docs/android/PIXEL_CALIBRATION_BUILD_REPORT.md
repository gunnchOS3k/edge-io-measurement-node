# PIXEL_CALIBRATION_BUILD_REPORT

Generated: 2026-07-22T18:29:37Z

## Build

| Field | Value |
|---|---|
| Result | SUCCESS |
| APK path | `clients/android/app/build/outputs/apk/debug/app-debug.apk` |
| Size | 5775971 bytes |
| SHA-256 | `98b4c9dcb4e36df1177e35e7a9c845aa54542b20c81a667a37dbed665f9a0f4a` |
| Prior SHA-256 | `c0476831adf27d38d4be80dee0afe7ad084dcbce85fbb29a2c64110e163b549d` |
| Hash comparison | **CHANGED** — expected after Android calibration exporter hardening (versionCode 4 / 0.3.1-gate3-android) |
| Package | `org.gunnchos.edgeio.debug` |
| Version name | `0.3.1-gate3-android` |
| Version code | `4` |
| Debuggable | yes |
| minSdk | 26 |
| targetSdk | 34 |
| Permissions | INTERNET, ACCESS_NETWORK_STATE |
| Build command | `cd clients/android && gradle clean test assembleDebug` |
| Unit tests | PASS (ConsentManager + SessionExporter) |

## Device preflight (this agent environment)

```
List of devices attached
```

**Classification: NO_DEVICE**

This cloud agent cannot see a USB device attached to Edmund’s Mac. USB-C connection on the Mac does not pass through to the remote Linux runner.

### How to make the Pixel visible

**Option A — wireless debugging (preferred for this agent)**

1. On Pixel: Developer options → Wireless debugging → Pair device with pairing code.
2. Note IP:port and pairing code.
3. Tell the agent the pairing host/port/code, or run:
   ```
   adb pair <ip>:<pair_port>
   adb connect <ip>:<debug_port>
   adb devices -l
   ```
4. Expect `DEVICE_AUTHORIZED`.

**Option B — local Mac install**

On the Mac that has the Pixel via USB-C:

```
adb devices -l
adb install -r /path/to/app-debug.apk
adb shell am start -n org.gunnchos.edgeio.debug/org.gunnchos.edgeio.MainActivity
```

Then complete consent/calibration manually and share/export the JSON into a path this agent can read.

## Install / launch

Not performed in this environment (NO_DEVICE). No fabricated install.
