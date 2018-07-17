import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { Geolocation } from '@ionic-native/geolocation';

@Component({
  selector: 'location-permission-pane',
  templateUrl: 'location-permission.html',
})
export class LocationPermissionPane {

  constructor(
    private navCtrl:NavController,
    private geolocation:Geolocation
  ) {}

  getPermission() {
    this.geolocation.getCurrentPosition().then((resp) => {
      console.log(resp);
      this.navCtrl.pop();
     }).catch((error) => {
       console.log('Error getting location', error);
     });
  }
}
