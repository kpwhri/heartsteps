import { geolocation } from "geolocation";

export function locationSuccess(position) {
    console.log("Latitude: " + position.coords.latitude,
                "Longitude: " + position.coords.longitude);
}

export function locationError(error) {
  console.log("Error: " + error.code,
              "Message: " + error.message);
}