import { Component } from '@angular/core';
import { IonicPage, NavController } from 'ionic-angular';
import { EnrollPage } from '../enroll/enroll';

@IonicPage()
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
