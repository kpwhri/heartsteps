import { Component } from '@angular/core';
import { EnrollmentService } from './enrollment.service';
import { LoadingService } from '@infrastructure/loading.service';
import { FormControl, Validators, FormGroup } from '@angular/forms';
import { ViewController } from 'ionic-angular';

@Component({
    selector: 'heartsteps-enroll',
    templateUrl: 'enroll.html',
    providers: [ EnrollmentService ]
})
export class EnrollmentModal {
    public error:string
    public enrollmentForm:FormGroup

    constructor(
        private enrollmentService: EnrollmentService,
        private loadingService:LoadingService,
        private viewCtrl: ViewController
    ) {
        this.enrollmentForm = new FormGroup({
            entryToken: new FormControl('', Validators.required),
            birthYear: new FormControl('')
        });
    }

    enroll() {
        this.error = null;

        if(this.enrollmentForm.valid) {
            this.loadingService.show('Authenticating entry code');
    
            const token = this.enrollmentForm.value.entryToken;
            const birthYear = this.enrollmentForm.value.birthYear;
            this.enrollmentService.enroll(token, birthYear)
            .then(() => {
                this.loadingService.dismiss();
                this.viewCtrl.dismiss();
            })
            .catch((error) => {
                this.error = error;
                this.loadingService.dismiss();
            })
        } else {
            this.enrollmentForm.markAsDirty();
            this.enrollmentForm.markAsTouched();
        }
    }
}
