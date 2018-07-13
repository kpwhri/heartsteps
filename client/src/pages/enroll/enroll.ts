import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { EnrollmentService } from '../../heartsteps/enrollment.service';

@IonicPage()
@Component({
  selector: 'page-enroll',
  templateUrl: 'enroll.html',
  providers: [ EnrollmentService ]
})
export class EnrollPage {

  // Enrollment token enterd by user
  enrollmentToken:String;
  error:Boolean;

  constructor(private enrollmentService: EnrollmentService, public navCtrl: NavController, public navParams: NavParams) {}

  enroll() {
    if(!this.enrollmentToken || this.enrollmentToken==="") {
      return;
    }

    let service = this;
    service.error = false;
    
    this.enrollmentService.enroll(this.enrollmentToken)
    .then(() => {
      console.log('... sucessfully enrolled ...')
    })
    .catch(function(){
      service.error = true;
    })

    
  }

}
