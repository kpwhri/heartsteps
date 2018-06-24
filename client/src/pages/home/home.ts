import { Component } from '@angular/core';
import { NavController, IonicPage } from 'ionic-angular';
import { AuthorizationService } from '../../heartsteps/authorization.service';
import { WelcomePage } from '../welcome/welcome';

@IonicPage()
@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {

  constructor(private navCtrl: NavController, private authService: AuthorizationService) {

  }

  ionViewCanEnter() {
    return this.authService.isAuthorized()
    .catch(() => {
      this.navCtrl.setRoot(WelcomePage);
      this.navCtrl.popToRoot();
    });
  }

}
