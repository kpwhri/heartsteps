import { BIRTH_YEAR, ENTRY_CODE, INTEGRATION_STATUS_MESSAGE } from "../common/globals.js";

function mySettings(props) {
  let integrationStatus = props.settingsStorage.getItem(INTEGRATION_STATUS_MESSAGE);
  console.log(integrationStatus);
  let intComment = new String();
  switch (integrationStatus) {
    case "enabled":
      intComment = `Thank you for registering your Fitbit with the
                    HeartSteps program!`;
      break;
    case "not started":
      intComment = `Please enter and save your entry code & birth year
                    to link your Fitbit to the HeartSteps program.`;
      break;
    case "auth token invalid":
      intComment = `An invalid authorization token was returned from
                    the HeartSteps system. Please tell study staff
                    that the system has a problem.`;
      break;
    case "user identifier invalid":
      intComment = `An invalid participant identifier was returned from
                    the HeartSteps system. Please tell study staff
                    that the system has a problem.`;
      break;
    case "user id & auth token invalid":
      intComment = `An invalid authorization token & participant identifier
                    was returned from the HeartSteps system. Please tell study staff
                    that the system has a problem.`;
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
