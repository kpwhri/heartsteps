import { Component, OnInit, ElementRef, Renderer2 } from "@angular/core";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";
import { ActivatedRoute } from "@angular/router";
import { MorningMessage } from "@heartsteps/morning-message/morning-message.model";


@Component({
    templateUrl: './morning-survey.page.html'
})
export class MorningSurveyPage implements OnInit {

    private morningMessage:MorningMessage;

    constructor(
        private activatedRoute: ActivatedRoute,
        private element:ElementRef,
        private renderer:Renderer2
    ) {}

    ngOnInit() {
        this.morningMessage = this.activatedRoute.snapshot.data['morningMessage'];

        this.renderer.addClass(this.element.nativeElement, 'start-screen');
    }

}
