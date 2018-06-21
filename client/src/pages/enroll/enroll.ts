import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { EnrollmentService } from '../../heartsteps/enrollment.service';
import { HomePage } from '../home/home';

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
  providers: [ EnrollmentService ]
})
export class EnrollPage {

  // Enrollment token enterd by user
  enrollmentToken:String;
  errorMessage:String;

  constructor(private enrollmentService: EnrollmentService, public navCtrl: NavController, public navParams: NavParams) {}

  enroll() {
    if(!this.enrollmentToken || this.enrollmentToken==="") {
      return;
    }

    let service = this;
    service.errorMessage = null;
    
    this.enrollmentService.enroll(this.enrollmentToken)
    .then(function() {
      this.navCtrl.setRoot(HomePage)
    })
    .catch(function(){
      service.errorMessage = "Invalid token"
    })

    
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad EnrollPage');
  }

}
