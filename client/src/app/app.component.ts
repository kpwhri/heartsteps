import { Component } from '@angular/core';
import { Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { ParticipantService } from '@heartsteps/participants/participant.service';
import { BackgroundService } from '@app/background.service';
import { NotificationService } from './notification.service';
import { AuthorizationService } from './authorization.service';
import { Router } from '@angular/router';
import { AnalyticsService } from '@infrastructure/heartsteps/analytics.service';

@Component({
    templateUrl: 'app.html'
})
export class MyApp {

    showDashboard: boolean = false;

    constructor(
        platform: Platform,
        statusBar: StatusBar,
        splashScreen: SplashScreen,
        private router: Router,
        private participantService:ParticipantService,
        private backgroundService: BackgroundService,
        private notificationService: NotificationService,
        private authorizationService: AuthorizationService,
        private analyticsService: AnalyticsService
    ) {
        platform.ready()
        .then(() => {
            return this.analyticsService.setup();
        })
        .then(() => {
            this.participantService.participant.subscribe((participant: any) => {
                this.setupBackgroundProcess(participant);
                this.setupNotifications(participant);
                this.setupAuthorization(participant);
                this.setDashboard(participant);
            });
            return this.participantService.update();
        })
        .then(() => {
            statusBar.styleDefault();
            splashScreen.hide();
        });
    }

    setupNotifications(participant:any) {
        if(participant && participant.profileComplete) {
            this.notificationService.setup();
        }
    }

    setupBackgroundProcess(participant:any) {
        if(participant && participant.profileComplete) {
            this.backgroundService.init();
        }
    }

    setupAuthorization(participant:any) {
        if(participant) {
            this.authorizationService.setup();
        } else {
            this.authorizationService.reset();
        }
    }

    setDashboard(participant:any) {
        if(!participant) {
            this.router.navigate(['welcome']);
        } else if (!participant.profileComplete) {
            this.router.navigate(['onboard']);
        } else {
            // this.router.navigate(['home']);
        }
    }
}

