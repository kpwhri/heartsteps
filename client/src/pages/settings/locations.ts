import { Component } from '@angular/core';
import { NavController, ModalController } from 'ionic-angular';
import { LocationEdit } from './location-edit';
import { LocationsService } from '../../heartsteps/locations.service';

@Component({
    selector: 'locations-page',
    templateUrl: 'locations.html'
})
export class LocationsPage {

    locations:Array<any>

    constructor(
        private navCtrl:NavController,
        private modalCtrl:ModalController,
        private locationsService:LocationsService
    ) {
        this.locationsService.getLocations()
        .then((locations) => {
            this.locations = locations
        })
        .catch(() => {
            this.locations = []
        })
    }

    editLocation(location:any) {
        this.showLocationPopover(location)
        .then((updatedLocation) => {
            location.address = updatedLocation.address
            location.type = updatedLocation.type
            location.latitude = updatedLocation.latitude
            location.longitude = updatedLocation.longitude
        })
        .catch(() => {
            // don't do anything
        })
    }

    newLocation() {
        this.showLocationPopover({})
        .then((location) => {
            this.locations.push(location);
        })
        .catch(()=>{
            // don't do anything
        })
    }

    showLocationPopover(location:any):Promise<any> {
        return new Promise((resolve, reject) => {
            let modal = this.modalCtrl.create(LocationEdit, {
                location: location
            });

            modal.onDidDismiss((updatedLocation:any) => {
                if(updatedLocation) {
                    resolve(updatedLocation)
                } else {
                    reject()
                }
            });

            modal.present()
        });
    }

    saveLocations() {
        this.locationsService.validate(this.locations)
        .then(() => {
            return this.locationsService.saveLocations(this.locations)
        })
        .then(() => {
            this.navCtrl.pop()
        })
        .catch((error) => {
            if(error.locations) {
                this.locations = error.locations
            }
        })
    }
}
