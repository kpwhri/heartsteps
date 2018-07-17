import { Component, ViewChild } from '@angular/core';
import { IonicPage, NavController, Slides, Nav } from 'ionic-angular';

import { NotificationsPage } from './notifications';
import { LocationPermissionPane } from './location-permission';
import { OnboardEndPane } from './onboard-end';

@IonicPage()
@Component({
  selector: 'page-onboard',
  templateUrl: 'onboard.html'
})
export class OnboardPage {
  @ViewChild(Slides) slides:Slides;
  @ViewChild(Nav) nav:Nav;

  private screens:Array<any>;

  constructor(public navCtrl: NavController) {
    this.screens = [
      NotificationsPage,
      LocationPermissionPane,
      OnboardEndPane
    ];
  }

  ionViewWillEnter() {
    this.nav.swipeBackEnabled = false;
    this.nav.setPages(this.screens.reverse());
  }

}
