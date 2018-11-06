export const ANTI_SEDENTARY_MESSAGE = "sendAntisedentaryMessage";
export const AUTHORIZATION_TOKEN = "authorizationToken";
export const BIRTH_YEAR = "birthYear";
export const ENTRY_CODE = "entryCode";
export const HEARTSTEPS_ID = "heartstepsId";
export const INTEGRATION_STATUS_MESSAGE = "integrationStatus";
export const QUERY_STEP_MESSAGE = "queryStepCount";
export const RECENT_STEPS = "recentSteps";

export function isNotNull(val){
  return (typeof val === "undefined"
      ||  val != ""
      ||  val.length > 0);
}
