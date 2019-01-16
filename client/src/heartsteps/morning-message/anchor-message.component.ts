import { Component, OnInit } from "@angular/core";
import { MorningMessageService } from "./morning-message.service";


@Component({
    selector: 'heartsteps-anchor-message',
    templateUrl: './anchor-message.component.html'
})
export class AnchorMessageComponent implements OnInit {

    private anchorMessage:string;

    constructor(
        private morningMessageService: MorningMessageService
    ) {}

    ngOnInit() {
        this.morningMessageService.get()
        .then((morningMessage) => {
            this.anchorMessage = morningMessage.anchor;
        })
        .catch(() => {
            this.anchorMessage = null;
        })
    }

}
