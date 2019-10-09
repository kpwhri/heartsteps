import { Component } from "@angular/core";
import { ParticipantService } from "@heartsteps/participants/participant.service";

@Component({
    template: ''
})
export class RootComponent {

    constructor(
        private participantService: ParticipantService
    ) {
        console.log('ROOT COMPONENT!');
        this.participantService.update();
    }
}