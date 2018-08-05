import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { EnrollmentService } from '../../heartsteps/enrollment.service';
import { loadingService } from '../../infrastructure/loading.service';
import { FormControl, Validators, FormGroup } from '@angular/forms';

@IonicPage()
@Component({
    selector: 'page-enroll',
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
            entryToken: new FormControl('', Validators.required)
        })
    }

    enroll() {
        this.error = false

        if(this.enrollmentForm.valid) {
            this.loadingService.show('Authenticating entry code')
    
            let token = this.enrollmentForm.value.entryToken
            this.enrollmentService.enroll(token)
            .then(() => {
                this.loadingService.dismiss()  
            })
            .catch(() => {
                this.error = true
                this.loadingService.dismiss()
            })
        } else {
            this.enrollmentForm.markAsDirty()
        }
    }
}
