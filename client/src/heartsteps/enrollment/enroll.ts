import { Component, Output, EventEmitter } from '@angular/core';
import { EnrollmentService } from './enrollment.service';
import { LoadingService } from '@infrastructure/loading.service';
import { FormControl, Validators, FormGroup } from '@angular/forms';
import { BrowserService } from '@infrastructure/browser.service';


@Component({
    selector: 'heartsteps-enroll',
    templateUrl: 'enroll.html',
    providers: [ EnrollmentService ]
})
export class EnrollmentModal {
    public error:string
    public enrollmentForm:FormGroup

    @Output('enrolled') enrolled:EventEmitter<boolean> = new EventEmitter();

    constructor(
        private enrollmentService: EnrollmentService,
        private loadingService:LoadingService,
        private browserService: BrowserService
    ) {
        this.enrollmentForm = new FormGroup({
            entryToken: new FormControl('', Validators.required),
            birthYear: new FormControl('', Validators.required)
        });
    }

    public enroll() {
        this.error = undefined;
        this.loadingService.show('Authenticating');

        const token = this.enrollmentForm.value.entryToken;
        const birthYear = this.enrollmentForm.value.birthYear;
        
        this.enrollmentService.enroll(token, birthYear)
        .then(() => {
            this.enrolled.emit(true);
        })
        .catch(() => {
            this.error = 'Participant with matching entry code and birth year not found';
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public openPrivacyPolicy() {
        this.browserService.open('http://heartsteps-kpwhri.appspot.com/privacy-policy/');
    }
}
