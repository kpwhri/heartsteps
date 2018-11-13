import { settingsStorage } from "settings";
import * as messaging from "messaging";

import * as global from "../common/globals.js";

// Send a message to the watch
export function sendData(data) {
  // If we have a MessageSocket, send the data to the device
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    messaging.peerSocket.send(data);
  } else {
    console.log("No peerSocket connection");
  }
}

export function enrollSettingsValid(entryCode, birthYear) {
  let currentYear = new Date().getFullYear();
  let birthYearValid = global.isNotNull(birthYear) &&
                     birthYear >= (currentYear-120) && birthYear <= currentYear;
  const entryCodeRe = /[A-Z]{4}-[A-Z]{4}/;
  // Uncomment this when we have XXXX-XXXX codes set up
  let entryCodeValid = global.isNotNull(entryCode) && entryCodeRe.test(entryCode);
  // let entryCodeValid = global.isNotNull(entryCode);
  let enrollValid = global.INITIALIZE_ENROLLMENT;
  if (entryCodeValid && birthYearValid) {
      enrollValid = global.VALID;
  } else if (entryCodeValid && !birthYearValid) {
      enrollValid = global.BIRTH_YEAR_INVALID;
  } else if (!entryCodeValid && birthYearValid) {
      enrollValid = global.ENTRY_CODE_INVALID;
  } else if (!entryCodeValid && !birthYearValid) {
      enrollValid = global.BIRTH_ENTRY_INVALID;
  } else {
      enrollValid = global.UNKNOWN_INVALID;
  }
  return enrollValid;
}

// Rethink this to give a return value
// Initialize a failure then overwrite as you continue
export function enrollParticipant(entry_code, birth_year) {
  let authTokenOk = false;
  let heartstepsIdOk = false;
  let enrollStatus = global.INITIALIZE_ENROLLMENT;
  const url = `${global.BASE_URL}/api/enroll/`;
  let authData = {
    "enrollmentToken": entry_code,
    "birthYear": birth_year
  };
  fetch(url, {
    method: "POST",
    body: JSON.stringify(authData),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  // Store the auth token that's returned
  .then(function(response) {
    // Test if return if valid - error text doesn't get me much anyway
    if (response["status"] == 200) {
      let authorizationToken = response.headers.get('Authorization-Token');
      if (global.isNotNull(authorizationToken)) {
        settingsStorage.setItem(global.AUTHORIZATION_TOKEN, authorizationToken);
        authTokenOk = true;
      }
      return response.json();
    } else {
      settingsStorage.setItem(global.INTEGRATION_STATUS_MESSAGE, global.CANNOT_AUTHENTICATE);
      sendData({
        key: global.INTEGRATION_STATUS_MESSAGE,
        value: settingsStorage.getItem(global.INTEGRATION_STATUS_MESSAGE)
      });
      throw `HTTP Response Status ${response["status"]}`;
    }
  })
  // Store the user identifier
  .then(function(jsonBody) {
    let heartstepsId = jsonBody["heartstepsId"];
    if (global.isNotNull(heartstepsId)) {
      settingsStorage.setItem(global.HEARTSTEPS_ID, heartstepsId);
      heartstepsIdOk = true;
    }
    if (heartstepsIdOk) {
      if (authTokenOk) {
        enrollStatus = global.VALID;
      } else {
        enrollStatus = global.AUTH_INVALID;
      }
    } else {
      if (authTokenOk) {
        enrollStatus = global.ID_INVALID;
      } else {
        enrollStatus = global.AUTH_ID_INVALID;
      }
    }
    settingsStorage.setItem(global.INTEGRATION_STATUS_MESSAGE, enrollStatus);
    sendData({
      key: global.INTEGRATION_STATUS_MESSAGE,
      value: settingsStorage.getItem(global.INTEGRATION_STATUS_MESSAGE)
    });
  })
  .catch(error => console.error('Error in enrollParticipant: ', error))
}
