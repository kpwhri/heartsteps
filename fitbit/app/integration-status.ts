import * as messaging from "messaging";
import document from "document";

const INTEGRATION_STATUS_ID: string = "hs-integration";

export function updateIntegrationStatus(status: string) {
  document.getElementById(INTEGRATION_STATUS_ID).textContent = status;
}
