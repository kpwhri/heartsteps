import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

@Component({
  selector: 'location-permission-pane',
  templateUrl: 'location-permission.html',
})
export class LocationPermissionPane {

  constructor(private navCtrl:NavController) {}

  getPermission() {
    console.log('Permission plz');
    this.navCtrl.pop();
  }
}
