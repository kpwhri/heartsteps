import * as messaging from "messaging";
import document from "document";

const INTEGRATION_STATUS = "integrationStatus";
let txtIntegrationStatus = document.getElementById("hs-integration");

export function updateIntegrationStatus(evt) {
  // Phone updates integrationStatus depending on result
  if (evt.data.key == INTEGRATION_STATUS) {
    txtIntegrationStatus.textContent = evt.data.value;
  }
}
