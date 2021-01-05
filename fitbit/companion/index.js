import * as messaging from "messaging";
import { localStorage } from "local-storage";

import * as global from "../common/globals.js";

function getNewPin() {
  const url = `${global.BASE_URL}/api/clock-face/create`;
	return fetch(url, {
    method: "POST"
  })
  .then(response => response.json())
	.then(function(data) {
    console.log("Got new pin");
    console.log(data);
    localStorage.setItem("PIN", data['pin']);
    localStorage.setItem("TOKEN", data['token']);
    return data['pin'];
	});
}

function checkPaired() {
  const url = `${global.BASE_URL}/api/clock-face/status`;
	return fetch(url, {
	    headers: {
        'Content-Type': 'application/json',
        'CLOCK_FACE_PIN': localStorage.getItem("PIN"),
        'CLOCK_FACE_TOKEN': localStorage.getItem("TOKEN")
	    }
	})
  .then(function (response) {
    return response.json();
  })
	.then(function(data) {
    localStorage.setItem("PAIRED", data["paired"]);
    localStorage.setItem("USERNAME", data["username"])
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
  localStorage.removeItem("TOKEN");
  localStorage.removeItem("PAIRED");
  localStorage.removeItem("USERNAME");
}

function getItem(key) {
  try {
    localStorage.getItem(key);
  } catch(error) {
    return undefined;
  }
}

function sendWatchStatus(statusMessage) {
  const paired = getItem("PAIRED");
  const pin = getItem("PIN");

  if(messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    messaging.peerSocket.send({
      status: statusMessage,
      pin: pin,
      authorized: paired
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
        "step_counts": stepCounts
      }),
	    headers: {
        'Content-Type': 'application/json',
        'CLOCK_FACE_PIN': localStorage.getItem("PIN"),
        'CLOCK_FACE_TOKEN': localStorage.getItem("TOKEN")
	    }
    }).then(function(response) {
      if (response.status == 401) {
        console.log("Unauthrized Response");
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

