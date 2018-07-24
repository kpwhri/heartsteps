import { Component } from '@angular/core';
import { NavController, ModalController } from 'ionic-angular';
import { LocationEdit } from './location-edit';
import { Geolocation } from '@ionic-native/geolocation';

@Component({
    selector: 'locations-page',
    templateUrl: 'locations.html'
})
export class LocationsPage {

    locations:Array<any>

    constructor(
        private navCtrl:NavController,
        private modalCtrl:ModalController,
        private geolocation:Geolocation
    ) {
        this.locations = []
    }

    editLocation(location:any) {
        this.showLocationPopover(location)
        .then((updatedLocation) => {
            location.address = updatedLocation.address
            location.type = updatedLocation.type
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
            this.geolocation.getCurrentPosition()
            .then((position:Position) => {
                let modal = this.modalCtrl.create(LocationEdit, {
                    location: location,
                    currentLocation: {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    }
                });
    
                modal.onDidDismiss((updatedLocation:any) => {
                    if(updatedLocation) {
                        resolve(updatedLocation)
                    } else {
                        reject()
                    }
                });
        
                modal.present()
            })
        });
    }

    saveLocations() {
        this.navCtrl.pop();
    }
}
