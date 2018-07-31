import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { EnrollmentService } from '../../heartsteps/enrollment.service';
import { loadingService } from '../../infrastructure/loading.service';

@IonicPage()
@Component({
    selector: 'page-enroll',
    templateUrl: 'enroll.html',
    providers: [ EnrollmentService ]
})
export class EnrollPage {
    private enrollmentToken:String
    private error:Boolean

    constructor(
        private enrollmentService: EnrollmentService,
        private loadingService:loadingService
    ) {}

    enroll() {
        if(!this.enrollmentToken || this.enrollmentToken==="") {
            return
        }
        this.error = false

        this.loadingService.show('Authenticating entry code')
        this.enrollmentService.enroll(this.enrollmentToken)
        .then(() => {
            this.loadingService.dismiss()  
        })
        .catch(() => {
            this.error = true
            this.loadingService.dismiss()
        })
    }
}
