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
      console.log(response);
      let authorizationToken = response.headers.get('Authorization-Token');
      settingsStorage.setItem(AUTHORIZATION_TOKEN, authorizationToken);
      console.log("authToken: " + authorizationToken);
      return response.json();
    })
    // Save HeartstepsID and Auth token
    .then(function(jsonBody) {
      let heartsteps_id = jsonBody["heartstepsId"];
      console.log("heartsteps_id: " + heartsteps_id);
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
