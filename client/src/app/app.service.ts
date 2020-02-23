import { Injectable } from '@angular/core';
import { ParticipantService } from '@heartsteps/participants/participant.service';
import { NotificationService } from './notification.service';
import { AuthorizationService } from './authorization.service';
import { AnalyticsService } from '@infrastructure/heartsteps/analytics.service';
import { ReplaySubject } from 'rxjs';

@Injectable()
export class AppService {

    public ready: ReplaySubject<boolean> = new ReplaySubject(1);

    constructor(
        private participantService:ParticipantService,
        private notificationService: NotificationService,
        private authorizationService: AuthorizationService,
        private analyticsService: AnalyticsService
    ) {
        this.participantService.participant.subscribe((participant) => {
            console.log('AppService', 'got participant', participant);
            Promise.all([
                this.setupAuthorization(participant),
                this.setupNotifications(participant)
            ])
            .catch(() => {
                console.log('AppService', 'There was an error during participant setup');
            });
        });
    }

    public setup(): Promise<void> {
        return this.analyticsService.setup()
        .then(() => {
            return this.participantService.update();
        })
        .then(() => {
            this.ready.next(true);
            return undefined;
        });
    }

    private setupAuthorization(participant:any) {
        if(participant) {
            return this.authorizationService.setup();
        } else {
            return this.authorizationService.reset();
        }
    }

    private setupNotifications(participant:any): Promise<void> {
        if(participant) {
            return this.notificationService.setup();
        } else {
            return Promise.resolve();
        }
    }
}
