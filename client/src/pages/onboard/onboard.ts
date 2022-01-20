import { Component, OnInit } from "@angular/core";
import { NotificationsPermissionComponent } from "@heartsteps/notifications/notification-permission.component";
import { WeeklyReflectionTimePage } from "@heartsteps/weekly-survey/weekly-reflection-time.page";
import { FirstBoutPlanningTimePage } from "@heartsteps/bout-planning/first-bout-planning-time.page";
import { WalkingSuggestionTimesComponent } from "@heartsteps/walking-suggestions/walking-suggestion-times.component";
import { PlacesList } from "@heartsteps/places/places-list";
import { Router } from "@angular/router";
import { ParticipantInformation } from "@heartsteps/contact-information/participant-information";
import { Step } from "@infrastructure/components/stepper.component";
import { ParticipantService } from "@heartsteps/participants/participant.service";
import { FitbitAuthPage } from "./fitbit-auth.page";
import { FitbitClockFacePairPage } from "./fitbit-clock-face-pair.page";

import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";

const onboardingPageRecord: Record<string, Step> = {
    'contact-information': {
        key: "contactInformation",
        title: "Contact Information",
        component: ParticipantInformation,
    },
    'notifications-enabled': {
        key: "notificationsEnabled",
        title: "Notifications",
        component: NotificationsPermissionComponent,
    },
    'weekly-reflection-time': {
        key: "weeklyReflectionTime",
        title: "Reflection Time",
        component: WeeklyReflectionTimePage,
    },
    'first-bout-planning-time': {
        key: "firstBoutPlanningTime",
        title: "First Bout Planning Time",
        component: FirstBoutPlanningTimePage,
    },
    'walking-suggestion-times': {
        key: "walkingSuggestionTimes",
        title: "Suggestion Times",
        component: WalkingSuggestionTimesComponent,
    },
    'places': {
        key: "places",
        title: "Places",
        component: PlacesList,
    },
    'fitbit-authorization': {
        key: "fitbitAuthorization",
        title: "Fitbit",
        component: FitbitAuthPage,
    },
    'fitbit-clock-face': {
        key: "fitbitClockFace",
        title: "JustWalk Clock Face",
        component: FitbitClockFacePairPage,
    }
}


const onboardingPages: Array<Step> = [
    {
        key: "contactInformation",
        title: "Contact Information",
        component: ParticipantInformation,
    },
    {
        key: "notificationsEnabled",
        title: "Notifications",
        component: NotificationsPermissionComponent,
    },
    {
        key: "weeklyReflectionTime",
        title: "Reflection Time",
        component: WeeklyReflectionTimePage,
    },
    {
        key: "walkingSuggestionTimes",
        title: "Suggestion Times",
        component: WalkingSuggestionTimesComponent,
    },
    {
        key: "places",
        title: "Places",
        component: PlacesList,
    },
    {
        key: "fitbitAuthorization",
        title: "Fitbit",
        component: FitbitAuthPage,
    },
];


@Component({
    selector: "pages-onboarding",
    templateUrl: "onboard.html",
    entryComponents: [
        ParticipantInformation,
        NotificationsPermissionComponent,
        WeeklyReflectionTimePage,
        FirstBoutPlanningTimePage,
        WalkingSuggestionTimesComponent,
        PlacesList,
        FitbitAuthPage,
        FitbitClockFacePairPage
    ],
})
export class OnboardPage implements OnInit {
    pages: Array<Step>;

    constructor(
        private participantService: ParticipantService,
        private router: Router,
        private featureFlagService: FeatureFlagService
    ) { }

