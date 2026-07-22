# Edge-IO Android Build Report

Generated: 2026-07-22T17:06:05Z

## Build result

**SUCCESS**

## Artifact

| Field | Value |
|---|---|
| APK path | `results/android/edge-io-debug.apk` (copy of `clients/android/app/build/outputs/apk/debug/app-debug.apk`) |
| APK size | 5763283 bytes |
| SHA-256 | `c0476831adf27d38d4be80dee0afe7ad084dcbce85fbb29a2c64110e163b549d` |
| Package name | `org.gunnchos.edgeio.debug` |
| Version name | `0.3.0-gate3` |
| Version code | `3` |
| Debuggable | yes (debug build) |
| Build command | `cd clients/android && gradle test assembleDebug` |
| Gradle version | 8.2 |
| Java version | openjdk version "21.0.10" 2026-01-20 |
| compileSdk | 34 |
| minSdk | 26 |
| targetSdk | 34 |

## Unit tests

`gradle test` — BUILD SUCCESSFUL (debug + release unit tests)

## Device preflight

```
List of devices attached
```

**Classification: NO_DEVICE**

Pixel 6a was not attached/authorized in this agent environment. Installation and on-device calibration were not performed.

Unlock the Pixel and accept the USB debugging authorization dialog when connecting, then re-run `adb devices -l` expecting `DEVICE_AUTHORIZED`.
