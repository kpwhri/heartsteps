import { Component, ViewChild } from '@angular/core';
import { IonicPage, Nav } from 'ionic-angular';

import { ProfileService } from "../../heartsteps/profile.factory";

import { NotificationsPage } from './notifications';
import { LocationPermissionPane } from './location-permission';
import { ActivitySuggestionTimes } from '../settings/activity-suggestion-times';

import { OnboardEndPane } from './onboard-end';
import { ParticipantInformationPage } from '@pages/settings/participant-information';
import { PlacesListPage } from '@pages/places/places-list';
import { FitbitAuthPage } from '@pages/onboard/fitbit-auth';
import { FitbitAppPage } from '@pages/onboard/fitbit-app';
import { WeeklyReflectionTimePage } from '@pages/settings/weekly-reflection-time.page';
import { ParticipantService } from '@heartsteps/participant.service';

const onboardingSteps = [{
    //     key: 'participantInformation',
    //     screen: ParticipantInformationPage
    // }, {
        key: 'notificationsEnabled',
        screen: NotificationsPage
    }, {
        key: 'weeklyReflectionTime',
        screen: WeeklyReflectionTimePage
    }, {
        key: 'activitySuggestionTimes',
        screen: ActivitySuggestionTimes
    }, {
        key: 'locationPermission',
        screen: LocationPermissionPane
    }, {
        key: 'places',
        screen: PlacesListPage
    }, {
        key: 'fitbitAuth',
        screen: FitbitAuthPage
    }, {
        key: 'fitbitApp',
        screen: FitbitAppPage
    }]

@IonicPage()
@Component({
    selector: 'page-onboard',
    templateUrl: 'onboard.html',
    entryComponents: [
        PlacesListPage
    ]
})
export class OnboardPage {
    @ViewChild(Nav) nav:Nav;

    private screens:Array<any>;

    constructor(
        private profileService: ProfileService,
        private participantService: ParticipantService
    ) {}

    setScreens():Promise<any> {
        return this.profileService.getProfile()
        .then((profile) => {
            this.screens = []

            onboardingSteps.forEach((step) => {
                if(!profile[step.key]) {
                    this.screens.push(step.screen)
                }
            })

            return this.screens
        })
        .catch(() => {
            Promise.reject(false)
        })
    }

    showNextScreen() {
        let nextScreen = this.screens.shift()
        if(nextScreen) {
            this.nav.push(nextScreen);
        } else {
            this.participantService.update()
        }
    }

    ionViewWillEnter() {
        // OnboardEndPane is blank root to allow other pages to be added/removed
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
