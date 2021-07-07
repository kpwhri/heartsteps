import { EventEmitter } from "@angular/core";
import { Component, Output } from "@angular/core";
import { FitbitClockFaceService } from "@heartsteps/fitbit-clock-face/fitbit-clock-face.service";


@Component({
    templateUrl: './fitbit-clock-face-pair.page.html'
})
export class FitbitClockFacePairPage {

    @Output() next = new EventEmitter<boolean>();

    constructor(
        private fitbitClockFaceService: FitbitClockFaceService
    ) {}

    public paired() {
        this.next.emit();
    }

    public skip() {
        this.next.emit();
    }
    
}
