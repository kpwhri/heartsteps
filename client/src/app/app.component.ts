import { Component } from '@angular/core';
import { ParticipantService, Participant } from '@heartsteps/participants/participant.service';
import { Router, NavigationStart, NavigationEnd } from '@angular/router';
import { AppService } from './app.service';
import { Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

@Component({
    templateUrl: 'app.html'
})
export class MyApp {

    constructor(
        platform: Platform,
        statusBar: StatusBar,
        splashScreen: SplashScreen,
        private participantService:ParticipantService,
        private appService: AppService,
        private router: Router
    ) {
        console.log('AppComponent', 'starting...')
        this.participantService.participant.subscribe((participant) => {
            console.log('AppComponent', 'got participant', participant);
            this.updateRoute(participant);
        });
        this.router.events
        .filter((event) => event instanceof NavigationEnd)
        .subscribe((event: NavigationEnd) => {
            if (event.url == "/") {
                this.participantService.update();
            }
        })
        
        platform.ready()
        .then(() => {
            return this.appService.setup()
        })
        .then(() => {
            console.log('AppComponent', 'setup');
            statusBar.styleDefault();
            splashScreen.hide();
        });
    }

    private updateRoute(participant: Participant) {
        if(this.router.url === "/") {
            if(participant && participant.isSetup && (participant.isBaselineComplete || participant.staff)) {
                this.router.navigate(['home', 'dashboard']);
            } else if (participant && participant.isSetup) {
                this.router.navigate(['baseline']);
            } else if (participant) {
                this.router.navigate(['onboard'])
            } else {
                this.router.navigate(['welcome']);
            }   
        }
    }

}
