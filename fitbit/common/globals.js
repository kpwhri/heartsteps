export const ANTI_SEDENTARY_MESSAGE = "sendAntisedentaryMessage";
export const AUTHORIZATION_TOKEN = "authorizationToken";
export const BASE_URL = "https://heartsteps-kpwhri.appspot.com";
// export const BASE_URL = "http://localhost:8080";
export const BIRTH_YEAR = "birthYear";
export const ENTRY_CODE = "entryCode";
export const HEARTSTEPS_ID = "heartstepsId";
export const INTEGRATION_STATUS_MESSAGE = "integrationStatus";
export const QUERY_STEP_MESSAGE = "queryStepCount";
export const RECENT_STEPS = "recentSteps";

// Possible values to set INTEGRATION_STATUS_MESSAGE
// helpful to format the var values so they can be displayed?
export const AUTH_INVALID = "authorization token invalid";
export const AUTH_ID_INVALID = "authorization token & heartsteps id invalid";
export const BIRTH_YEAR_INVALID = "birth year invalid";
export const BIRTH_ENTRY_INVALID = "both invalid";
export const CANNOT_AUTHENTICATE = "http failure to authenticate";
export const VALID = "success";
export const ENTRY_CODE_INVALID = "entry code invalid";
export const ID_INVALID = "heartsteps id invalid";
export const INITIALIZE_ENROLLMENT = "initialize enrollment";
export const UNKNOWN_INVALID = "unknown error";

export function isNotNull(val){
  return (typeof val === "undefined"
      ||  val != ""
      ||  val.length > 0);
}

// Get the name component (value) of the newValue JSON settings object
// evt (events) have properties key, newValue & oldValue (& isTrusted)
// The value properties take the form {"name":"actual-value"}
export function parseSettingsValue(jsonValue){
  return JSON.parse(jsonValue).name;
}
