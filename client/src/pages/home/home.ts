import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { EnrollPage } from '../enroll/enroll';

@Component({
  selector: 'page-home',
  templateUrl: 'home.html',
  entryComponents: [EnrollPage]
})
export class HomePage {

  constructor(public navCtrl: NavController) {

  }

  goToEnrollPage() {
    this.navCtrl.push(EnrollPage);
  }

}
