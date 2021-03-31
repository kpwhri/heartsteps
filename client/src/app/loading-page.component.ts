import { Component } from "@angular/core";
import { ParticipantService } from "@heartsteps/participants/participant.service";
import { Router } from "@angular/router";

@Component({
    template: '<app-page title="Loading"><p>Updating participant information</p></app-page>'
})
export class LoadingPageComponent {

    constructor(
        participantService: ParticipantService,
        router: Router
    ) {
        console.log('Loading page will update participant')
        participantService.update()
        .then(() => {
            console.log('Loading page has updated participant')
            router.navigate(['/'])
        });
    }

}