import { Component, OnInit } from "@angular/core";
import { AnchorMessageService } from "./anchor-message.service";

@Component({
    selector: 'heartsteps-anchor-message',
    templateUrl: './anchor-message.component.html'
})
export class AnchorMessageComponent implements OnInit {

    public anchorMessage:string;

    constructor(
        private anchorMessageService: AnchorMessageService
    ) {}

    ngOnInit() {
        this.anchorMessageService.get()
        .then((message) => {
            this.anchorMessage = message;
        })
        .catch(() => {
            this.anchorMessage = undefined;
        })
    }

}
