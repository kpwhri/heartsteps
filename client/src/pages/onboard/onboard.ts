import { Component, ViewChild, OnInit, ComponentFactoryResolver, ViewContainerRef } from '@angular/core';

import { ParticipantService } from '@heartsteps/participants/participant.service';
import { NotificationsPermission } from '@heartsteps/notifications/notifications';
import { LocationPermission } from '@heartsteps/locations/location-permission';
import { Subscription } from 'rxjs';
import { WeeklyReflectionTimePage } from '@heartsteps/weekly-survey/weekly-reflection-time.page';
import { ActivitySuggestionTimes } from '@heartsteps/activity-suggestions/activity-suggestion-times';
import { PlacesList } from '@heartsteps/places/places-list';
import { ProfileService } from '@heartsteps/participants/profile.factory';
import { Router } from '@angular/router';
import { ParticipantInformation } from '@heartsteps/contact-information/participant-information';
import { FitbitAuth } from '@heartsteps/fitbit/fitbit-auth';

const onboardingPages:Array<any> = [{
    key: 'contact',
    title: 'Contact Information',
    component: ParticipantInformation
}, {
    key: 'notificationsEnabled',
    title: 'Notifications',
    component: NotificationsPermission
}, {
    key: 'weeklyReflectionTime',
    title: 'Reflection Time',
    component: WeeklyReflectionTimePage
}, {
    key: 'activitySuggestionTimes',
    title: 'Suggestion Times',
    component: ActivitySuggestionTimes
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
        NotificationsPermission,
        LocationPermission,
        WeeklyReflectionTimePage,
        ActivitySuggestionTimes,
        LocationPermission,
        PlacesList
    ]
})
export class OnboardPage implements OnInit {
    @ViewChild("screenDisplay", { read: ViewContainerRef }) container: ViewContainerRef;
    index:number = 0;
    pages:Array<any>;

    public pageTitle:string;
    private pageSubscription:Subscription;

    constructor(
        private router: Router,
        private profileService: ProfileService,
        private componentFactoryResolver: ComponentFactoryResolver
    ) {}

    ngOnInit() {
        this.profileService.getProfile()
        .then((profile) => {
            this.pages = [];
            onboardingPages.forEach((page) => {
                if(!profile[page.key]) {
                    this.pages.push(page);
                }
            });
            this.loadPage(0);
        });
    }

    nextPage() {
        this.loadPage(this.index + 1);
    }

    prevPage() {
        this.loadPage(this.index - 1);
    }

    loadPage(pageNumber:number) {
        if(pageNumber >= this.pages.length) {
            this.router.navigate(['/']);
            return;
        }
        const page:any = this.pages[pageNumber];
        if(!page) {
            return;
        } else {
            this.index = pageNumber;
        }

        if(this.pageSubscription) {
            this.pageSubscription.unsubscribe();
        }
        this.container.clear();

        this.pageTitle = page.title;
        let componentFactory = this.componentFactoryResolver.resolveComponentFactory(page.component);
        let componentRef = this.container.createComponent(componentFactory);

        let instance:any = componentRef.instance;
        this.pageSubscription = instance.saved.subscribe(() => {
            this.pageSubscription.unsubscribe();
            this.pageSubscription = null;

            this.nextPage();
        });
    }

}
