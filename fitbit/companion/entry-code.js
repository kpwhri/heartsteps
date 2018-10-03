import { settingsStorage } from "settings";
import * as messaging from "messaging";

import { ENTRY_CODE, INTEGRATION_STATUS_MESSAGE } from "../common/globals.js";

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
      console.log(response.headers.get('Content-Type'));
      for(let header of response.headers){
         console.log("header: " + header);
      }
      console.log("Authorization-Token: " + response.headers.get('Authorization-Token'));
      return response.json();
    })
    // May want to check for the auth token existence
    // And probably save it somewhere for location posts
    .then(function(jsonBody) {
      let heartsteps_id = jsonBody["heartstepsId"];
      console.log(`ID returned: ${heartsteps_id}`);
      if (heartsteps_id) {
        let integrationStatus = "enabled";
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

