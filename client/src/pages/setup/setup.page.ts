import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ParticipantInformation } from '@heartsteps/contact-information/participant-information';
import { FitbitAuth } from '@heartsteps/fitbit/fitbit-auth';
import { Step } from '@infrastructure/components/stepper.component';
import { FitbitService } from '@heartsteps/fitbit/fitbit.service';

const onboardingPages:Array<Step> = [{
    key: 'contactInformation',
    title: 'Contact Information',
    component: ParticipantInformation
}, {
    key: 'fitbit',
    title: 'Fitbit',
    component: FitbitAuth
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
