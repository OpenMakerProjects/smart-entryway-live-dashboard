# Validation results

On 2026-10-10 IST, GitHub Actions recovery run 37984331788 validated and decoded 55 UTF-8 chunks and pushed the original PNG to the same automation branch. Full gates explicitly ran on the decoded commit: pinned GPIOZero, smbus2, RPi.bme280 and Bless packages installed/imported; Python compilation passed; 8 unit tests passed (3 retained Controller, 2 packet/range, 3 PNG transport); the real localhost dashboard page and JSON endpoint smoke test passed; PNG/SVG/links/MIT/credential gates passed.

A ninth CLI compatibility subprocess regression test was added afterward and must pass on the final head before merge. PNG is 1315675 bytes, 1536×1024, SHA256 21a51af6f3dd8f5b5a316b8e800a391ca1bb3144bd275cc4e3b09b7d6144b035. No transport chunks remain.

This Linux Python application uses host compilation and HTTP tests, not an MCU board build. Physical Pi GPIO, BME280 accuracy, reed contact and actual BLE/BlueZ peripheral registration or radio notifications have not been tested. Final push/PR checks must pass before merge.
