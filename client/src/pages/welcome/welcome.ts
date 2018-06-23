import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { EnrollPage } from '../enroll/enroll';

@Component({
  selector: 'page-welcome',
  templateUrl: 'welcome.html'
})
export class WelcomePage {

  constructor(private navCtrl: NavController) {
  }

  goToEnrollPage() {
    this.navCtrl.push(EnrollPage)
  }

}
