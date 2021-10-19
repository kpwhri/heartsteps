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

import { Subscription } from "rxjs";
import { skip } from "rxjs/operators";
import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";

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
        NotificationsPermissionComponent,
        WeeklyReflectionTimePage,
        FirstBoutPlanningTimePage,
        WalkingSuggestionTimesComponent,
        PlacesList,
    ],
})
export class OnboardPage implements OnInit {
    pages: Array<Step>;
    private featureFlagSubscription: Subscription;

    constructor(
        private participantService: ParticipantService,
        private router: Router,
        private featureFlagService: FeatureFlagService
    ) {}

    ngOnInit() {
        // TODO: change pipe(1) to reflect new updates to currentFeatureFlags behaviorsubject

        this.featureFlagSubscription =
            this.featureFlagService.currentFeatureFlags
                .pipe(skip(1)) // BehaviorSubject class provides the default value (in this case, an empty feature flag list). This line skip the default value
                .subscribe((flags) => {
                    this.participantService.getProfile().then((profile) => {
                        this.pages = [];

                        // TODO: how can we parameterize this? or make it database-driven?
                        if (this.featureFlagService.hasFlag("bout_planning")) {
                            console.log("the user has 'bout_planning' flag.");
                            let nlm_onboarding_page = {
                                key: "firstBoutPlanningTime",
                                title: "First Bout Planning Time",
                                component: FirstBoutPlanningTimePage,
                            };
                            onboardingPages.splice(3, 0, nlm_onboarding_page);
                        } else {
                            console.log("the user doesn't have 'bout_planning' flag.");
                        }

                        if (this.featureFlagService.hasFlag("fitbit_clockface")) {
                            console.log("the user has 'fitbit_clockface' flag.");
                            let fitbit_clockface_onboarding_page = {
                                key: "fitbitClockFace",
                                title: "HeartSteps Clock Face",
                                component: FitbitClockFacePairPage,
                            };
                            onboardingPages.splice(onboardingPages.length - 1, 0, fitbit_clockface_onboarding_page);
                        } else {
                            console.log("the user doesn't have 'fitbit_clockface' flag.");
                        }

                        let skipPageIDs: Array<string> =
                            this.featureFlagService.getSubFlagsInNamespace(
                                "onboarding.skip"
                            );

                        onboardingPages.forEach((page) => {
                            if (
                                !profile[page.key] &&
                                skipPageIDs.indexOf(page.key) < 0
                            ) {
                                this.pages.push(page);
                            }
                        });
                    });
                    this.featureFlagSubscription.unsubscribe();
                });
        this.featureFlagService.refreshFeatureFlags();
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
