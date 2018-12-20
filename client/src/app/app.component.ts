import { Component } from '@angular/core';
import { Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { ParticipantService } from '@heartsteps/participants/participant.service';
import { BackgroundService } from '@app/background.service';
import { Router } from '@angular/router';
import { NotificationService } from './notification.service';

@Component({
    templateUrl: 'app.html'
})
export class MyApp {
    constructor(
        platform: Platform,
        statusBar: StatusBar,
        splashScreen: SplashScreen,
        private router: Router,
        private participant:ParticipantService,
        private backgroundService: BackgroundService,
        private notificationService: NotificationService
    ) {
        platform.ready()
        .then(() => {
            this.participant.onChange().subscribe((participant: any) => {
                this.setupBackgroundProcess(participant);
                this.setupNotifications(participant);
            })
            return this.participant.update();
        })
        .then(() => {
            statusBar.styleDefault();
            splashScreen.hide();
        });
    }

    setupNotifications(participant:any) {
        if(participant.profileComplete) {
            this.notificationService.setup();
        }
    }

    setupBackgroundProcess(participant:any) {
        if(participant.profileComplete) {
            this.backgroundService.init();
        }
    }
}

