import { Component, ViewChild } from '@angular/core';
import { Slides } from 'ionic-angular';

import { ParticipantService } from '@heartsteps/participants/participant.service';

@Component({
    selector: 'page-onboard',
    templateUrl: 'onboard.html'
})
export class OnboardPage {
    @ViewChild(Slides) slides: Slides

    constructor(
        private participantService: ParticipantService
    ) {}

    ionViewWillEnter() {
        this.slides.lockSwipes(true);
    }

    public onSaved() {
        this.next();
    }

    public next() {
        if(this.slides.isEnd()) {
            this.participantService.update();
        } else {
            this.slides.lockSwipes(false);
            this.slides.slideNext();
            this.slides.lockSwipes(true);
        }
    }

    public previous() {
        if(!this.slides.isBeginning()) {
            this.slides.slidePrev();
        }
    }

}
