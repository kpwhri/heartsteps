import { Component, OnInit } from "@angular/core";
import { ParticipantService } from "@heartsteps/participants/participant.service";
import { Router, ActivatedRoute } from "@angular/router";


@Component({
    templateUrl: './complete.page.html'
})
export class CompletePage implements OnInit {

    public studyContactName: string;
    public studyContactNumber: string;

    constructor(
        private participantService: ParticipantService,
        private router: Router,
        private activatedRoute: ActivatedRoute
    ) {}

    ngOnInit() {
        this.studyContactName = this.activatedRoute.snapshot.data['studyContactInformation'].name;
        this.studyContactNumber = this.activatedRoute.snapshot.data['studyContactInformation'].number;
    }

    public logout() {
        this.participantService.logout()
        .then(() => {
            this.router.navigate(['welcome']);
        });
    }

}
