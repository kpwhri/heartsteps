import { Component } from '@angular/core';
import { IonicPage, Platform } from 'ionic-angular';
import { Geolocation } from '@ionic-native/geolocation';

import { HeartstepsServer } from '../../infrastructure/heartsteps-server.service';

@IonicPage()
@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {
    constructor(
        private server:HeartstepsServer,
        private geolocation:Geolocation,
        private platform:Platform
    ) {}

    createDecision():Promise<Boolean> {
        return this.geolocation.getCurrentPosition()
        .then((position:Position) => {

            if(this.platform.is('ios') || this.platform.is('android')) {
                return this.server.post('/decisions', {})
            } else {
                return this.server.post('/decisions', {
                    location: {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    }
                })
            }
        })
        .then(() => {
            return true;
        })
        .catch(() => {
            return false;
        });
    }
}
