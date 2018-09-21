function entryCode(props) {
  return (
    <Page>
      <Section
        title={<Text bold align="center">HeartSteps Settings</Text>}
        description={<Text>HeartSteps 2.0 is a project of the Kaiser
            Permanent Washington Health Research Institute</Text>}>
        <TextInput label="Entry Code" settingsKey="entryCode" />
      </Section>
    </Page>
  );
}

registerSettingsPage(entryCode);
