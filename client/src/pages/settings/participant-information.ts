import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';

@Component({
    selector: 'participant-information-page',
    templateUrl: 'participant-information.html'
})
export class ParticipantInformationPage {

    constructor(
        private navCtrl:NavController
    ) {}

    save() {
        this.navCtrl.pop()
    }

}
