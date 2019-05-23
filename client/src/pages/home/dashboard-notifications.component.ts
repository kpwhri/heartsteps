import { Component } from "@angular/core";
import { WeeklySurveyService, WeeklySurvey } from "@heartsteps/weekly-survey/weekly-survey.service";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";
import { Router } from "@angular/router";
import { MorningMessage } from "@heartsteps/morning-message/morning-message.model";


@Component({
    selector: 'dashboard-notifications',
    templateUrl: './dashboard-notifications.component.html'
})
export class DashboardNotificationComponent {

    public morningMessage: MorningMessage;
    public weeklySurvey: WeeklySurvey;

    constructor (
        private weeklySurveyService: WeeklySurveyService,
        private morningMessageService: MorningMessageService,
        private router: Router
    ) {
        this.weeklySurveyService.checkExpiration();
        this.weeklySurveyService.survey.subscribe((survey) => {
            this.weeklySurvey = survey;
        });

        this.morningMessageService.get()
        .then((morningMessage) => {
            if(!morningMessage.surveyComplete) {
                this.morningMessage = morningMessage;
            }
        })
    }

    public navigateToWeeklySurvey() {
        this.router.navigate(['weekly-survey']);
    }

    public navigateToMorningMessage() {
        this.router.navigate(['morning-survey']);
    }

}
