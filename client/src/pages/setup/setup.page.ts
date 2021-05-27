import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { ParticipantInformation } from '@heartsteps/contact-information/participant-information';
import { Step } from '@infrastructure/components/stepper.component';
import { FitbitService } from '@heartsteps/fitbit/fitbit.service';
import { FitbitAuthorizePage } from './fitbit-authorize.page';

const onboardingPages:Array<Step> = [{
    key: 'contactInformation',
    title: 'Contact Information',
    component: ParticipantInformation
}, {
    key: 'fitbit',
    title: 'Fitbit',
    component: FitbitAuthorizePage
}];

@Component({
    templateUrl: 'setup.page.html'
})
export class SetupPage {
    pages:Array<Step> = onboardingPages;

    constructor(
        private router: Router,
        private fitbitService: FitbitService
    ) {
        this.fitbitService.setRedirectURL('/setup/fitbit-authorize');
    }

    public finish() {
        this.router.navigate(['setup','complete']);
    }

}
