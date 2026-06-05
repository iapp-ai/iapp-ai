/**
 * iApp AI — Node.js SDK + MCP server launcher.
 *
 * Legacy v1.x usage keeps working:
 *     const iapp_ai = require("iapp_ai");
 *     const client = new iapp_ai("YOUR_API_KEY");
 *
 * Modern SDK (v2+):
 *     const { IAppClient } = require("iapp_ai");
 *     const client = new IAppClient("YOUR_API_KEY");
 */
"use strict";

const legacy = require("./modules_ai");
const { IAppClient, IAppError, API_BASE } = require("./client");

// Default export stays the legacy class for v1.x compatibility; the modern
// client is attached as named properties.
legacy.IAppClient = IAppClient;
legacy.IAppError = IAppError;
legacy.API_BASE = API_BASE;

module.exports = legacy;
