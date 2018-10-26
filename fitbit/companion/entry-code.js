import { settingsStorage } from "settings";
import * as messaging from "messaging";

import { AUTHORIZATION_TOKEN, HEARTSTEPS_ID, ENTRY_CODE,
  INTEGRATION_STATUS_MESSAGE } from "../common/globals.js";

export function sendSettingsData(data) {
  // If we have a MessageSocket, send the data to the device
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    messaging.peerSocket.send(data);
  } else {
    console.log("No peerSocket connection");
  }
}

export function updateEntryCode(key, val) {
  if (key == ENTRY_CODE && val) {
    sendSettingsData({
        key: key,
        value: JSON.parse(val)
    });
    // If the user is authenticated
    // Pass entryCode as enrollmentToken to server
    let entryCode = JSON.parse(val).name;
    let enrollmentToken = {"enrollmentToken": entryCode};
    const url = "https://heartsteps-kpwhri.appspot.com/api/enroll/";
    fetch(url, {
      method: "POST",
      body: JSON.stringify(enrollmentToken),
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(function(response) {
      let authorizationToken = response.headers.get('Authorization-Token');
      settingsStorage.setItem(AUTHORIZATION_TOKEN, authorizationToken);
      return response.json();
    })
    // May want to check for the auth token existence
    // And probably save it somewhere for location posts
    .then(function(jsonBody) {
      let heartsteps_id = jsonBody["heartstepsId"];
      if (heartsteps_id) {
        let integrationStatus = "enabled";
        settingsStorage.setItem(HEARTSTEPS_ID, heartsteps_id);
      }
      else {
        let integrationStatus = "disenabled";
      }
      settingsStorage.setItem(INTEGRATION_STATUS_MESSAGE, integrationStatus);
      sendSettingsData({
        key: INTEGRATION_STATUS_MESSAGE,
        value: integrationStatus
      });
    })
    .catch(error => console.error('Error in updateEntryCode: ', error))
  }
}
