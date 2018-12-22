import { Component } from "@angular/core";
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";


@Component({
    templateUrl: 'settings-page.html',
})
export class SettingsPage {

    constructor(
        private walkingSuggestionService:WalkingSuggestionService
    ){}

    public testWalkingSuggestion() {
        this.walkingSuggestionService.createTestDecision();
    }
} 