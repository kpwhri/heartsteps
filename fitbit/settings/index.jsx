import { BIRTH_YEAR, ENTRY_CODE, INTEGRATION_STATUS_MESSAGE } from "../common/globals.js";

function mySettings(props) {
  let integrationStatus = props.settingsStorage.getItem(INTEGRATION_STATUS_MESSAGE);
  let entryCodeDefined = !(typeof JSON.parse(props.settingsStorage.getItem(ENTRY_CODE)).name === "undefined");
  let birthYearDefined = !(typeof JSON.parse(props.settingsStorage.getItem(BIRTH_YEAR)).name === "undefined");
  let intComment = new String();
  console.log(integrationStatus);
  if (entryCodeDefined) {
    if (birthYearDefined) {
      intComment = `Your information was saved, but we can't get your
        watch to talk to our system.  Please check that the information
        is correct, or contact our study staff. (And if you just
        updated your information, we're working on it now. Please
        check back later!)`;
    } else {
      intComment = "Please enter your Birth Year to complete enrollment.";
    }
  } else {
    intComment = "Please enter your Entry Code to complete enrollment.";
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
