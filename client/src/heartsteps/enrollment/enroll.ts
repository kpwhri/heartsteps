import { Component } from '@angular/core';
import { EnrollmentService } from './enrollment.service';
import { loadingService } from '@infrastructure/loading.service';
import { FormControl, Validators, FormGroup } from '@angular/forms';

@Component({
    selector: 'heartsteps-enroll',
    templateUrl: 'enroll.html',
    providers: [ EnrollmentService ]
})
export class EnrollPage {
    public error:Boolean
    public enrollmentForm:FormGroup

    constructor(
        private enrollmentService: EnrollmentService,
        private loadingService:loadingService
    ) {
        this.enrollmentForm = new FormGroup({
            entryToken: new FormControl('', Validators.required),
            birthYear: new FormControl('')
        });
    }

    enroll() {
        this.error = false;

        if(this.enrollmentForm.valid) {
            this.loadingService.show('Authenticating entry code');
    
            const token = this.enrollmentForm.value.entryToken;
            const birthYear = this.enrollmentForm.value.birthYear;
            this.enrollmentService.enroll(token, birthYear)
            .then(() => {
                this.loadingService.dismiss();
            })
            .catch(() => {
                this.error = true;
                this.loadingService.dismiss();
            })
        } else {
            this.enrollmentForm.markAsDirty();
            this.enrollmentForm.markAsTouched();
        }
    }
}
