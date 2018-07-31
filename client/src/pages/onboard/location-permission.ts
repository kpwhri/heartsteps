import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { Geolocation } from '@ionic-native/geolocation';
import { loadingService } from '../../infrastructure/loading.service';

@Component({
  selector: 'location-permission-pane',
  templateUrl: 'location-permission.html',
})
export class LocationPermissionPane {

  constructor(
    private navCtrl:NavController,
    private geolocation:Geolocation,
    private loadingService:loadingService
  ) {}

  getPermission() {
    this.loadingService.show("Getting location permission")
    this.geolocation.getCurrentPosition().then((resp) => {
      this.loadingService.dismiss()
      this.navCtrl.pop()
     }).catch((error) => {
      this.loadingService.dismiss()
       console.log('Error getting location', error);
     });
  }
}
