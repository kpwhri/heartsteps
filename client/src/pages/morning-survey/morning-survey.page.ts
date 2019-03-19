import { Component, OnInit, ElementRef, Renderer2 } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { MorningMessage } from "@heartsteps/morning-message/morning-message.model";
import { StartPageComponent } from "./start.page";
import { SurveyPageComponent } from "./survey.page";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";


@Component({
    templateUrl: './morning-survey.page.html'
})
export class MorningSurveyPage implements OnInit {

    public morningMessage:MorningMessage;

    public pages:Array<any> = [{
        key: 'start',
        title: 'Good Morning',
        component: StartPageComponent
    }, {
        key: 'survey',
        title: 'Daily Survey',
        component: SurveyPageComponent
    }]

    constructor(
        private morningMessageService: MorningMessageService,
        private activatedRoute: ActivatedRoute,
        private element:ElementRef,
        private renderer:Renderer2,
        private router: Router
    ) {}

    ngOnInit() {
        this.morningMessage = this.activatedRoute.snapshot.data['morningMessage'];
        this.renderer.addClass(this.element.nativeElement, 'start-screen');
    }

    finish() {
        this.morningMessageService.complete()
        .then(() => {
            this.router.navigate(['/']);
        });
    }

}
