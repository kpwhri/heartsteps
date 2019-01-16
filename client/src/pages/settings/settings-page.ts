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
        private morningMessageService: MorningMessageService
    ){}

    public testWalkingSuggestion() {
        this.walkingSuggestionService.createTestDecision()
        .then(() => {
            this.alertDialog.show('Walking suggestion sending');
        });
    }

    public testAntisedentaryMessage() {
        this.alertDialog.show('Not implemented');
    }

    public testMorningMessage() {
        this.loadingService.show("Getting morning message");
        this.morningMessageService.load()
        .then(() => {
            this.loadingService.dismiss();
            this.router.navigate(['morning-survey']);
        });
    }

    public testWeeklySurveyMessage() {
        this.weekService.getCurrentWeek()
        .then((week:Week) => {
            this.weeklySurveyService.set(week.id);
        });
    }

    public unenroll() {
        this.enrollmentService.unenroll();
        this.router.navigate(['']);
    }
} 