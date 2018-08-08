import { Component, ViewChild } from '@angular/core';
import { IonicPage, Nav } from 'ionic-angular';

import { NotificationsPage } from './notifications';
import { LocationPermissionPane } from './location-permission';
import { OnboardEndPane } from './onboard-end';
import { ActivitySuggestionTimes } from './activity-suggestion-times';
import { LocationsPage } from './locations';
import { Storage } from '@ionic/storage';
import { ParticipantService } from '../../heartsteps/participant.service';

@IonicPage()
@Component({
    selector: 'page-onboard',
    templateUrl: 'onboard.html'
})
export class OnboardPage {
    @ViewChild(Nav) nav:Nav;

    private screens:Array<any>;

    constructor(
        private storage:Storage,
        private participantService:ParticipantService
    ) {}

    setScreens():Promise<any> {
        return this.participantService.getProfile()
        .then((profile) => {
            this.screens = []

            if(!profile.notificationPermission) {
                this.screens.push(NotificationsPage)
            }
            if(!profile.activitySuggestionTimes) {
                this.screens.push(ActivitySuggestionTimes)
            }
            if(!profile.locationPermission) {
                this.screens.push(LocationPermissionPane)
            }
            if(!profile.locations) {
                this.screens.push(LocationsPage)
            }
        })
    }

    showNextScreen() {
        let nextScreen = this.screens.shift()
        if(nextScreen) {
            this.nav.push(nextScreen);
        }
    }

    ionViewWillEnter() {
        this.nav.setRoot(OnboardEndPane)
        this.nav.swipeBackEnabled = false

        this.nav.viewWillUnload.subscribe(() => {
            this.showNextScreen()
        })

        return this.setScreens()
        .then(() => {
            this.showNextScreen()
        })
    }

}
