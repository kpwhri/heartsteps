import * as global from "../common/globals.js";

function getIntComment(intStatus) {
  let intComment;
  if (intStatus == global.VALID) {
    intComment = `Thank you for registering your Fitbit with the
                  HeartSteps program!`;
  } else if (intStatus == global.INITIALIZE_ENROLLMENT) {
    intComment = `Please enter and save your entry code & birth year
                  to link your Fitbit to the HeartSteps program.`;
  } else if (intStatus == global.AUTH_INVALID) {
    intComment = `An invalid authorization token was returned from
                  the HeartSteps system. Please tell study staff
                  that the system has a problem.`;
  } else if (intStatus == global.ID_INVALID) {
    intComment = `An invalid participant identifier was returned from
                  the HeartSteps system. Please tell study staff
                  that the system has a problem.`;
  } else if (intStatus == global.AUTH_ID_INVALID) {
    intComment = `An invalid authorization token & participant identifier
                  was returned from the HeartSteps system. Please tell study staff
                  that the system has a problem.`;
  } else if (intStatus == global.BIRTH_YEAR_INVALID) {
    intComment = `Birth year is not valid or is not in a valid format.`;
  } else if (intStatus == global.BIRTH_ENTRY_INVALID) {
    intComment = `Birth Year and Entry Code are not valid or is not in
                  a valid format.`;
  } else if (intStatus == global.ENTRY_CODE_INVALID) {
    intComment = `Entry Code is not valid or is not in a valid format.`;
  } else if (intStatus == global.CANNOT_AUTHENTICATE) {
    intComment = `The HeartSteps server was unable to authenticate your
                  account. The Entry Code or Birth Year could be incorrect,
                  or we may be having trouble on our end.
                  Please try again in a bit, or let study staff
                  know if the error continues`;
  } else if (intStatus == global.UNKNOWN_INVALID) {
    intComment = `We were unable to authenticate you for reasons
                  unknown. Please let the study staff know.`;
  } else {
    intComment = `Your Fitbit is not linked to the HeartSteps program.`;
  }
  return intComment;
}

const section1Description = "This information is necessary"
  + " so we can associate this watch with your HeartSteps account";
const section3Description = "HeartSteps 2.0 is a project of"
  + " the Kaiser Permanente Washington Health Research Institute.";

const colorSet = [
  {color: "black"},
  {color: "darkslategrey"},
  {color: "dimgrey"},
  {color: "grey"},
  {color: "lightgrey"},
  {color: "beige"}
];

function mySettings(props) {
  let integrationStatus = props.settingsStorage.getItem(global.INTEGRATION_STATUS_MESSAGE);
  let integrationComment = getIntComment(integrationStatus);
  return (
    <Page>
      <Section
        title='HeartSteps Integration Data'
        description={section1Description}>
        <TextInput label="Entry Code" settingsKey="entryCode" />
        <TextInput label="Birth Year" settingsKey="birthYear" type="number" />
      </Section>
      <Section
        title='Integration Status'
        description={integrationComment}>
        <TextImageRow label={integrationStatus} />
      </Section>
      <Section
        title='About'
        description={section3Description}>
      </Section>
      <Section
        title='Background Color'>
        <ColorSelect
          settingsKey='colorBackground'
          colors={colorSet} />
      </Section>
    </Page>
  );
}

registerSettingsPage(mySettings);
