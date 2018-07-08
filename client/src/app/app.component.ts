import { Component, ViewChild } from '@angular/core';
import { Platform, ToastController, Nav } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { WelcomePage } from '../pages/welcome/welcome';
import { AuthorizationService } from '../heartsteps/authorization.service';
// import { HomePage } from '../pages/home/home';
import { OnboardPage } from '../pages/onboard/onboard';
import { FcmService } from '../heartsteps/fcm';


@Component({
  templateUrl: 'app.html'
})
export class MyApp {
  @ViewChild(Nav) nav:Nav
  rootPage:any;

  constructor(platform: Platform, statusBar: StatusBar, splashScreen: SplashScreen, toastCtrl:ToastController, authService:AuthorizationService, fcmService:FcmService) {
    platform.ready()
    .then(() => {
      return new Promise((resolve) => {
        authService.isAuthorized()
        .then(() => {
          // if(false) {
          //   this.rootPage = HomePage;
          // } else {
            this.rootPage = OnboardPage;
          // }
        })
        .catch(() => {
          this.rootPage = WelcomePage;
        })
        .then(() => {
          resolve();
        });
      })
    })
    .then(() => {
      fcmService.onMessage().subscribe((message) => {
        let toast = toastCtrl.create({
          message: message,
          showCloseButton: true
        })
        toast.present();
      })
    })
    .then(() => {
      // Okay, so the platform is ready and our plugins are available.
      // Here you can do any higher level native things you might need.
      statusBar.styleDefault();
      splashScreen.hide();
    });
  }
}

