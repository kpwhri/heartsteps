import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

@Component({
    selector: 'locations-page',
    templateUrl: 'locations.html'
})
export class LocationsPage {

    locations:Array<any>

    constructor(
        private navCtrl:NavController
    ) {
        this.locations = [];
    }

    editLocation(location:any) {

    }

    newLocation(location:any) {

    }

    saveLocations() {
        this.navCtrl.pop();
    }
}
