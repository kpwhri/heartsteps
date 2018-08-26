import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { loadingService } from '@infrastructure/loading.service';
import { LocationService } from '@infrastructure/location.service';

@Component({
  selector: 'location-permission-pane',
  templateUrl: 'location-permission.html',
})
export class LocationPermissionPane {

  constructor(
    private navCtrl:NavController,
    private locationService:LocationService,
    private loadingService:loadingService
  ) {}

  getPermission() {
    this.loadingService.show("Getting location permission")
    this.locationService.getPermission()
    .then(() => {
      this.loadingService.dismiss()
      this.navCtrl.pop()
     }).catch(() => {
      this.loadingService.dismiss()
     });
  }
}
