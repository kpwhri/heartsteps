import { settingsStorage } from "settings";
import * as messaging from "messaging";
import { me } from "companion";

const ENTRY_CODE = "entryCode";
const INTEGRATION_STATUS = "integrationStatus";

// Event fires when a setting is changed
settingsStorage.onchange = function(evt) {
  updateEntryCode(evt.key, evt.newValue);
}

// Settings were changed while the companion was not running
if (me.launchReasons.settingsChanged) {
  // Send the value of the setting
  updateEntryCode(ENTRY_CODE, settingsStorage.getItem(ENTRY_CODE));
}

function updateEntryCode(key, val) {
  if (key == ENTRY_CODE && val) {
    sendSettingsData({
        key: key,
        value: JSON.parse(val)
    });
    // If the user is authenticated
    // Pass entryCode as enrollmentToken to server
    let entryCode = {enrollmentToken: JSON.parse(val).name};
    let heartsteps_id = '';
    const url = "https://heartsteps-kpwhri.appspot.com/api/enroll/";
    fetch(url, {
      method: "POST",
      body: JSON.stringify(entryCode),
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(function(response) {
      console.log(response.headers.get('Content-Type'));
      return response.json();
    })
    .then(function(jsonBody){
      heartsteps_id = jsonBody["heartstepsId"];
      console.log(`ID: ${heartsteps_id}`);
    })
    .catch(error => console.error('Error: ', error))
    if (entryCode == "111111") {
      settingsStorage.setItem(INTEGRATION_STATUS, "enabled");
      sendSettingsData({
        key: INTEGRATION_STATUS,
        value: "enabled"
      });
    }
    else {
      console.log("EntryCode validation failure");
    }
  }
}

function sendSettingsData(data) {
  // If we have a MessageSocket, send the data to the device
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    messaging.peerSocket.send(data);
  } else {
    console.log("No peerSocket connection");
  }
}
