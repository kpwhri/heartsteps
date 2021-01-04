import * as messaging from "messaging";
import { localStorage } from "local-storage";

import * as global from "../common/globals.js";

function getNewPin() {
  const url = `${global.BASE_URL}/api/pin_gen/myarr/`;
	return fetch(url)
  .then(response => response.json())
	.then(function(data) {
    console.log("Got new pin");
    console.log(data);
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
  console.log('update  watch staus');
  const pin = getPin();
  const authorization_token = getAuthorizationToken();
  if (!pin) {
    console.log("Fetching pin");
    getNewPin().then(function() {
      console.log("Got new pin");
      sendWatchStatus();
    })
    .catch(() => {
      console.log("Getting new pin failed?");
      sendWatchStatus();
    });
  } else if (!authorization_token) {
    console.log("Check paired")
    checkPaired().then(() => {
      console.log("Checked pairing");
      sendWatchStatus();
    })
    .catch(() => {
      console.log("Check pair failed");
    })
  } else {
    sendWatchStatus("Authorized");
  }
}

function getAuthorizationToken() {
  try{
    return localStorage.getItem("AUTHORIZATION_TOKEN");
  } catch(error) {
    console.log("Error getting authorization token");
    console.log(error);
    return false;
  }
}

function getPin() {
  try {
    return localStorage.getItem("PIN");
  } catch(error) {
    console.log("Error getting pin");
    console.log(error);
    return undefined;
  }
}

function clear() {
  localStorage.removeItem("PIN");
  localStorage.removeItem("PIN_UNIID");
  localStorage.removeItem("AUTHORIZATION_TOKEN");
}

function sendWatchStatus(statusMessage) {
  const authorizationToken = getAuthorizationToken();
  const pin = getPin();
  let authorized = false;
  if (authorizationToken) {
    authorized = true;
  }

  if(messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    messaging.peerSocket.send({
      status: statusMessage,
      pin: pin,
      authorized: authorized
    });
  } else {
    console.log("No phone, should debounce");
  }
}

function sendStepCounts(stepCounts) {
  console.log("Sending step counts");
  console.log(stepCounts);
  const url = `${global.BASE_URL}/api/watch-app/steps`;
  let token = getAuthorizationToken();
  if (token) {
    fetch(url, {
      method: "POST",
      body: JSON.stringify({
        "step_number": stepCounts
      }),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      }
    }).then(function(response) {
      if (response.status != 201) {
        console.log("ERROR: sendSteps completed with status "+ response.status);
        clear();
      } 
    }).catch(function(error) {
      console.error('Error in sendSteps: ', error);
    })
  } else {
    console.log("Not authorized to send step counts")
  }
}

messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.steps) {
    sendStepCounts(evt.data.steps);
  } else if (evt.data.key == global.CHECK_AUTH) {
    updateWatchStatus();
  }
}

