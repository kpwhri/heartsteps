import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { ModalController } from 'ionic-angular';
import { PlacesService } from './places.service';
import { PlaceEdit } from './place-edit';
import { ChoiceDialogController } from '@infrastructure/choice-dialog.controler';
import { FormGroup } from '@angular/forms';

@Component({
    selector: 'heartsteps-places-list',
    templateUrl: 'places-list.html',
    entryComponents: [PlaceEdit]
})
export class PlacesList implements OnInit {
    @Output() saved = new EventEmitter<boolean>();
    public form: FormGroup = new FormGroup({});

    locations:Array<any>
    errorMessage:String

    constructor(
        private modalCtrl:ModalController,
        private locationsService:PlacesService,
        private choiceDialog: ChoiceDialogController
    ) {}

    ngOnInit() {
        return this.locationsService.getLocations()
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
            if(updatedLocation) {
                location.address = updatedLocation.address
                location.latitude = updatedLocation.latitude
                location.longitude = updatedLocation.longitude   
            } else {
                // location was deleted
                const index = this.locations.indexOf(location)
                if(index > -1) {
                    this.locations.splice(index, 1)
                }
            }
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
        return this.choiceDialog.showChoices('Type of place to create', [{
            text: 'Home',
            value: 'home'
        }, {
            text: 'Work',
            value: 'work'
        }, {
            text: 'Other',
            value: 'other'
        }]);
    }

    showLocationPopover(location:any):Promise<any> {
        return new Promise((resolve, reject) => {
            let modal = this.modalCtrl.create(PlaceEdit, {
                location: location
            });

            modal.onDidDismiss((updatedLocation:any) => {
                if(updatedLocation) {
                    resolve(updatedLocation)
                } else if (updatedLocation === false) {
                    resolve(false)
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
            this.saved.emit(true);
        })
        .catch((error) => {
            if(error.message) {
                this.errorMessage = error.message
            }

            if(error.locations) {
                this.locations = error.locations
            }
        })
    }
}
