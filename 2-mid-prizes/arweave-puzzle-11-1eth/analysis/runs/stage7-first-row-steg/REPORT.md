# Stage 7 — historical first-row private-key stego protocol

Targeted reference: public surg0r/steg code from 2015. It hides a private-key string in consecutive first-row R-channel LSBs, with one length byte and a four-character SHA-256 checksum suffix.

- Protocol/order variants checked: 2048
- Variants with any supported checksum match: 0
- Exact Ethereum target match: false

## Canonical surg0r-style read of this image

- First decoded length byte: 255
- Bytes available after length: 199

The first-row anomaly makes this family historically relevant, but this bounded test found no winning key and records no candidate payload.
