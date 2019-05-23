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
        this.weeklySurveyService.getAvailableSurvey()
        .then((survey) => {
            this.weeklySurvey = survey
        })
        .catch(() => {
            console.log('Weekly survey unavailable');
        })

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
