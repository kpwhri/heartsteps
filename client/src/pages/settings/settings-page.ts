import { Component } from "@angular/core";
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";
import { EnrollmentService } from "@heartsteps/enrollment/enrollment.service";
import { Router } from "@angular/router";


@Component({
    templateUrl: 'settings-page.html',
})
export class SettingsPage {

    constructor(
        private walkingSuggestionService:WalkingSuggestionService,
        private enrollmentService:EnrollmentService,
        private router:Router
    ){}

    public testWalkingSuggestion() {
        this.walkingSuggestionService.createTestDecision();
    }

    public unenroll() {
        this.enrollmentService.unenroll();
        this.router.navigate(['']);
    }
} 