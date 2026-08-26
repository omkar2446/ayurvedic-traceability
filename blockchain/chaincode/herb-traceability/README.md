# Herb Traceability Chaincode

This package is the Hyperledger Fabric chaincode component for Ayurvedic herb provenance.

## Phase 1 scope

Phase 1 creates a real Fabric Contract API project and exports `HerbTraceabilityContract`. It does not create a network, channel, ledger records, or business transactions yet. Batch, custody, laboratory, processing, product, recall, and history functions begin in later phases.

## Prerequisites

- Node.js 18 or newer
- npm
- Hyperledger Fabric binaries and Docker for later network phases

## Install and load-check

From this directory:

```powershell
npm install
npm run load-check
```

Expected output:

```text
HerbTraceabilityContract loaded
```

The package exports the contract in the form required by Fabric chaincode packaging:

```js
const { HerbTraceabilityContract } = require("./lib/herbContract");
module.exports.contracts = [HerbTraceabilityContract];
```

## Later phases

The official Hyperledger Fabric test network will be used later. This project will not copy the Fabric samples repository into the application. Network startup, channel creation, deployment, and transaction tests are intentionally deferred until the corresponding phases.
