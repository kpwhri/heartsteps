import * as messaging from "messaging";
import document from "document";

const INTEGRATION_STATUS_ID = "hs-integration";

export function updateIntegrationStatus(status) {
  document.getElementById(INTEGRATION_STATUS_ID).textContent = status;
}
