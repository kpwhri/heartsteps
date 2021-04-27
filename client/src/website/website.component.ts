import { Component, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { ParticipantService } from '@heartsteps/participants/participant.service';
import { AnalyticsService } from '@infrastructure/heartsteps/analytics.service';

@Component({
    templateUrl: './website.component.html'
})
export class HeartstepsWebsite implements OnInit {

    constructor(
        private analyticsService: AnalyticsService,
        private router: Router,
        private participantService: ParticipantService
    ) {
        this.router.events
        .filter((event) => event instanceof NavigationEnd)
        .subscribe((event: NavigationEnd) => {
            if(event.url === '/') {
                this.participantService.get()
                .then((participant) => {
                    this.updateRoute(participant);
                });
            }
        })
    }

    public ngOnInit() {
        this.analyticsService.setup();
    }

    private updateRoute(participant: any) {
        if(participant) {
            this.router.navigate(['setup']);
        } else {
            this.router.navigate(['welcome']);
        }
    }
    
}