    // ngOnInit() {
        // this.pages = [];
        // this.featureFlagService.getFeatureFlags()
        //     .then((featureFlags) => {
        //         console.log('src', 'pages', 'onboard', 'onboard.page.ts', 'ngOnInit', 'featureFlags', featureFlags);
        //         return this.participantService.getProfile();
        //     })
        //     .then((profile) => {
        //         console.log('src', 'pages', 'onboard', 'onboard.page.ts', 'ngOnInit', 'profile', profile);
        //         Promise.all([
        //             this.featureFlagService.hasFlag("weekly_reflection"),
        //             this.featureFlagService.hasFlag("bout_planning"),
        //             this.featureFlagService.hasFlag("walking_suggestion"),
        //             this.featureFlagService.hasFlag("places"),
        //             this.featureFlagService.hasFlag("fitbit_clock_face")
        //         ]).then((results) => {
        //             console.log('src', 'pages', 'onboard', 'onboard.page.ts', 'ngOnInit', 'results', results);
        //             if (!profile.contactInformation) {
        //                 this.pages.push(onboardingPageRecord['contact-information']);
        //             }
        //             if (!profile.notificationsEnabled) {
        //                 this.pages.push(onboardingPageRecord['notifications-enabled']);
        //             }
        //             if (results[0] && !profile.weeklyReflectionTime) {
        //                 this.pages.push(onboardingPageRecord['weekly-reflection-time']);
        //             }
        //             if (results[1] && !profile.firstBoutPlanningTime) {
        //                 this.pages.push(onboardingPageRecord['first-bout-planning-time']);
        //             }
        //             if (results[2] && !profile.walkingSuggestionTimes) {
        //                 this.pages.push(onboardingPageRecord['walking-suggestion-times']);
        //             }
        //             if (results[3] && !profile.places) {
        //                 this.pages.push(onboardingPageRecord['places']);
        //             }
        //             if (!profile.fitbitAuthorization) {
        //                 this.pages.push(onboardingPageRecord['fitbit-authorization']);
        //             }
        //             if (results[4] && !profile.fitbitClockFace) {
        //                 this.pages.push(onboardingPageRecord['fitbit-clock-face']);
        //             }
        //             console.log('src', 'pages', 'onboard', 'onboard.page.ts', 'ngOnInit', 'pages', this.pages);
        //         });
        //     });
    // }
    ngOnInit() {
        this.participantService.getProfile()
        .then((profile) => {
            this.pages = [];
            this.featureFlagService.getFeatureFlags()
            .then(() => {
                Promise.all([
                    this.featureFlagService.hasFlag("weekly_reflection"),
                    this.featureFlagService.hasFlag("bout_planning"),
                    this.featureFlagService.hasFlag("walking_suggestion"),
                    this.featureFlagService.hasFlag("places"),
                    this.featureFlagService.hasFlag("fitbit_clock_face")
                ]).then((results) => {
                    if (!profile.contactInformation) {
                        this.pages.push(onboardingPageRecord['contact-information']);
                    }
                    if (!profile.notificationsEnabled) {
                        this.pages.push(onboardingPageRecord['notifications-enabled']);
                    }
                    if (results[0] && !profile.weeklyReflectionTime) {
                        this.pages.push(onboardingPageRecord['weekly-reflection-time']);
                    }
                    if (results[1] && !profile.firstBoutPlanningTime) {
                        this.pages.push(onboardingPageRecord['first-bout-planning-time']);
                    }
                    if (results[2] && !profile.walkingSuggestionTimes) {
                        this.pages.push(onboardingPageRecord['walking-suggestion-times']);
                    }
                    if (results[3] && !profile.places) {
                        this.pages.push(onboardingPageRecord['places']);
                    }
                    if (!profile.fitbitAuthorization) {
                        this.pages.push(onboardingPageRecord['fitbit-authorization']);
                    }
                    if (results[4] && !profile.fitbitClockFace) {
                        this.pages.push(onboardingPageRecord['fitbit-clock-face']);
                    }
                    console.log('src', 'pages', 'onboard', 'onboard.page.ts', 'ngOnInit', 'pages', this.pages);
                });
            });
        });
    }


    public finish() {
        console.log("Onboarding finished!");
        this.participantService
            .markOnboardComplete()
            .then(() => {
                return this.participantService.markParticipantNotLoaded();
            })
            .then(() => {
                console.log("Onboarding done: Navigate to home");
                this.router.navigate(["/"]);
            });
    }
}
