import { Component } from '@angular/core';
import { IonicPage } from 'ionic-angular';

import { HeartstepsServer } from '../../infrastructure/heartsteps-server.service';

@IonicPage()
@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {
    constructor(private server:HeartstepsServer) {}

    createDecision():Promise<Boolean> {
        return this.server.post('/decisions', {})
        .then(() => {
            return true;
        })
        .catch(() => {
            return false;
        });
    }
}
