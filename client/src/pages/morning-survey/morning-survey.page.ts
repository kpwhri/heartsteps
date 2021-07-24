import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { MorningMessage } from "@heartsteps/morning-message/morning-message.model";
import { StartPageComponent } from "./start.page";
import { SurveyPageComponent } from "./survey.page";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";

@Component({
    templateUrl: "./morning-survey.page.html",
})
export class MorningSurveyPage {
    public morningMessage: MorningMessage;

    public pages: Array<any> = [];

    constructor(
        private morningMessageService: MorningMessageService,
        private router: Router
    ) {
        this.morningMessageService.get().then((morningMessage) => {
            this.morningMessage = morningMessage;

            if (this.morningMessage.anchor) {
                this.pages = [
                    {
                        key: "start",
                        title: "Good Morning",
                        component: StartPageComponent,
                    },
                    {
                        key: "survey",
                        title: "What's your day like today?",
                        component: SurveyPageComponent,
                    },
                ];
            } else {
                this.pages = [
                    {
                        key: "survey",
                        title: "What's your day like today?",
                        component: SurveyPageComponent,
                    },
                ];
            }
        });
    }

    finish() {
        this.morningMessageService.complete().then(() => {
            this.router.navigate(["/"]);
        });
    }
}
