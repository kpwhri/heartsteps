// Get integrationStatus setting & update text in settings
import * as messaging from "messaging";
import document from "document";
import { getIntegrationStatus } from "./integration-status";

import { geolocation } from "geolocation";

messaging.peerSocket.onmessage = getIntegrationStatus;

// Will need to wake the companion up on occasion
// https://dev.fitbit.com/build/guides/companion/
geolocation.enableHighAccuracy = true
geolocation.getCurrentPosition(locationSuccess, locationError);

function locationSuccess(position) {
    console.log("Latitude: " + position.coords.latitude,
                "Longitude: " + position.coords.longitude);
}

function locationError(error) {
  console.log("Error: " + error.code,
              "Message: " + error.message);
}
