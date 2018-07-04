import { Component, ViewChild } from '@angular/core';
import { IonicPage, NavController, Slides, Nav } from 'ionic-angular';

import { AuthorizationService } from '../../heartsteps/authorization.service';
import { WelcomePage } from '../welcome/welcome';
import { NotificationsPage } from './notifications';

/**
 * Generated class for the OnboardPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-onboard',
  templateUrl: 'onboard.html',
})
export class OnboardPage {
  @ViewChild(Slides) slides:Slides;
  @ViewChild(Nav) nav:Nav;

  constructor(public navCtrl: NavController, private authService:AuthorizationService) {}

  ionViewWillEnter() {
    this.nav.push(NotificationsPage);
    console.log("change please");
  }

  next() {
    console.log("NEXT");
  }

  ionViewCanEnter() {
    return this.authService.isAuthorized()
    .catch(() => {
      this.navCtrl.setRoot(WelcomePage);
      this.navCtrl.popToRoot();
    });
  }

}
