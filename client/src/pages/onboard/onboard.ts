import { Component, OnInit } from '@angular/core';
import { NotificationsPermissionComponent } from '@heartsteps/notifications/notification-permission.component';
import { LocationPermission } from '@heartsteps/locations/location-permission';
import { WeeklyReflectionTimePage } from '@heartsteps/weekly-survey/weekly-reflection-time.page';
import { WalkingSuggestionTimesComponent } from '@heartsteps/walking-suggestions/walking-suggestion-times.component';
import { PlacesList } from '@heartsteps/places/places-list';
import { ProfileService } from '@heartsteps/participants/profile.factory';
import { Router } from '@angular/router';
import { ParticipantInformation } from '@heartsteps/contact-information/participant-information';
import { FitbitAuth } from '@heartsteps/fitbit/fitbit-auth';
import { Step } from '@infrastructure/components/stepper.component';

const onboardingPages:Array<Step> = [{
    key: 'contactInformation',
    title: 'Contact Information',
    component: ParticipantInformation
}, {
    key: 'notificationsEnabled',
    title: 'Notifications',
    component: NotificationsPermissionComponent
}, {
    key: 'weeklyReflectionTime',
    title: 'Reflection Time',
    component: WeeklyReflectionTimePage
}, {
    key: 'walkingSuggestionTimes',
    title: 'Suggestion Times',
    component: WalkingSuggestionTimesComponent
}, {
    key: 'locationPermission',
    title: 'Locations',
    component: LocationPermission
}, {
    key: 'places',
    title: 'Places',
    component: PlacesList
}, {
    key: 'fitbitAuthorization',
    title: 'Fitbit',
    component: FitbitAuth
}];

@Component({
    selector: 'pages-onboarding',
    templateUrl: 'onboard.html',
    entryComponents: [
        NotificationsPermissionComponent,
        LocationPermission,
        WeeklyReflectionTimePage,
        WalkingSuggestionTimesComponent,
        LocationPermission,
        PlacesList
    ]
})
export class OnboardPage implements OnInit {
    pages:Array<Step>;

    constructor(
        private profileService: ProfileService,
        private router: Router
    ) {}

    ngOnInit() {
        this.profileService.get()
        .then((profile) => {
            this.pages = [];
            onboardingPages.forEach((page) => {
                if(!profile[page.key]) {
                    this.pages.push(page);
                }
            });
        });
    }

    public finish() {
        this.router.navigate(['/']);
    }

}
