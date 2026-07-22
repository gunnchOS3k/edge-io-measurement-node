# FILEPROVIDER_FIX_AND_RECOVERY_NOTES

## Failed export (preserved)

| Field | Value |
|---|---|
| Run ID | `pixel-cal-1784755600830` |
| Measurement | completed (~60.6s, 13 samples) |
| Cache write | success |
| Share export | FAILED — FileProvider authority mismatch |
| Recovery | `adb exec-out run-as … cat cache/pixel-cal-1784755600830.json` |
| Raw SHA-256 | `f19d15bc3f12e5e072f50847eff3dad89728b717d0f59f24e68b92cbe4d48ab8` |
| Privacy | PASS |
| Schema as physical evidence | FAIL (`consent.status=withdrawn`, `producer.commit=unknown_local_build`) |
| Pilot count | excluded |

## Root cause

- Manifest: `${applicationId}.provider` → `org.gunnchos.edgeio.debug.provider`
- Code used: `$packageName.files` → mismatch

## Fix (versionCode 5 / 0.3.2-gate3-android)

- Centralized `EdgeIoFileProvider.authority(BuildConfig.APPLICATION_ID)`
- Share intent uses matching authority + `FLAG_GRANT_READ_URI_PERMISSION` + `application/json`
- Full exception diagnostics on status + logcat (`EdgeIoExport`)
- Session retained after share failure; EXPORT SESSION retryable
- Secondary `CreateDocument` save path (no broad storage permission)
- Consent frozen at session start for export evidence
- `producer.commit` from `BuildConfig.GIT_COMMIT`
- Regression unit tests for authority + frozen consent

## New build

| Field | Value |
|---|---|
| versionName | `0.3.2-gate3-android` |
| versionCode | `5` |
| SHA-256 | `62f0b68320eaf08b409dc2e5685ac27813668a2443f3883ec0c69ba184fc404a` |
| Install | Success |
| Launch | MainActivity resumed, no crash |
| Merged manifest authority | `org.gunnchos.edgeio.debug.provider` |
