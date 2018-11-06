import { settingsStorage } from "settings";
import * as messaging from "messaging";

import { AUTHORIZATION_TOKEN, BIRTH_YEAR, HEARTSTEPS_ID, ENTRY_CODE,
  INTEGRATION_STATUS_MESSAGE, isNotNull } from "../common/globals.js";

// export function sendSettingsData(data) {
//   // If we have a MessageSocket, send the data to the device
//   if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
//     messaging.peerSocket.send(data);
//   } else {
//     console.log("No peerSocket connection");
//   }
// }

export function enrollParticipant(ENTRY_CODE, BIRTH_YEAR){
  console.log("Hey, let's enroll!");
  let authTokenOk = false;
  let heartstepsIdOk = false;
  let integrationStatus = "not started";
  let enrollmentToken = {"enrollmentToken": ENTRY_CODE};
  const url = "https://heartsteps-kpwhri.appspot.com/api/enroll/";
  // Post entryCode as enrollmentToken
  fetch(url, {
    method: "POST",
    body: JSON.stringify(enrollmentToken),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  // Store the auth token that's returned
  .then(function(response) {
    console.log("Full response: " + response);
    let authorizationToken = response.headers.get('Authorization-Token');
    if (isNotNull(authorizationToken)) {
      settingsStorage.setItem(AUTHORIZATION_TOKEN, authorizationToken);
      authTokenOk = true;
      console.log("authToken: " + authorizationToken);
    }
    return response.json();
  })
  // Store the user identifier
  .then(function(jsonBody) {
    let heartstepsId = jsonBody["heartstepsId"];
    if (isNotNull(heartstepsId)) {
      settingsStorage.setItem(HEARTSTEPS_ID, heartsteps_id);
      heartstepsIdOk = true;
      console.log("heartsteps_id: " + heartsteps_id);
    }
    if (heartstepsIdOk) {
      if (authTokenOk) {
        integrationStatus = "enabled";
      } else {
        integrationStatus = "auth token invalid";
      }
    } else {
      if (authTokenOk) {
        integrationStatus = "user identifier invalid";
      } else {
        integrationStatus = "user id & auth token invalid";
      }
    }
    // Update integration message on watch
    settingsStorage.setItem(INTEGRATION_STATUS_MESSAGE, integrationStatus);
  })
  .catch(error => console.error('Error in enrollParticipant: ', error))
}

// deprecated
// export function updateEntryCode(key, val) {
//   if (key == ENTRY_CODE && val) {
//     sendSettingsData({
//         key: key,
//         value: JSON.parse(val)
//     });
//     // Pass entryCode as enrollmentToken to server
//     let entryCode = JSON.parse(val).name;
//     let enrollmentToken = {"enrollmentToken": entryCode};
//     const url = "https://heartsteps-kpwhri.appspot.com/api/enroll/";
//     fetch(url, {
//       method: "POST",
//       body: JSON.stringify(enrollmentToken),
//       headers: {
//         'Content-Type': 'application/json'
//       }
//     })
//     .then(function(response) {
//       console.log(response);
//       let authorizationToken = response.headers.get('Authorization-Token');
//       settingsStorage.setItem(AUTHORIZATION_TOKEN, authorizationToken);
//       console.log("authToken: " + authorizationToken);
//       return response.json();
//     })
//     // Save HeartstepsID and Auth token
//     .then(function(jsonBody) {
//       let heartsteps_id = jsonBody["heartstepsId"];
//       console.log("heartsteps_id: " + heartsteps_id);
//       if (heartsteps_id) {
//         let integrationStatus = "enabled";
//         settingsStorage.setItem(HEARTSTEPS_ID, heartsteps_id);
//       }
//       else {
//         let integrationStatus = "disenabled";
//       }
//       settingsStorage.setItem(INTEGRATION_STATUS_MESSAGE, integrationStatus);
//       sendSettingsData({
//         key: INTEGRATION_STATUS_MESSAGE,
//         value: integrationStatus
//       });
//     })
//     .catch(error => console.error('Error in updateEntryCode: ', error))
//   }
// }
