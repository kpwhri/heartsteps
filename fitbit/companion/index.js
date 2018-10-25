import { settingsStorage } from "settings";
import * as messaging from "messaging";
import { me } from "companion";
import companion from "companion";

// Post entryCode to server and display result
import { sendSettingsData, updateEntryCode } from "./entry-code";

// Get location
import { geolocation } from "geolocation";
import { locationSuccess, locationError } from "./location";

import { ANTI_SEDENTARY_MESSAGE, ENTRY_CODE, INTEGRATION_STATUS_MESSAGE,
   QUERY_STEP_MESSAGE } from "../common/globals.js";

// Tell the device to check steps every 5 minutes
const WAKE_INTERVAL = 5;

/************************************************************
  Look for when Entry Code is updated in watch settings
  and send that code to the HeartSteps server for validation.
*************************************************************/
// Event fires when a setting is changed
settingsStorage.onchange = function(evt) {
  updateEntryCode(evt.key, evt.newValue);
}

// Settings were changed while the companion was not running
if (me.launchReasons.settingsChanged) {
  // Send the value of the setting
  updateEntryCode(ENTRY_CODE, settingsStorage.getItem(ENTRY_CODE));
}

/*****************************************************************
  Tell the device to query watch for step count every X minutes.
  Only allow this if user is authenticated.
*****************************************************************/
const MILLISECONDS_PER_MINUTE = 1000 * 60;
// me.wakeInterval does NOT seem to wake the phone-side app
me.wakeInterval = (WAKE_INTERVAL * MILLISECONDS_PER_MINUTE) + 1;
console.log("Wake interval set to " + me.wakeInterval);

companion.wakeInterval = (WAKE_INTERVAL * MILLISECONDS_PER_MINUTE);
console.log ("Me.wakeinterval = " + me.wakeInterval);
console.log ("Companion.wakeinterval = " + companion.wakeInterval);

// Just something to run to ensure another function's getting called
function testFunction(){
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    // messaging.peerSocket.send(QUERY_STEP_MESSAGE);
    console.log("Phone side: Repeated run a success");
    console.log("Current time: "+ Date.now());
  } else {
    // Close the companion and wait to be awoken
    console.log("Phone side: No peerSocket connection");
    console.log("Current time: "+ Date.now());
    me.yield();
  }
}



// Set the companion onWakeInterval (instead of me.wakeInterval)
// Stops as soon as the screen goes off on the phone
me.onwakeinterval = function(evt) {
  // The companion started due to a periodic timer
  console.log("Phone side: Started due to new me.onwakeinterval!");
  testFunction();
  // Message socket opens
  // Is this actually necessary?
  messaging.peerSocket.onopen = () => {
    console.log("PhoneSide: Companion Socket Open (me)");
  };
}

// This is the code modified from the doco
// Never seems to run
// This only runs if companion is NOT running
// Otherwise check for .onwakeinterval
if (me.launchReasons.wokenUp) {
  // The companion started due to a periodic timer
  console.log("Started due to me.launchReasons.wokenUp!");
  testFunction();
  // Message socket opens
  // Is this actually necessary?
  messaging.peerSocket.onopen = () => {
    console.log("Phone Side: Companion Socket Open (me)");
  };
}

// From Dischord channel
if (companion.launchReasons.wokenUp) {
  // The companion started due to a periodic timer
  console.log("Started due to companion.launchReasons.wokenUp!");
  testFunction();
  // Message socket opens
  // Is this actually necessary?
  messaging.peerSocket.onopen = () => {
    console.log("Phone Side: Companion Socket Open (companion)");
  };
}

// Standard JS setInterval
// But only runs when the app is active
setInterval(function() {
  if (messaging.peerSocket.readyState != messaging.peerSocket.OPEN) {
    console.log ("Phone Side: Connection problem - peerSocket not OPEN");
  } else {
    console.log ("Phone Side: setInterval good to go");
    testFunction();
 }
}, WAKE_INTERVAL*MILLISECONDS_PER_MINUTE);

// Listen for message sent by watch
messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.key == "testFunction") {
    console.log("Phone side:  Hey, the watch sent a message!");
  } else {
    console.log("Phone side: something else: " + evt.data.key);
  }
}

// Listen for socket to be opened by watch
messaging.peerSocket.open = function() {
  console.log("Phone side:  Hey, socket's open!");
}

// Listen for the onerror event
messaging.peerSocket.onerror = function(err) {
  // Handle any errors
  console.log("Phone side Connection error: " + err.code + " - " + err.message);
}


/***************************************
  Send location data to the server
  Only allow this if user is authenticated.
  The lat/long look weird - check the projection
  How to send the User with this?
***************************************/
const PLACE_SOURCE = "watch";
function sendLocation(lat, long, place) {
  const url = "https://heartsteps-kpwhri.appspot.com/api/locations/";
  let data = {"latitude": lat, "longitude": long, source: PLACE_SOURCE};
  fetch(url, {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(function(response) {
    // if (response.status == 201)
    console.log("Succeeded with status " + response.status);
  }).catch(error => console.error('Error in sendLocation: ', error))
}

// Get location
geolocation.enableHighAccuracy = true;
geolocation.getCurrentPosition(locationSuccess, locationError);
