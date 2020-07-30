import { me } from "companion";
import { geolocation } from "geolocation";
import * as messaging from "messaging";
import { settingsStorage } from "settings";

import * as simpleSettings from "./simple/companion-settings";
import * as global from "../common/globals.js";

import { locationSuccess, locationError } from "./location";
import { enrollParticipant, enrollSettingsValid, sendData }
  from "./enrollment";

simpleSettings.initialize();

/* -- On initialization, check if authentication -- */
/* -- is set up and remove warnings if so        -- */

/************************************************************
  Set integrationStatus in settings based on Entry Code & Birth Year
  Send to HeartSteps server for validation.
*************************************************************/
function updateEnrollStatus(evtKey){
  if (evtKey == global.ENTRY_CODE || evtKey == global.BIRTH_YEAR) {
    let entryCode = global.parseSettingsValue(settingsStorage.getItem(global.ENTRY_CODE)).toUpperCase();
    let birthYr = global.parseSettingsValue(settingsStorage.getItem(global.BIRTH_YEAR));
    let enrollValid = enrollSettingsValid(entryCode, birthYr);
    if (enrollValid == global.VALID) {
      enrollParticipant(global.parseSettingsValue(settingsStorage.getItem(global.ENTRY_CODE)),
                        global.parseSettingsValue(settingsStorage.getItem(global.BIRTH_YEAR)))
    } else {
      settingsStorage.setItem(global.INTEGRATION_STATUS_MESSAGE, enrollValid);
      sendData({
        key: global.INTEGRATION_STATUS_MESSAGE,
        value: settingsStorage.getItem(global.INTEGRATION_STATUS_MESSAGE)
      });
    }
  }
}

// Update status when setting is changed
// The newValue is already set in settingsStorage
settingsStorage.onchange = function(evt) {
  if (evt.key == global.ENTRY_CODE || evt.key == global.BIRTH_YEAR) {
    let enrollStatus = updateEnrollStatus(evt.key);
  }
}

// Update status if settings changed while companion not running
if (me.launchReasons.settingsChanged) {
  // Give this a try at any time, in case it's enrollment
  let enrollStatus = updateEnrollStatus(global.ENTRY_CODE);
}

/***************************************
  Send location data to the server
***************************************/
const PLACE_SOURCE = "watch";
function sendLocation(lat, long, place) {
  let token = settingsStorage.getItem(global.AUTHORIZATION_TOKEN);
  if (token) {
    const url = `${global.BASE_URL}/api/locations/`;
    let data = {"latitude": lat, "longitude": long, source: PLACE_SOURCE};
    fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      }
    }).then(function(response) {
      if (response.status != 201) {
        console.log("ERROR: sendLocation completed with status "+ response.status);
      }
    }).catch(error => console.error('Error in sendLocation: ', error))
  } else {
    console.log("ERROR in sendLocation: user not authenticated");
  }
}

// Get location
function sendLatLong() {
  let geo = {};
  geolocation.getCurrentPosition(
    (position) => {
      sendLocation(position.coords.latitude, position.coords.longitude, PLACE_SOURCE);
    },
    (error) => {
      sendLocation(0, 0, PLACE_SOURCE);
    },
    { "enableHighAccuracy" : true }
  );
  }

// Send step data to server
function sendSteps(step_count, step_dtm) {
  const url = `${global.BASE_URL}/api/watch-app/steps`;
  let data = {"step_number": step_count, "step_dtm": step_dtm};
  let token = settingsStorage.getItem(global.AUTHORIZATION_TOKEN);
  if (token) {
    fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      }
    }).then(function(response) {
      if (response.status != 201) {
        console.log("ERROR: sendSteps completed with status "+ response.status);
      }
    }).catch(error => console.error('Error in sendSteps: ', error))
  } else {
    console.log("ERROR in sendSteps: user not authenticated");
  }
}

/*--- ClockFacePin authentication process ---*/
/*--- sends request for pin ---*/
function getPin() {
  const url = `${global.BASE_URL}/api/pin_gen/myarr/`;
	return fetch(url)
  .then(response => response.json())
	.then(function(data) {
    settingsStorage.setItem(global.AUTHORIZATION_PIN, data['pin']);
    settingsStorage.setItem(global.PIN_UUID, data['uniid']);
		if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
      messaging.peerSocket.send(settingsStorage.getItem(global.AUTHORIZATION_PIN));
		}
	})
  .catch(error => console.error('Error in getPin: ', error));
}

/*--- checks if pin is connected to user ---*/
function getUser() {
  const url = `${global.BASE_URL}/api/pin_gen/user/`;
  console.log("pin: ", settingsStorage.getItem(global.AUTHORIZATION_PIN));
  console.log("uniid: ", settingsStorage.getItem(global.PIN_UUID));
  let p = {
    "pin": settingsStorage.getItem(global.AUTHORIZATION_PIN),
    "uniid": settingsStorage.getItem(global.PIN_UUID)
  };
	return fetch(url, {
		method: "POST",
	    body: JSON.stringify(p),
	    headers: {
	      'Content-Type': 'application/json'
	    }
	})
  .then(response => response.json())
	.then(function(data) {
    if (!data["authenticated"]) {
      console.log("ERROR: Pin not associated with user");
			if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
        messaging.peerSocket.send(settingsStorage.getItem(global.AUTHORIZATION_PIN));
			}
		} else {
      settingsStorage.setItem(global.AUTHORIZATION_TOKEN, data["token"]);
			if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
        messaging.peerSocket.send("Authenticated");
			}
		}
	})
  .catch(error => console.error('Error in getUser: ', error));
}

function sendPinAuthToPhone() {
  let pauth = settingsStorage.getItem(global.AUTHORIZATION_PIN);
  let tauth = settingsStorage.getItem(global.AUTHORIZATION_TOKEN);

  // if no pin, get pin
  if (!pauth) {
    getPin();
  } else if (!tauth) { // have pin, no token
    getUser();
  } else { // has pin & token; user already authenticated
    if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
      messaging.peerSocket.send("Authenticated");
    }
  }
}

// on init, check for pin & auth token
sendPinAuthToPhone();

/*--- When phone receives step data message from watch ---*/
/*--- forward Step & Location data to server           ---*/
messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.key == global.RECENT_STEPS) {
    sendLatLong();
    sendSteps(evt.data.value, evt.data.time);
  } else if (evt.data.key == global.CHECK_AUTH) {
    getUser();
  } else {
    return {};
  }
}

settingsStorage.clear();