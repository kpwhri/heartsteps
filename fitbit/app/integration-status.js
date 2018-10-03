import * as messaging from "messaging";
import document from "document";

const INTEGRATION_STATUS_ID = "hs-integration";

export function updateIntegrationStatus(status) {
  let txtIntegrationStatus = document.getElementById(INTEGRATION_STATUS_ID);
  txtIntegrationStatus.textContent = status;
}
