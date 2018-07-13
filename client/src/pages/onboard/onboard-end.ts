import { Component} from '@angular/core';
import { ParticipantService } from '../../heartsteps/participant.service';

@Component({
    selector: 'onboard-end',
    templateUrl: 'onboard-end.html',
})
export class OnboardEndPane {
    constructor(private participant:ParticipantService) {}

    finishOnboarding() {
        this.participant.finishOnboard();
    }

}
