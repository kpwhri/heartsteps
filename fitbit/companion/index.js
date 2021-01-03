import * as messaging from "messaging";
import { localStorage } from "local-storage";

import * as global from "../common/globals.js";

function getNewPin() {
  const url = `${global.BASE_URL}/api/pin_gen/myarr/`;
	return fetch(url)
  .then(response => response.json())
	.then(function(data) {
    localStorage.setItem("PIN", data['pin']);
    localStorage.setItem("PIN_UNIID", data['uniid']);
    return data['pin'];
	});
}

function checkPaired() {
  const url = `${global.BASE_URL}/api/pin_gen/user/`;
	return fetch(url, {
		method: "POST",
	    body: JSON.stringify({
        "pin": localStorage.getItem("PIN"),
        "uniid": localStorage.getItem("PIN_UNIID")
      }),
	    headers: {
	      'Content-Type': 'application/json'
	    }
	})
  .then(function (response) {
    return response.json();
  })
	.then(function(data) {
    if (!data["authenticated"]) {
      return false;
		} else {
      localStorage.setItem("AUTHORIZATION_TOKEN", data["token"]);
      return true;
		}
	});
}

function updateWatchStatus() {
  const authorization_token = localStorage.getItem("AUTHORIZATION_TOKEN");
  const pin = localStorage.getItem("PIN");
  if (!pin || typeof pin == 'undefined') {
    sendWatchStatus("Loading");
    getNewPin().then(function() {
      sendWatchStatus("Pairing");
    })
  } else if (!authorization_token || typeof authorization_token == 'undefined') {
    console.log('Checking pair')
    sendWatchStatus("Loading");
    checkPaired().then((paired) => {
      if(paired) {
        sendWatchStatus("Authorized");
      } else {
        sendWatchStatus("Pairing");
      }
    })
    .catch(() => {
      sendWatchStatus("Error pairing");
    })
  } else {
    sendWatchStatus("Authorized");
  }
}

function sendWatchStatus(statusMessage) {
  const authorization_token = localStorage.getItem("AUTHORIZATION_TOKEN");
  const pin = localStorage.getItem("PIN");
  let authorized = false;
  if (authorization_token) {
    authorized = true;
  }

  if(messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    messaging.peerSocket.send({
      status: statusMessage,
      pin: pin,
      authorized: authorized
    });
  }
}

messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.key == global.RECENT_STEPS) {
    console.log('Not implemented!');
  } else if (evt.data.key == global.CHECK_AUTH) {
    updateWatchStatus();
  }
}

