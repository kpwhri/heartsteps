import { Component, OnInit, Input } from "@angular/core";
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
        if(!this.anchorMessage) {
            this.anchorMessageService.get()
            .then((message) => {
                this.anchorMessage = message;
            })
            .catch(() => {
                this.anchorMessage = undefined;
            });
        }
    }

    @Input('message')
    set setAnchorMessage(message) {
        if(message) {
            this.anchorMessage = message;
        }
    }

}
