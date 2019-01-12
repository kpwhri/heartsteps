import { Component, EventEmitter, Output } from '@angular/core';
import { LoadingService } from '@infrastructure/loading.service';
import { LocationService } from './location.service';

@Component({
  selector: 'heartsteps-location-permission',
  templateUrl: 'location-permission.html',
})
export class LocationPermission {
  @Output() saved = new EventEmitter<boolean>();

  constructor(
    private locationService:LocationService,
    private loadingService:LoadingService
  ) {}

  getPermission() {
    this.loadingService.show("Getting location permission")
    this.locationService.getPermission()
    .then(() => {
      return this.locationService.saveLocation();
    })
    .then(() => {
      this.loadingService.dismiss()
      this.saved.emit(true);
     }).catch(() => {
      this.loadingService.dismiss()
     });
  }
}
