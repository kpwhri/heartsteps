import { Component } from "@angular/core";
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";
import { EnrollmentService } from "@heartsteps/enrollment/enrollment.service";
import { Router } from "@angular/router";
import { WeekService } from "@heartsteps/weekly-survey/week.service";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { WeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";
import { LoadingService } from "@infrastructure/loading.service";
import { AntiSedentaryService } from "@heartsteps/anti-sedentary/anti-sedentary.service";

@Component({
    templateUrl: 'settings-page.html',
})
export class SettingsPage {

    constructor(
        private walkingSuggestionService:WalkingSuggestionService,
        private enrollmentService:EnrollmentService,
        private router:Router,
        private loadingService: LoadingService,
        private alertDialog: AlertDialogController,
        private weeklySurveyService: WeeklySurveyService,
        private morningMessageService: MorningMessageService,
        private antiSedentaryService: AntiSedentaryService
    ){}

    public testWalkingSuggestion() {
        this.loadingService.show('Requesting walking suggestion message');
        this.walkingSuggestionService.createTestDecision()
        .catch(() => {
            this.alertDialog.show('Error sending test message');
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public testAntisedentaryMessage() {
        this.loadingService.show("Requesting anti-sedentary message");
        this.antiSedentaryService.sendTestMessage()
        .catch(() => {
            this.alertDialog.show('Error sending anti-sedentary message');
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public testMorningMessage() {
        this.loadingService.show("Requesting morning message");
        this.morningMessageService.requestNotification()
        .catch(() => {
            this.alertDialog.show("Error sending morning message");
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public testWeeklySurveyMessage() {
        this.loadingService.show("Requesting weekly survey");
        this.weeklySurveyService.testReflectionNotification()
        .catch(() => {
            this.alertDialog.show("Error sending weekly survey message");
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public unenroll() {
        this.enrollmentService.unenroll()
        .then(() => {
            this.router.navigate(['welcome']);
        });
    }
} 