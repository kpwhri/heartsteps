import * as global from "../common/globals.js";

function mySettings(props) {
  let integrationStatus = props.settingsStorage.getItem(global.INTEGRATION_STATUS_MESSAGE);
  let intComment = new String();
  switch (integrationStatus) {
    case global.VALID:
      intComment = `Thank you for registering your Fitbit with the
                    HeartSteps program!`;
      break;
    case global.INITIALIZE_ENROLLMENT:
      intComment = `Please enter and save your entry code & birth year
                    to link your Fitbit to the HeartSteps program.`;
      break;
    case global.AUTH_INVALID:
      intComment = `An invalid authorization token was returned from
                    the HeartSteps system. Please tell study staff
                    that the system has a problem.`;
      break;
    case global.ID_INVALID:
      intComment = `An invalid participant identifier was returned from
                    the HeartSteps system. Please tell study staff
                    that the system has a problem.`;
      break;
    case global.AUTH_ID_INVALID:
      intComment = `An invalid authorization token & participant identifier
                    was returned from the HeartSteps system. Please tell study staff
                    that the system has a problem.`;
      break;
    case global.BIRTH_YEAR_INVALID:
      intComment = `Birth year is not valid or is not in a valid format.`;
      break;
    case global.BIRTH_ENTRY_INVALID:
      intComment = `Birth Year and Entry Code are not valid or is not in
                    a valid format.`;
      break;
    case global.ENTRY_CODE_INVALID:
      intComment = `Entry Code is not valid or is not in a valid format.`;
      break;
    case global.CANNOT_AUTHENTICATE:
      intComment = `The HeartSteps server was unable to authenticate your
                    account. The Entry Code or Birth Year could be incorrect,
                    or we may be having trouble on our end.
                    Please try again in a bit, or let study staff
                    know if the error continues`;
      break;
    case global.UNKNOWN_INVALID:
      intComment = `We were unable to authenticate you for reasons
                    unknown. Please let the study staff know.`;
      break;
    default:
      intComment = `Your Fitbit is not linked to the HeartSteps program.`;
      break;
  }

  return (
    <Page>
      <Section
        title={<Text bold align="center">HeartSteps Integration Data</Text>}
        description={<Text>This information is necessary so we can
          associate this watch with your HeartSteps account</Text>}>
        <TextInput label="Entry Code" settingsKey="entryCode" />
        <TextInput label="Birth Year" settingsKey="birthYear" />
      </Section>
      <Section
        title={<Text bold align="center">Integration Status</Text>}
        description={<Text>{intComment}</Text>}>
        <TextImageRow label={integrationStatus} />
      </Section>
      <Section
        title={<Text bold align="center">About</Text>}
        description={<Text>HeartSteps 2.0 is a project of the Kaiser
            Permanent Washington Health Research Institute.</Text>}>
        <Text>Contact details</Text>
      </Section>
    </Page>
  );
}

registerSettingsPage(mySettings);
