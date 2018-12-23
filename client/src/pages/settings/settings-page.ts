import { Component } from "@angular/core";
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";
import { EnrollmentService } from "@heartsteps/enrollment/enrollment.service";
import { Router } from "@angular/router";
import { AlertController } from "ionic-angular";


@Component({
    templateUrl: 'settings-page.html',
})
export class SettingsPage {

    constructor(
        private walkingSuggestionService:WalkingSuggestionService,
        private enrollmentService:EnrollmentService,
        private router:Router,
        private alertCtrl: AlertController
    ){}

    public testWalkingSuggestion() {
        this.walkingSuggestionService.createTestDecision()
        .then(() => {
            const alert = this.alertCtrl.create({
                title: 'Walking suggestion sending',
                buttons: ['Ok']
            });
            alert.present();
        });
    }

    public testAntisedentaryMessage() {
        const alert = this.alertCtrl.create({
            title: 'Not implemented',
            buttons: ['Ok']
        });
        alert.present();
    }

    public testMoringMessage() {
        const alert = this.alertCtrl.create({
            title: 'Not implemented',
            buttons: ['Ok']
        });
        alert.present();
    }

    public unenroll() {
        this.enrollmentService.unenroll();
        this.router.navigate(['']);
    }
} 