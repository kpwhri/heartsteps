import { Component } from '@angular/core';
import { Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { WelcomePage } from '../pages/welcome/welcome';
import { AuthorizationService } from '../heartsteps/authorization.service';
import { HomePage } from '../pages/home/home';

@Component({
  templateUrl: 'app.html'
})
export class MyApp {
  rootPage:any;

  constructor(platform: Platform, statusBar: StatusBar, splashScreen: SplashScreen, authService:AuthorizationService) {
    platform.ready()
    .then(() => {
      return new Promise((resolve) => {
        authService.isAuthorized()
        .then(() => {
          this.rootPage = HomePage;
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
      // Okay, so the platform is ready and our plugins are available.
      // Here you can do any higher level native things you might need.
      statusBar.styleDefault();
      splashScreen.hide();
    });
  }
}

