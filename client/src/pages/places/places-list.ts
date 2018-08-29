import { Component } from '@angular/core';
import { NavController, ModalController, ActionSheetController } from 'ionic-angular';
import { PlacesService } from '@heartsteps/places.service';
import { PlaceEdit } from '@pages/places/place-edit';

@Component({
    selector: 'places-list-page',
    templateUrl: 'places-list.html',
    entryComponents: [PlaceEdit]
})
export class PlacesListPage {

    locations:Array<any>

    constructor(
        private navCtrl:NavController,
        private modalCtrl:ModalController,
        private locationsService:PlacesService,
        private actionSheetCtrl:ActionSheetController
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
        let locationType:string = ""
        this.pickPlaceType()
        .then((type) => {
            locationType = type
            return this.showLocationPopover(false)
        })
        .then((location) => {
            location.type = locationType
            this.locations.push(location);
        })
        .catch(()=>{
            // don't do anything
        })
    }

    pickPlaceType():Promise<string> {
        return new Promise((resolve, reject) => {
            let actionSheet = this.actionSheetCtrl.create({
                title: 'Type of place to create',
                buttons: [
                    {
                        text: 'Home',
                        handler: ()=> {
                            resolve('home')
                        }
                    }, {
                        text: 'Work',
                        handler: () => {
                            resolve('work')
                        }
                    }, {
                        text: 'Other',
                        handler: () => {
                            resolve('other')
                        }
                    }, {
                        text: 'Cancel',
                        handler: () => {
                            reject()
                        }
                    }
                ]
            })
            actionSheet.present()
        })
    }

    showLocationPopover(location:any):Promise<any> {
        return new Promise((resolve, reject) => {
            let modal = this.modalCtrl.create(PlaceEdit, {
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
