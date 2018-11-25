import { Component } from '@angular/core';
import { Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { ParticipantService } from '@heartsteps/participants/participant.service';
import { BackgroundService } from '@app/background.service';
import { Router } from '@angular/router';

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
        private backgroundService: BackgroundService
    ) {
        platform.ready()
        .then(() => {
            this.participant.onChange().subscribe((participant: any) => {
                this.setupBackgroundProcess(participant);
                this.updateRootPage(participant);
            })
            return this.participant.update();
        })
        .then(() => {
            statusBar.styleDefault();
            splashScreen.hide();
        });
    }

    updateRootPage(participant:any) {
        // if (participant.profileComplete) {
        //     this.router.navigate(['/dashboard']);
        // } else if (participant.enrolled) {
        //     this.router.navigate(['/onboard']);
        // } else {
        //     this.router.navigate['/'];
        // }
    }

    setupBackgroundProcess(participant:any) {
        if(participant.profileComplete) {
            this.backgroundService.init();
        }
    }
}

