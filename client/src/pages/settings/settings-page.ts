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
        private weekService: WeekService,
        private weeklySurveyService: WeeklySurveyService,
        private morningMessageService: MorningMessageService,
        private antiSedentaryService: AntiSedentaryService
    ){}

    public testWalkingSuggestion() {
        this.walkingSuggestionService.createTestDecision()
        .then(() => {
            this.alertDialog.show('Walking suggestion sending');
        })
        .catch(() => {
            this.alertDialog.show('Error sending test message');
        });
    }

    public testAntisedentaryMessage() {
        this.antiSedentaryService.sendTestMessage()
        .then(() => {
            this.alertDialog.show('Anti sedentary message sending');
        })
        .catch(() => {
            this.alertDialog.show('Error sending test message');
        });
    }

    public testMorningMessage() {
        this.loadingService.show("Getting morning message");
        this.morningMessageService.requestNotification()
        .catch((error) => {
            return this.alertDialog.show(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public testWeeklySurveyMessage() {
        this.weekService.getCurrentWeek()
        .then((week:Week) => {
            this.weeklySurveyService.set(week.id);
        });
    }

    public unenroll() {
        this.enrollmentService.unenroll()
        .then(() => {
            this.router.navigate(['welcome']);
        });
    }
} 