import * as messaging from "messaging";
import { localStorage } from "local-storage";
import { geolocation } from "geolocation";

import * as global from "../common/globals.js";

function removeItem(key) {
  try {
    localStorage.removeItem(key);
  } catch(error) {
    console.log("Couldn't remove "+ key);
  }
}

function getItem(key) {
  try {
    const value = localStorage.getItem(key);
    if (value == 'true') {
      return true;
    }
    if (value == 'false') {
      return false;
    }
    return value;
  } catch(error) {
    return undefined;
  }
}

function clear() {
  removeItem("PIN");
  removeItem("TOKEN");
  removeItem("PAIRED");
  removeItem("USERNAME");
}

function getNewPin() {
  const url = `${global.BASE_URL}/api/fitbit-clock-face/create`;
  clear();
	return fetch(url, {
    method: "POST"
  })
  .then(function(response) {
    console.log("Response " + response.status);
    return response.json();
  })
	.then(function(data) {
    console.log("Got new pin");
    console.log(data);
    localStorage.setItem("PIN", data['pin']);
    localStorage.setItem("TOKEN", data['token']);
    return data['pin'];
	});
}

function checkPaired() {
  const url = `${global.BASE_URL}/api/fitbit-clock-face/status`;
	return fetch(url, {
	    headers: {
        'Content-Type': 'application/json',
        'CLOCK-FACE-PIN': getItem("PIN"),
        'CLOCK-FACE-TOKEN': getItem("TOKEN")
	    }
	})
  .then(function (response) {
    if(response.status == 401) {
      clear();
      return Promise.resolve({});
    } else {
      return response.json();
    }
  })
	.then(function(data) {
    console.log('Check paied data');
    console.log(data);
    localStorage.setItem("PAIRED", data["paired"]);
    localStorage.setItem("USERNAME", data["username"])
	});
}

function updateWatchStatus() {
  const pin = getItem("PIN");
  const paired = getItem("PAIRED");

  if (!pin) {
    getNewPin().then(function() {
      sendWatchStatus();
    })
    .catch(() => {
      sendWatchStatus();
    });
  } else {
    checkPaired().then(() => {
      sendWatchStatus();
    })
    .catch(() => {
      sendWatchStatus();
    })
  }
}

function sendWatchStatus() {
  const paired = getItem("PAIRED");
  const pin = getItem("PIN");

  if(messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    messaging.peerSocket.send({
      pin: pin,
      authorized: paired
    });
  } else {
    debounceSendWatchStatus();
  }
}

function debounceSendWatchStatus() {
  setTimeout(function() {
    sendWatchStatus();
  }, 5 * 1000);
}

function sendStepCounts(stepCounts) {
  geolocation.getCurrentPosition(function(position) {
    sendStepCountsAndLocation(stepCounts, {
      'latitude': position.coords.latitude,
      'longitude': position.coords.longitude
    })
  }, function(error) {
    sendStepCountsAndLocation(stepCounts, undefined);
  });
}

function sendStepCountsAndLocation(stepCounts, location) {
  const url = `${global.BASE_URL}/api/fitbit-clock-face/step-counts`;
  const paired = getItem("PAIRED")
  const pin = getItem("PIN");
  const token = getItem("TOKEN");
  if (paired) {
    fetch(url, {
      method: "POST",
      body: JSON.stringify({
        "step_counts": stepCounts,
        "location": location
      }),
	    headers: {
        'Content-Type': 'application/json',
        'CLOCK-FACE-PIN': pin,
        'CLOCK-FACE-TOKEN': token
	    }
    }).then(function(response) {
      if (response.status == 401) {
        clear();
        sendWatchStatus();
      }
    }).catch(function(error) {
      console.log('Error in sendSteps: ', error);
    })
  } else {
    console.log("Not authorized to send step counts");
    sendWatchStatus();
  }
}

messaging.peerSocket.onmessage = function(evt) {
  if (evt.data.steps) {
    sendStepCounts(evt.data.steps);
  } else if (evt.data.key == global.CHECK_AUTH) {
    updateWatchStatus();
  }
}

