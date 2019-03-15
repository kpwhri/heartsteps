import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { MorningMessage } from "@heartsteps/morning-message/morning-message.model";


@Component({
    templateUrl: './start.page.html'
})
export class StartPageComponent implements OnInit {

    public message: string;

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    constructor(
        private activatedRoute: ActivatedRoute
    ){}

    ngOnInit() {
        const morningMessage: MorningMessage = this.activatedRoute.snapshot.data['morningMessage'];
        if (morningMessage.text) {
            this.message = morningMessage.text;            
        }
    }

    done() {
        this.next.emit();
    }

}
