import { Component } from "@angular/core";
import { ParticipantService } from "@heartsteps/participants/participant.service";
import { Router } from "@angular/router";


@Component({
    templateUrl: './complete.page.html'
})
export class CompletePage {

    constructor(
        private participantService: ParticipantService,
        private router: Router
    ) {}

    public logout() {
        this.participantService.logout()
        .then(() => {
            this.router.navigate(['welcome']);
        });
    }

}
