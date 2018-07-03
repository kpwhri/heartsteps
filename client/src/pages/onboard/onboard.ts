import { Component, ViewChild } from '@angular/core';
import { IonicPage, NavController, Slides } from 'ionic-angular';

import { AuthorizationService } from '../../heartsteps/authorization.service';
import { WelcomePage } from '../welcome/welcome';

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

  constructor(public navCtrl: NavController, private authService:AuthorizationService) {}

  ionViewWillEnter() {
    this.slides.lockSwipes(true);
  }

  next() {
    this.slides.lockSwipes(false);
    this.slides.slideNext();
    this.slides.lockSwipes(true);
  }

  ionViewCanEnter() {
    return this.authService.isAuthorized()
    .catch(() => {
      this.navCtrl.setRoot(WelcomePage);
      this.navCtrl.popToRoot();
    });
  }

}
