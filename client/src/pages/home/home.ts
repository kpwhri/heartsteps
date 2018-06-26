import { Component } from '@angular/core';
import { NavController, IonicPage } from 'ionic-angular';
import { AuthorizationService } from '../../heartsteps/authorization.service';
import { WelcomePage } from '../welcome/welcome';
import { FcmService } from '../../heartsteps/fcm';

@IonicPage()
@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {

  constructor(
    private navCtrl: NavController,
    private authService: AuthorizationService,
    private fcmService:FcmService
  ) {

  }

  getToken() {
    this.fcmService.getPermission();
  }

  ionViewCanEnter() {
    return this.authService.isAuthorized()
    .catch(() => {
      this.navCtrl.setRoot(WelcomePage);
      this.navCtrl.popToRoot();
    });
  }

}
