import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { EnrollmentService } from '../../heartsteps/enrollment.service';

/**
 * Generated class for the EnrollPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-enroll',
  templateUrl: 'enroll.html',
})
export class EnrollPage {

  // Enrollment token enterd by user
  enrollmentToken:String;

  constructor(private enrollmentService: EnrollmentService, public navCtrl: NavController, public navParams: NavParams) {}

  enroll() {
    if(!this.enrollmentToken || this.enrollmentToken==="") {
      return;
    }

    this.enrollmentService.enroll(this.enrollmentToken)
    .then(function(response) {
      // go to success page
    })
    .catch(function(){
      // show error message
    })

    
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad EnrollPage');
  }

}
