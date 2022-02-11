import { Component } from "@angular/core";
import {
    WeeklySurveyService,
    WeeklySurvey,
} from "@heartsteps/weekly-survey/weekly-survey.service";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";
import { Router } from "@angular/router";
import { MorningMessage } from "@heartsteps/morning-message/morning-message.model";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";


@Component({
    selector: "dashboard-notifications",
    templateUrl: "./dashboard-notifications.component.html",
})
export class DashboardNotificationComponent {
    public morningMessage: MorningMessage;
    public weeklySurvey: WeeklySurvey;

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private morningMessageService: MorningMessageService,
        private featureFlagService: FeatureFlagService,
        private router: Router
    ) {
        this.weeklySurveyService
            .getAvailableSurvey()
            .then((survey) => {
                this.weeklySurvey = survey;
            })
            .catch(() => {
                this.weeklySurvey = undefined;
            });

        this.morningMessageService
            .get()
            .then((morningMessage) => {
                if (!morningMessage.isComplete()) {
                    this.morningMessage = morningMessage;
                } else {
                    this.morningMessage = undefined;
                }
            })
            .catch(() => {
                this.morningMessage = undefined;
            });
    }

    public navigateToWeeklySurvey() {
        this.router.navigate(["weekly-survey"]);
    }

    public navigateToMorningMessage() {
        this.router.navigate(["morning-survey"]);
    }

    public hasFlag(flag: string): boolean {
        return this.featureFlagService.hasFlagNP(flag);
    }
}
