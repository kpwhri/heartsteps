import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";

@Component({
    templateUrl: "./start.page.html",
})
export class StartPageComponent implements OnInit {
    public message: string;
    public today: Date;

    @Output("next") next: EventEmitter<boolean> = new EventEmitter();

    constructor(private morningMessageService: MorningMessageService) {}

    ngOnInit() {
        this.morningMessageService.get().then((morningMessage) => {
            this.today = morningMessage.date;
            if (morningMessage.text) {
                this.message = morningMessage.text;
            }
        });
    }

    done() {
        this.next.emit();
    }
}
