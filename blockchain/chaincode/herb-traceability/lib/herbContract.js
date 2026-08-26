"use strict";

const { Contract } = require("fabric-contract-api");

class HerbTraceabilityContract extends Contract {
  constructor() {
    super("HerbTraceabilityContract");
  }
}

module.exports = { HerbTraceabilityContract };
